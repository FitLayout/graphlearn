# FitLayout - Python GNN Demo
# (c) 2026 Radek Burget <burgetr@fit.vut.cz>

# This script tests the trained model on a testing dataset.

import torch
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from torch.utils.data import random_split
from flclient.flclient import default_prefix_string, R, SEGM
from graph.creator import AreaGraphCreator
from graph.dataset import RemoteDataset, LocalDataset

from models import GCNC
from config import fl, tags, relations, params

# Create the graph creator
gc = AreaGraphCreator(fl, relations, tags)

# Load the dataset
dataset = LocalDataset('data/graphs')
print("# of classes: ", dataset.num_classes)
print("# of features: ", dataset.num_features)
print("# of node features: ", dataset.num_node_features)
print("# of edge features: ", dataset.num_edge_features)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

model = GCNC(dataset.num_node_features, dataset.num_classes).to(device)

# Load the trained model state
model.load_state_dict(torch.load("models/last.pt"))
print("Loaded model from models/last.pt")

# Split the dataset to get the test set
# Using the same split sizes and seed as in training to ensure consistency
torch.manual_seed(42) # Use a fixed seed for reproducibility of the split
train_size = int(0.7 * len(dataset))
val_size = int(0.15 * len(dataset))
test_size = len(dataset) - train_size - val_size
_, _, test_dataset = random_split(dataset, [train_size, val_size, test_size])

test_dataloader = DataLoader(test_dataset, batch_size=1, shuffle=False)

print_errors = True

# Use the model to predict on the entire test dataset and print the accuracy
# and the differences between predicted and actual labels
err_count = 0
total_cnt = 0
total_err = 0
for data in test_dataloader:
    data = data.to(device)
    model.eval()
    with torch.no_grad():
        pred = model(data.x, data.edge_index).argmax(dim=1)
    acc = torch.sum(pred == data.y).item() / len(data.y)
    total_cnt += len(data.y)
    total_err += torch.sum(torch.abs(pred - data.y)).item()
    if acc < 1:
        err_count += 1
        if print_errors:
            print(f"Incorrect predictions for artifact: {data.artifact_iri[0]}")
            node_uris = data.node_uris[0]
            for i in range(len(data.y)):
                if pred[i] != data.y[i]:
                    print(f"  Node URI: {node_uris[i]}, Predicted: {tags[pred[i]]}, Actual: {tags[data.y[i]]}")

print(f"Number of instances with incorrect predictions: {err_count}")
print(f"Total number of areas: {total_cnt}")
print(f"Incorrectly classified areas: {total_err}")
if total_cnt > 0:
    print(f"Accuracy: {(total_cnt - total_err) / total_cnt}")
    print(f"Error rate: {total_err / total_cnt}")
