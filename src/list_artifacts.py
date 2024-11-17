from client.flclient import default_prefix_string, R, SEGM
from config import fl

# Tries to query the FitLayout server and retrieve the list of artiacts

# The SPARQL query to retrieve all text chunks (artiacts) from the server
query = default_prefix_string() + """
    SELECT DISTINCT ?art
    WHERE {
        ?art rdf:type segm:AreaTree
    }
"""

# Execute the SPARQL query and print the results
ret = []
for row in fl.sparql(query):
    print(row["art"])
