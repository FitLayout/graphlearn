# FitLayout - Python GNN Demo
# (c) 2026 Radek Burget <burgetr@fit.vut.cz>

# Classes for creating a PyTorch Geometric graphs from FitLayout artifacts.

import string
import sys
import torch
from flclient import FitLayoutClient, default_prefix_string, R, SEGM
from torch_geometric.data import Data

class GraphCreator:
    """ 
    A base class for creating a graph from a RDF repository. It implements the graph creation logic.
    """

    def __init__(self, client, relations, tags):
        self.client = client
        self.relations = relations
        self.tags = tags
        self.use_nesting = True
        # Maximum distance to consider a node as a neighbor for masking.
        self.mask_dist = 0

    def get_page_data(self, artifact_iri):
        """ 
        Collects the data basic about the artifact source page from the RDF repository by executing a SPARQL query.
        :param artifact_iri: IRI of the artifact
        :return: Dictionary with the collected data or None if no data was found.
        """
        query = default_prefix_string() + """
            SELECT ?title ?width ?height ?fontSize
            WHERE {
                ?art segm:hasSourcePage ?page .
                ?page box:width ?width .
                ?page box:height ?height .
                ?page box:title ?title .

                ?root box:belongsTo ?page .
                ?root box:documentOrder "0"^^xsd:int .
                ?root box:fontSize ?fontSize

                FILTER (?art = <""" + str(artifact_iri) + """>)
            }
        """
        return next(self.client.sparql(query), None)

    def relation_id(self, relation_iri):
        try:
            return self.relations.index(relation_iri)
        except ValueError:
            return -1
    
    def tag_id(self, tag_iri):
        try:
            return self.tags.index(tag_iri)
        except ValueError:
            return 0

    # Normalizes a color channel value to the range [0, 1]
    def normc(self, clr):
        if clr < 0:
            return 0
        if clr > 255:
            return 1
        return clr / 255.0

    def unmask_connected_nodes(self, index, dist, edge_index, visited, mask):
        """
        Recursively unmasks all nodes that are connected to the given node in the given distance.
        """
        if not visited[index]:
            mask[index] = True
            visited[index] = True
            if dist > 0:
                for i in range(len(edge_index[0])):
                    if edge_index[0][i] == index:
                        self.unmask_connected_nodes(edge_index[1][i], dist - 1, edge_index, visited, mask)
                    elif edge_index[1][i] == index:
                        self.unmask_connected_nodes(edge_index[0][i], dist - 1, edge_index, visited, mask)

    def create_graph_data(self, artifact_iri, cdata, edata, ndata):
        pgdata = self.get_page_data(artifact_iri)
        if pgdata is None:
            print("Failed to retrieve page data for artifact: ", artifact_iri)
            sys.exit(1)
        normw = int(pgdata["width"]) # use the full page width as 100%
        if normw == 0:
            normw = 1200
        normh = 1200 # use the estimated fold Y as 100%
        normfs = float(pgdata["fontSize"]) # use the average font size as 100%
        if normfs == 0:
            normfs = 12.0

        # Extract the node data from the RDF graph
        node_index = {}
        node_uris = []
        nodes = []
        labels = []
        mask = []
        for chunk in cdata:
            bgcolor = decode_rgb_string(chunk.get("backgroundColor", None))
            tcolor = decode_rgb_string(chunk.get("color", None))
            contentLength = int(chunk.get("contentLength", 0))
            text = chunk.get("text", "")
            letter_percentage, number_percentage, punctuation_percentage = count_letters_numbers_punctuation(text)
            data = [
                self.normc(bgcolor[0]), self.normc(bgcolor[1]), self.normc(bgcolor[2]),
                self.normc(tcolor[0]), self.normc(tcolor[1]), self.normc(tcolor[2]),
                float(chunk["x"]) / normw, float(chunk["y"]) / normh,
                #float(chunk["x"] + chunk["w"]) / normw, float(chunk["y"] + chunk["h"]) / normh,
                #float(chunk["w"]) / normw, float(chunk["h"]) / normh,
                contentLength,
                letter_percentage,
                number_percentage,
                punctuation_percentage,
                float(chunk["fontSize"]) / normfs,
                float(chunk["fontStyle"]),
                float(chunk["fontWeight"]),
                float(chunk["lineThrough"]),
                float(chunk["underline"]),
            ]
            nodes.append(data)
            node_uris.append(str(chunk["uri"]))
            node_index[str(chunk["uri"])] = len(nodes) - 1
            tag = self.tag_id(chunk.get("tag", ""))
            labels.append(tag)
            #mask.append(True if contentLength > 0 else False)
            if self.mask_dist > 0:
                mask.append(False) # the connected nodes will be unmasked later
            else:
                mask.append(True) # use all nodes

            # Dump the tag and all the data as a single CSV line
            #csv_line = ";".join(map(str, [tag] + data + ['"' + text + '"']))
            #print(csv_line)            

        # Extract the edge data from the RDF graph
        edge_index = [[], []]
        edge_props = []
        for edge in edata:
            rel = self.relation_id(edge["type"])
            if (rel != -1): # consider the given relations only
                if str(edge["c1"]) in node_index and str(edge["c2"]) in node_index:
                    c1id = node_index[str(edge["c1"])]
                    c2id = node_index[str(edge["c2"])]
                    edge_index[0].append(c1id)
                    edge_index[1].append(c2id)
                    # One-hot relation type encoding
                    rel_one_hot = [0] * len(self.relations)
                    rel_one_hot[rel] = 1
                    # Append the relation type together with its weight
                    edge_props.append(rel_one_hot + [float(edge["weight"])])
                    # Print classes of the connected nodes and the edge properties as a single CSV line
                    #csv_line = ";".join(map(str, [labels[c1id], labels[c2id]] + edge_props[-1]))
                    #print(csv_line)
                else:
                    print("Invalid edge (start or end node missing) " + str(edge["type"]), file=sys.stderr)

        # Extract area nesting
        if self.use_nesting:
            for edge in ndata:
                if str(edge["c1"]) in node_index and str(edge["c2"]) in node_index:
                    c1id = node_index[str(edge["c1"])]
                    c2id = node_index[str(edge["c2"])]
                    edge_index[0].append(c1id)
                    edge_index[1].append(c2id)
                    rel_one_hot = [0] * len(self.relations)
                    rel_one_hot[0] = 1
                    edge_props.append(rel_one_hot + [1.0])
                    edge_index[0].append(c2id)
                    edge_index[1].append(c1id)
                    rel_one_hot = [0] * len(self.relations)
                    rel_one_hot[1] = 1
                    edge_props.append(rel_one_hot + [1.0])
                    # Print classes of the connected nodes and the edge properties as a single CSV line
                    #csv_line = ";".join(map(str, [labels[c1id], labels[c2id]] + edge_props[-1]))
                    #print(csv_line)

        # Unmask all labeled nodes
        if self.mask_dist > 0:
            for i in range(len(labels)):
                if labels[i] != 0:
                    visited = [False] * len(labels)
                    self.unmask_connected_nodes(i, self.mask_dist, edge_index, visited, mask)
            print("Number of unmasked nodes:", sum(mask), " of:", len(nodes))

        # Create the graph
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        edge_index = torch.tensor(edge_index, dtype=torch.long).to(device)
        edge_props = torch.tensor(edge_props, dtype=torch.float).to(device)
        data = Data(x=torch.tensor(nodes, dtype=torch.float).to(device),
                    edge_index=edge_index, 
                    edge_attr=edge_props, 
                    y=torch.tensor(labels, dtype=torch.long).to(device),
                    train_mask=torch.tensor(mask, dtype=torch.bool).to(device),
                    # Addtitional attributes to indentify the artifact and the areas that form the graph nodes
                    artifact_iri=artifact_iri,
                    node_uris=node_uris)
        return data


class AreaGraphCreator (GraphCreator):
    """ A GraphCreator that creates Area graphs from AreaTree artifacts. """

    def __init__(self, client, relations, tags):
        super(AreaGraphCreator, self).__init__(client, relations, tags)
    
    def get_artifact_iris(self):
        """ Finds the IRIs of all the AreaTree artifacts in the RDF repository."""
        query = default_prefix_string() + """
            SELECT DISTINCT ?art
            WHERE {
                ?art rdf:type segm:AreaTree
            }
        """
        ret = []
        for row in self.client.sparql(query):
            ret.append(row["art"])
        return ret

    def get_node_data(self, artifact_iri):
        # For Area graph, every node is an area
        return self.get_area_data(artifact_iri)

    def get_artifact_graph(self, artifact_iri):
        cdata = self.get_area_data(artifact_iri)
        edata = self.get_area_relations(artifact_iri)
        ndata = self.get_area_nesting(artifact_iri) if self.use_nesting else []
        return self.create_graph_data(artifact_iri, cdata, edata, ndata)
    
    def get_area_data(self, area_tree_iri):
        """
            Extracts the leaf nodes (areas) and their data from the RDF graph
        """
        leaf_filter = ""
        if not self.use_nesting:
            leaf_filter = """
                . OPTIONAL { ?child segm:isChildOf ?c }
                FILTER (!bound(?child))
            """
        query = default_prefix_string() + """
            SELECT (?c AS ?uri) ?backgroundColor ?color ?contentLength ?documentOrder ?fontSize ?fontStyle ?fontWeight ?lineThrough ?underline ?text ?x ?y ?w ?h ?tag
            WHERE {
                ?c rdf:type segm:Area .
                ?c segm:belongsTo <""" + str(area_tree_iri) + """> .
                ?c segm:containsBox ?box
                OPTIONAL { ?c box:backgroundColor ?backgroundColor } .
                OPTIONAL { ?box box:color ?color } .
                OPTIONAL { ?box box:contentLength ?contentLength } .
                ?c box:documentOrder ?documentOrder .
                ?c box:fontSize ?fontSize .
                ?c box:fontStyle ?fontStyle .
                ?c box:fontWeight ?fontWeight .
                ?c box:lineThrough ?lineThrough .
                ?c box:underline ?underline .
                OPTIONAL { ?c segm:text ?text } .
                ?c box:bounds ?b . 

                ?b box:positionX ?x .
                ?b box:positionY ?y .
                ?b box:width ?w .
                ?b box:height ?h .

                OPTIONAL { ?c segm:hasTag ?tag }
                """ + leaf_filter + """
            }
        """
        return self.client.sparql(query)
    
    def get_area_relations(self, area_tree_iri):
        query = default_prefix_string() + """
            SELECT ?c1 ?c2 ?weight ?type
            WHERE {
                ?c1 segm:belongsTo <""" + str(area_tree_iri) + """> .
                ?c1 segm:isInRelation ?rel .
                ?rel segm:hasRelatedRect ?c2 .
                ?rel segm:support ?weight .
                ?rel segm:hasRelationType ?type
            }
        """
        return self.client.sparql(query)
        
    def get_area_nesting(self, area_tree_iri):
        query = default_prefix_string() + """
            SELECT ?c1 ?c2
            WHERE {
                ?c1 segm:belongsTo <""" + str(area_tree_iri) + """> .
                ?c1 segm:isChildOf ?c2
            }
        """
        return self.client.sparql(query)
       


class ChunkGraphCreator (GraphCreator):
    """ A GraphCreator that creates graphs from ChunkSet artifacts. """

    def __init__(self, client, relations, tags):
        super(ChunkGraphCreator, self).__init__(client, relations, tags)
    
    def get_artifact_iris(self):
        """ Finds the IRIs of all the TextChunk artifacts """
        query = default_prefix_string() + """
            SELECT DISTINCT ?art
            WHERE {
                ?art rdf:type segm:ChunkSet
            }
        """
        ret = []
        for row in self.client.sparql(query):
            ret.append(row["art"])
        return ret

    def get_node_data(self, artifact_iri):
        # For Chunk graph, every node is an text chunk
        # TODO: When nesting is used, even the areas should be considered as nodes as well
        return self.get_chunk_data(artifact_iri)

    def get_artifact_graph(self, artifact_iri):
        cdata = self.get_chunk_data(artifact_iri)
        edata = self.get_chunk_relations(artifact_iri)
        #ndata = self.get_area_nesting(artifact_iri) if self.use_nesting else []
        ndata = []  # Nesting information not available for chunks
        return self.create_graph_data(artifact_iri, cdata, edata, ndata)
    
    def get_chunk_data(self, chunk_set_iri):
        query = default_prefix_string() + """
            SELECT (?c AS ?uri) ?backgroundColor ?color ?contentLength ?documentOrder ?fontFamily ?fontSize ?fontStyle ?fontWeight ?lineThrough ?underline ?text
                ?x ?y ?w ?h ?tag
            WHERE {
                ?c rdf:type segm:TextChunk .
                ?c segm:belongsToChunkSet <""" + str(chunk_set_iri) + """> .
                ?c box:backgroundColor ?backgroundColor .
                ?c box:color ?color .
                ?c box:contentLength ?contentLength .
                ?c box:documentOrder ?documentOrder .
                ?c box:fontFamily ?fontFamily .
                ?c box:fontSize ?fontSize .
                ?c box:fontStyle ?fontStyle .
                ?c box:fontWeight ?fontWeight .
                ?c box:lineThrough ?lineThrough .
                ?c box:underline ?underline .
                ?c segm:text ?text .
                ?c box:bounds ?b . 

                ?b box:positionX ?x .
                ?b box:positionY ?y .
                ?b box:width ?w .
                ?b box:height ?h .

                OPTIONAL { ?c segm:hasTag ?tag }
            }
        """
        return self.client.sparql(query)
    
    def get_chunk_relations(self, chunk_set_iri):
        query = default_prefix_string() + """
            SELECT ?c1 ?c2 ?weight ?type
            WHERE {
                ?c1 segm:belongsToChunkSet <""" + str(chunk_set_iri) + """> .
                ?c1 segm:isInRelation ?rel .
                ?rel segm:hasRelatedRect ?c2 .
                ?rel segm:support ?weight .
                ?rel segm:hasRelationType ?type
            }
        """
        return self.client.sparql(query)



def decode_rgb_string(rgb_string):
    """ Decodes a string of the form "#rrggbb" into an RGB tuple """
    if rgb_string is None or len(rgb_string) < 7:
        return (-1, -1, -1) # used for transparent/unknown color
    else:
        return (int(rgb_string[1:3], 16), int(rgb_string[3:5], 16), int(rgb_string[5:7], 16))

def count_letters_numbers_punctuation(text):
    if len(text) == 0:
        return (0, 0, 0)
    else:
        letters = 0
        numbers = 0
        punctuation = 0
        for char in text:
            if char.isalpha():
                letters += 1
            elif char.isdigit():
                numbers += 1
            elif char in string.punctuation:
                punctuation += 1
        letter_percentage = letters / len(text)
        number_percentage = numbers / len(text)
        punctuation_percentage = punctuation / len(text)
        return (letter_percentage, number_percentage, punctuation_percentage)
