from flclient import default_prefix_string, R, SEGM
from config import fl

# Delete all AreaTree artifacts from the repository so that they can be recreated using the segment.py script.

# The SPARQL query to retrieve all AreaTree artiacts from the server
query = default_prefix_string() + """
    SELECT DISTINCT ?art
    WHERE {
        ?art rdf:type segm:AreaTree
    }
"""

# Execute the SPARQL query and delete the area trees
ret = []
for row in fl.sparql(query):
    iri = row["art"]
    print("Deleting artifact: " + str(iri))
    fl.delete_artifact(iri)
