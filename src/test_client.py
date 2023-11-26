from client.flclient import FitLayoutClient, default_prefix_string, R, SEGM

query = default_prefix_string() + """
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

fl = FitLayoutClient("http://localhost:8080/fitlayout-web/api", "300ed999-eb63-4173-a3cc-2d95531f85f4")

result = fl.sparql(query)
#result = fl.artifacts(str(SEGM.ChunkSet))
for row in result:
    print(row)

#art = fl.get_artifact(R.art8)
#print(art)
