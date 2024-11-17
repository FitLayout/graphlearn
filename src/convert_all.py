import torch
from torch_geometric.data import Data
from client.flclient import default_prefix_string, R, SEGM
from graph.creator import AreaGraphCreator
from graph.dataset import RemoteDataSet

from config import fl

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
