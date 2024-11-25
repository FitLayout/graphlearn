from client.flclient import default_prefix_string, R, SEGM
from config import fl

# Gets a single artifact (AreaTree) from the server and exports its area
# data to a CSV file.

artUri = R["art23946"]  # Replace with the URI of the artifact you want to export

# The properties to get from the AreaTree to export
properties = ["uri", "backgroundColor", "color", "contentLength", "documentOrder", "fontSize", "fontStyle", "fontWeight", "lineThrough", "underline", "text", "x", "y", "w", "h", "tag"]

# Create the SELECT query property listing
select_properties = " ".join(["?" + prop for prop in properties])

# The SPARQL query to retrieve all text chunks (artiacts) from the server
query = default_prefix_string() + """
    SELECT """ + select_properties + """
    WHERE {
        ?uri rdf:type segm:Area .
        ?uri segm:belongsTo <""" + str(artUri) + """> .
        ?uri segm:containsBox ?box
        OPTIONAL { ?uri box:backgroundColor ?backgroundColor } .
        OPTIONAL { ?box box:color ?color } .
        OPTIONAL { ?box box:contentLength ?contentLength } .
        ?uri box:documentOrder ?documentOrder .
        ?uri box:fontSize ?fontSize .
        ?uri box:fontStyle ?fontStyle .
        ?uri box:fontWeight ?fontWeight .
        ?uri box:lineThrough ?lineThrough .
        ?uri box:underline ?underline .
        OPTIONAL { ?uri segm:text ?text } .
        ?uri box:bounds ?b . 

        ?b box:positionX ?x .
        ?b box:positionY ?y .
        ?b box:width ?w .
        ?b box:height ?h .

        OPTIONAL { ?uri segm:hasTag ?tag }
    }
"""

# Print the CSV header
print(",".join(properties))

# Execute the SPARQL query and print the results in CSV format. Replace missing values (of optional tags) with "None".
for row in fl.sparql(query):
    print(",".join(["\"" + str(row.get(prop, "None")) + "\"" for prop in properties]))
