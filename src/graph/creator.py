from client.flclient import FitLayoutClient, default_prefix_string, R, SEGM

class GraphCreator:
    """ Creates a graph from a RDF repository """

    def __init__(self, client):
        self.client = client
    
    def get_artifact_graph(self, artifact_iri):
        pgdata = self.get_chunk_set_data(artifact_iri)
        normw = int(pgdata["width"]) # use the full page width as 100%
        normh = 1200 # use the estimated fold Y as 100%
        normfs = float(pgdata["fontSize"]) # use the average font size as 100%

        cdata = self.get_chunk_data(artifact_iri)
        node_index = {}
        nodes = []
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

        edata = self.get_chunk_relations(artifact_iri)
        edges = []
        for edge in edata:
            if str(edge["c1"]) in node_index and str(edge["c2"]) in node_index:
                c1id = node_index[str(edge["c1"])]
                c2id = node_index[str(edge["c2"])]
                # TODO weights
                data = [c1id, c2id, float(edge["weight"])]
                edges.append(data)

        return (nodes, edges)
    
    def get_chunk_data(self, chunk_set_iri):
        query = default_prefix_string() + """
            SELECT (?c AS ?uri) ?backgroundColor ?color ?contentLength ?documentOrder ?fontFamily ?fontSize ?fontStyle ?fontWeight ?lineThrough ?underline ?text
                ?x ?y ?w ?h
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
                ?b box:height ?h
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


def decode_rgb_string(rgb_string):
    """ Decodes a string of the form "#rrggbb" into an RGB tuple """
    return (int(rgb_string[1:3], 16), int(rgb_string[3:5], 16), int(rgb_string[5:7], 16))
