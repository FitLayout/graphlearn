import sys
import torch
from client.flclient import FitLayoutClient, default_prefix_string, R, SEGM
from torch_geometric.data import Data

class GraphCreator:
    """ A base class for creating a graph from a RDF repository """

    def __init__(self, client, relations, tags):
        self.client = client
        self.relations = relations
        self.tags = tags

    def get_page_data(self, artifact_iri):
        """ Collects the data about the artifact source page from the RDF repository """
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
            return -1


class AreaGraphCreator (GraphCreator):
    """ Creates a graph of areas from a RDF repository """

    def __init__(self, client, relations, tags):
        super(AreaGraphCreator, self).__init__(client, relations, tags)
    
    def get_artifact_graph(self, artifact_iri):
        pgdata = self.get_page_data(artifact_iri)
        normw = int(pgdata["width"]) # use the full page width as 100%
        normh = 1200 # use the estimated fold Y as 100%
        normfs = float(pgdata["fontSize"]) # use the average font size as 100%

        # Extract the node data from the RDF graph
        cdata = self.get_area_data(artifact_iri)
        node_index = {}
        nodes = []
        labels = []
        for chunk in cdata:
            bgcolor = decode_rgb_string(chunk.get("backgroundColor", None))
            tcolor = decode_rgb_string(chunk.get("color", None))
            data = [
                bgcolor[0], bgcolor[1], bgcolor[2],
                tcolor[0], tcolor[1], tcolor[2],
                float(chunk["x"]) / normw, float(chunk["y"]) / normh,
                float(chunk["x"] + chunk["w"]) / normw, float(chunk["y"] + chunk["h"]) / normh,
                float(chunk["w"]) / normw, float(chunk["h"]) / normh,
                int(chunk.get("contentLength", 0)),
                float(chunk["fontSize"]),
                float(chunk["fontStyle"]) / normfs,
                float(chunk["fontWeight"]),
                float(chunk["lineThrough"]),
                float(chunk["underline"]),
            ]
            nodes.append(data)
            node_index[str(chunk["uri"])] = len(nodes) - 1
            tag = self.tag_id(chunk.get("tag", ""))
            labels.append(tag)

        # Extract the edge data from the RDF graph
        edge_index = [[], []]
        edge_props = []
        edata = self.get_area_relations(artifact_iri)
        for edge in edata:
            rel = self.relation_id(edge["type"])
            if str(edge["c1"]) in node_index and str(edge["c2"]) in node_index and rel != -1:
                c1id = node_index[str(edge["c1"])]
                c2id = node_index[str(edge["c2"])]
                edge_index[0].append(c1id)
                edge_index[1].append(c2id)
                edge_props.append([
                    float(edge["weight"]),
                    rel
                ])
            else:
                print("Invalid edge " + str(edge["type"]), file=sys.stderr)

        # Extract area nesting
        ndata = self.get_area_nesting(artifact_iri)
        for edge in ndata:
            if str(edge["c1"]) in node_index and str(edge["c2"]) in node_index:
                c1id = node_index[str(edge["c1"])]
                c2id = node_index[str(edge["c2"])]
                edge_index[0].append(c1id)
                edge_index[1].append(c2id)
                edge_props.append([1.0, 0])
                edge_index[0].append(c2id)
                edge_index[1].append(c1id)
                edge_props.append([1.0, 1])

        # Create the graph
        edge_index = torch.tensor(edge_index, dtype=torch.long)
        edge_props = torch.tensor(edge_props, dtype=torch.float)
        data = Data(x=torch.tensor(nodes, dtype=torch.float), edge_index=edge_index, edge_attr=edge_props, y=torch.tensor(labels, dtype=torch.long))
        return data

    def get_area_data(self, area_tree_iri):
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
            SELECT ?c1 ?c2 ?weight ?type
            WHERE {
                ?c1 segm:belongsTo <""" + str(area_tree_iri) + """> .
                ?c1 segm:isChildOf ?c2
            }
        """
        return self.client.sparql(query)
        


class ChunkGraphCreator (GraphCreator):
    """ Creates a graph of text chunks from a RDF repository """

    def __init__(self, client, relations, tags):
        super(ChunkGraphCreator, self).__init__(client, relations, tags)
    
    def get_artifact_graph(self, artifact_iri):
        pgdata = self.get_page_data(artifact_iri)
        normw = int(pgdata["width"]) # use the full page width as 100%
        normh = 1200 # use the estimated fold Y as 100%
        normfs = float(pgdata["fontSize"]) # use the average font size as 100%

        # Extract the node data from the RDF graph
        cdata = self.get_chunk_data(artifact_iri)
        node_index = {}
        nodes = []
        labels = []
        for chunk in cdata:
            bgcolor = decode_rgb_string(chunk["backgroundColor"])
            tcolor = decode_rgb_string(chunk["color"])
            data = [
                bgcolor[0], bgcolor[1], bgcolor[2],
                tcolor[0], tcolor[1], tcolor[2],
                float(chunk["x"]) / normw, float(chunk["y"]) / normh,
                float(chunk["x"] + chunk["w"]) / normw, float(chunk["y"] + chunk["h"]) / normh,
                float(chunk["w"]) / normw, float(chunk["h"]) / normh,
                int(chunk["contentLength"]),
                float(chunk["fontSize"]),
                float(chunk["fontStyle"]) / normfs,
                float(chunk["fontWeight"]),
                float(chunk["lineThrough"]),
                float(chunk["underline"]),
            ]
            nodes.append(data)
            node_index[str(chunk["uri"])] = len(nodes) - 1
            tag = self.tag_id(chunk.get("tag", ""))
            labels.append(tag)

        # Extract the edge data from the RDF graph
        edata = self.get_chunk_relations(artifact_iri)
        edge_index = [[], []]
        edge_props = []
        for edge in edata:
            rel = self.relation_id(edge["type"])
            if str(edge["c1"]) in node_index and str(edge["c2"]) in node_index and rel != -1:
                c1id = node_index[str(edge["c1"])]
                c2id = node_index[str(edge["c2"])]
                edge_index[0].append(c1id)
                edge_index[1].append(c2id)
                edge_props.append([
                    float(edge["weight"]),
                    rel
                ])
            else:
                print("Invalid edge " + str(edge["type"]), file=sys.stderr)

        # Create the graph
        edge_index = torch.tensor(edge_index, dtype=torch.long)
        edge_props = torch.tensor(edge_props, dtype=torch.float)
        data = Data(x=torch.tensor(nodes, dtype=torch.float), edge_index=edge_index, edge_attr=edge_props, y=torch.tensor(labels, dtype=torch.long))
        return data
    
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
