from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF
from flclient import default_prefix_string, R, SEGM
from config import fl

# Find the titles simply as all H1 elements in the repository
query = default_prefix_string() + """
    SELECT ?a ?art ?text WHERE {
        ?a segm:belongsTo ?art .
        ?a segm:containsBox ?b .
        ?b box:htmlTagName 'H1' .
        ?a segm:text ?text 
    }
"""
for row in fl.sparql(query):
    print(f"Artifact: {row['art']}, Title: {row['text']}, {row['a']}")
    fl.add_tag(URIRef(row['a']), 'book', 'title', 1.0, row['art'])

# Find the prices by the label of their parent area (<P class=price_color>)
# and the font size (to avoid other prices in the bottom of the page)
query = default_prefix_string() + """
    SELECT ?a ?art ?text WHERE {
        ?a segm:belongsTo ?art .
        ?a box:fontSize "26.0"^^xsd:float .
        ?a segm:isChildOf ?parent .
        ?parent rdfs:label '<P class=price_color>' .
        ?a segm:text ?text 
    }
"""
for row in fl.sparql(query):
    print(f"Artifact: {row['art']}, Price: {row['text']}, {row['a']}")
    fl.add_tag(URIRef(row['a']), 'book', 'price', 1.0, row['art'])
