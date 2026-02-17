# FitLayout - Python GNN Demo
# (c) 2026 Radek Burget <burgetr@fit.vut.cz>

# This script queries the FitLayout server and retrieves the textual content of the tagged visual areas along with their tags
# and support information. The tags can be assigned using the prepare/tagging.py script.

from flclient import default_prefix_string
from config import fl

query = default_prefix_string() + """
    SELECT ?a ?text ?tag ?support ?ts
    WHERE {
        ?a segm:text ?text .
        ?a segm:tagSupport ?ts .
        ?ts segm:hasTag ?tag .
        ?ts segm:support ?support
    }
"""

# Print the result
for row in fl.sparql(query):
    print(f"{row['text']} : {row['tag']} ({row['support']}) [{row['ts']}]")
