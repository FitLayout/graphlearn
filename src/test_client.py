# FitLayout - Python GNN Demo
# (c) 2026 Radek Burget <burgetr@fit.vut.cz>

# This script justs tests whether the dataset can be loaded successfully and prints some basic information about it.

from graph.creator import AreaGraphCreator
from graph.dataset import RemoteDataset, LocalDataset

from config import fl, tags, relations

# Create the graph creator
gc = AreaGraphCreator(fl, relations, tags)

# Examine the dataset
dataset = RemoteDataset(gc, limit=5)
print("# of classes: ", dataset.num_classes)
print("# of features: ", dataset.num_features)
print("# of node features: ", dataset.num_node_features)
print("# of edge features: ", dataset.num_edge_features)

data = dataset[0]
print("Node features:", data.x)
print("Edge indices:", data.edge_index)
print("Edge properties:", data.edge_attr)
print("Training mask:", data.train_mask)
print("Node labels:", data.y)

# Dump the dataset to a CSV file
# Mark the stat of each item (train, val, test)
for i, item in enumerate(dataset):
    print(f"Item {i+1}:")
    for key, value in item.__dict__.items():
        print(f"{key}: {value}")
    break
