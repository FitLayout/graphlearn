from flclient import FitLayoutCLI, BOX, SEGM, R
from config import fl

# This provides a simple interactive command-line interface for the FitLayout CLI
# Run with:
#   python -i -m src.prepare.cli
# in the project root directory

print("Connecting to FitLayout server on", fl.api_root, "repository", fl.repository_id)
print(" (as configured in config.py)")
cli = FitLayoutCLI(fl.api_root, fl.repository_id)
cli.ping()
print("Use `cli` to interact with FitLayout.")
print("Available methods:", end=" ")
for method in dir(cli):
    if (not method.startswith("_")) and callable(getattr(cli, method)):
        print(method, end=" ")
print()
print("E.g. cli.list_artifacts()")
print()
