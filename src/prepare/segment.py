from flclient import FitLayoutCLI, BOX
from config import fl

# This example demonstrates how to perform a basic segmentation on all pages in the repository.
# For each page, an AreaTree will be created and the page will be segmented into visible areas.
print("Connecting to FitLayout server on", fl.api_root, "repository", fl.repository_id)
cli = FitLayoutCLI(fl.api_root, fl.repository_id)

# Get all pages in the repository
page_uris = cli.get_artifacts(BOX.Page)
tree_uris = []

# Perform segmentation on each page
total = len(page_uris)
i = 0
for page_uri in page_uris:
    print(f"Segmenting page {i} of {total}: {page_uri}")
    r = cli.segment(page_uri)
    print(f"Result: {r}")
    if (r['status'] == "ok"):
        tree_uris.append(r['result'])
    i += 1
print("Segmentation completed")

# Compute the spatial relationships between areas and add the full text content to all the areas in the AreaTrees
total = len(tree_uris)
i = 0
for tree_uri in tree_uris:
    print(f"Computing spatial relationships for tree {i} of {total}: {tree_uri}")
    r = cli.fl.invoke_artifact_service('FitLayout.AreaConnections', tree_uri, {"minRelationWeight": 0.1, "method": "visibility" , "maxDistance": 500, "k": 5, "leafOnly": False})
    print(f"Result: {r}")
    print(f"Adding text content to tree: {tree_uri}")
    r = cli.fl.invoke_artifact_service('FitLayout.CompleteText', tree_uri, {"leavesOnly": False, "separator": " "})
    print(f"Result: {r}")
    i += 1
