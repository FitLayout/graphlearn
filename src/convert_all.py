import torch
from torch_geometric.data import Data
from client.flclient import FitLayoutClient, default_prefix_string, R, SEGM
from graph.creator import AreaGraphCreator
from graph.dataset import RemoteDataSet

# Disable IPv6 support if necessary (e.g. for the server running in docker containers)
import requests
requests.packages.urllib3.util.connection.HAS_IPV6 = False

# FitLayout client for a local development server
#repoId = "03304483-bce5-45fd-88e7-cffa6875031f" # adjust the repoId depending on your server config
#fl = FitLayoutClient("http://localhost:8080/fitlayout-web/api", repoId)

# Example of a local single-repository server (the repoId is "default")
fl = FitLayoutClient("http://manicka:8400/api", "default")

# The relations among visual areas that are included in the graphs
relations = [
    SEGM["isChildOf"],
    SEGM["isChildOf"], ## for parent
    R["rel-above"],
    R["rel-below"],
    R["rel-onLeft"],   ## TODO left-of, right-of
    R["rel-onRight"]
]

# The visual area tags that are used as classes
tags = [
    R["tag-klarna--none"],
    R["tag-klarna--cart"],
    R["tag-klarna--main_picture"],
    R["tag-klarna--name"],
    R["tag-klarna--price"],
    R["tag-klarna--add_to_cart"]
]

# Create the graph creator
gc = AreaGraphCreator(fl, relations, tags)

# Examine the dataset
dataset = RemoteDataSet(gc, limit=5)

for i, data in enumerate(dataset):
    print(i)
    torch.save(data, f"g{i}.pt")
