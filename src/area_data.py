import torch
from torch_geometric.data import Data
from client.flclient import default_prefix_string, R, SEGM
from graph.creator import AreaGraphCreator
from graph.dataset import RemoteDataSet

from config import fl

# The relations among visual areas that are included in the graphs
# Here, we don't consider any relations because we just examine
# the individual areas.
relations = []

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

iris = gc.get_artifact_iris();
print("The repository contains ", len(iris), " usable artifacts");
if len(iris) < 1:
    exit(1)

artIri = iris[0]
print("Using the first one: ")
print(artIri)

adata = gc.get_area_data(artIri)
for area in adata:
    print(area)
