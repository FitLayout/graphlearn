from flclient import FitLayoutCLI
from config import fl
import os

# This example demonstrates how to render web pages on the FitLayout server
# using the FitLayout CLI.

# Create a FitLayout CLI instance using the configured server
# The configuration is loaded from the ../config.py file
# The CLI provides the implmenetation of the most common operations with
# the pages such as renderinfg, segmentation or exporting
print("Connecting to FitLayout server on", fl.api_root, "repository", fl.repository_id)
cli = FitLayoutCLI(fl.api_root, fl.repository_id)

# Read all page URLs from data/book_urls.txt and render the pages on the FitLayout server
script_dir = os.path.dirname(os.path.abspath(__file__))
urls_file = os.path.join(script_dir, "../../data/book_urls.txt")
with open(urls_file, "r") as f:
    for url in f.readlines():
        if url.strip():  # skip empty lines
            print(f"Rendering page: {url.strip()} ", end="")
            resp = cli.render(url.strip())
            print(" done: ", resp)

print("Rendering completed")
