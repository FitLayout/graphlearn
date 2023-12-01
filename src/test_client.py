import torch
from torch_geometric.data import Data
from client.flclient import FitLayoutClient, default_prefix_string, R, SEGM
from graph.creator import AreaGraphCreator

query1 = default_prefix_string() + """
    SELECT (?c AS ?uri) ?backgroundColor ?color ?contentLength ?documentOrder ?fontFamily ?fontSize ?fontStyle ?fontWeight ?lineThrough ?underline ?text
        ?x ?y ?w ?h
    WHERE {
        ?c rdf:type segm:TextChunk .
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

query2 = default_prefix_string() + """
"""

#repoId = "dd212323-311e-47d1-9823-83158d579712"
#artUri = R.art20
repoId = "2e961c23-04a5-4735-b9e9-1e1751b8037e"
artUri = R.art5

fl = FitLayoutClient("http://localhost:8080/fitlayout-web/api", repoId)

#result = fl.sparql(query2)
#result = fl.artifacts(str(SEGM.ChunkSet))
#for row in result:
#    print(row)

#art = fl.get_artifact(R.art8)
#print(art)

relations = [
    SEGM["isChildOf"],
    SEGM["isChildOf"], ## for parent
    R["rel-above"],
    R["rel-below"],
    R["rel-onLeft"],   ## TODO left-of, right-of
    R["rel-onRight"]
]

tags = [
    R["tag-klarna--cart"],
    R["tag-klarna--main_picture"],
    R["tag-klarna--name"],
    R["tag-klarna--price"],
    R["tag-klarna--add_to_cart"]
]

gc = AreaGraphCreator(fl, relations, tags)
#csdata = gc.get_chunk_data(artUri)
#csdata = gc.get_chunk_relations(artUri)
#for row in csdata:
#    print(row)

data = gc.get_artifact_graph(artUri)
#data.validate(raise_on_error=True)
print(data.is_directed())

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
data = data.to(device)
