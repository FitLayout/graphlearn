# FitLayout - Python GNN Demo
# (c) 2026 Radek Burget <burgetr@fit.vut.cz>

# Queries the FitLayout server and retrieves the list of the AreaTree artiacts.
# Normally, the AreaTrees are created using prepare/segment.py script.

from flclient import default_prefix_string, R, SEGM
from config import fl

# The SPARQL query to retrieve all AreaTree artiacts from the server.
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
