import sys
from client.flclient import FitLayoutClient, default_prefix_string, R, SEGM

class GraphCreator:
    """ Creates a graph from a RDF repository """

    def __init__(self, client, relations, tags):
        self.client = client
        self.relations = relations
        self.tags = tags
    
    def get_artifact_graph(self, artifact_iri):
        pgdata = self.get_chunk_set_data(artifact_iri)
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
            tag = self.tag_id(chunk["tag"])
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

        return (nodes, edge_index, edge_props)
    
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

    def get_chunk_set_data(self, chunk_set_iri):
        query = default_prefix_string() + """
            SELECT ?title ?width ?height ?fontSize
            WHERE {
                ?cs segm:hasSourcePage ?page .
                ?page box:width ?width .
                ?page box:height ?height .
                ?page box:title ?title .

                ?root box:belongsTo ?page .
                ?root box:documentOrder "0"^^xsd:int .
                ?root box:fontSize ?fontSize

                FILTER (?cs = <""" + str(chunk_set_iri) + """>)
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


def decode_rgb_string(rgb_string):
    """ Decodes a string of the form "#rrggbb" into an RGB tuple """
    return (int(rgb_string[1:3], 16), int(rgb_string[3:5], 16), int(rgb_string[5:7], 16))
