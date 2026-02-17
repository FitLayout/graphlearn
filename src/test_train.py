# FitLayout - Python GNN Demo
# (c) 2026 Radek Burget <burgetr@fit.vut.cz>

# This script trains a Graph Convolutional Network (GCN) on a dataset of AreaTree objects.
# The resulting model is saved in the 'models' directory.

import os
import torch
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from torch.utils.data import random_split
from flclient.flclient import default_prefix_string, R, SEGM
from graph.creator import AreaGraphCreator
from graph.dataset import RemoteDataset, LocalDataset

from train import Train
from models import GCNC
from config import fl, tags, relations, params

# Create the graph creator
gc = AreaGraphCreator(fl, relations, tags)

# Examine the dataset
#dataset = RemoteDataset(gc, limit=100) # Using the remote dataset directly
dataset = LocalDataset('data/graphs') # Using the locally saved graphs created using convert_all.py
print("# of classes: ", dataset.num_classes)
print("# of features: ", dataset.num_features)
print("# of node features: ", dataset.num_node_features)
print("# of edge features: ", dataset.num_edge_features)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = GCNC(dataset.num_node_features, dataset.num_classes).to(device)

# Split the dataset to train and validation
torch.manual_seed(42) # Use a fixed seed for reproducibility of the split
train_size = int(0.7 * len(dataset))
val_size = int(0.15 * len(dataset))
test_size = len(dataset) - train_size - val_size
train_dataset, val_dataset, test_dataset = random_split(dataset, [train_size, val_size, test_size])

val_dataloader = DataLoader(val_dataset, batch_size=1, shuffle=False)
test_dataloader = DataLoader(test_dataset, batch_size=1, shuffle=False)
train_dataloader = DataLoader(train_dataset, batch_size=params["batch_size"], shuffle=params["shuffle"])

# Train the model
train = Train(model, train_dataloader, val_dataloader, params)
train.train_loop()

# Save the trained model
if not os.path.exists("models"):
    os.makedirs("models")
torch.save(model.state_dict(), "models/last.pt")

print("Model saved to models/last.pt")
