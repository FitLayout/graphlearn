# FitLayout - Python GNN Demo
# (c) 2026 Radek Burget <burgetr@fit.vut.cz>

# This script demonstrates how to use the FitLayout client library to create graph representations.
# It just creates graph representations for all AreaTree objects in a repository and saves them locally
# in pytorch format.

import os
import torch
from torch_geometric.data import Data
from flclient import default_prefix_string, R, SEGM
from graph.creator import AreaGraphCreator, ChunkGraphCreator
from graph.dataset import RemoteDataset

from config import fl, relations, tags

# Create the graph creator
gc = AreaGraphCreator(fl, relations, tags)

# Examine the dataset
dataset = RemoteDataset(gc, limit=None)

# Create data/graphs directory if it does not exist
if not os.path.exists("data/graphs"):
    os.makedirs("data/graphs")

for i, data in enumerate(dataset):
    print(i)
    torch.save(data, f"data/graphs/g{i}.pt")
