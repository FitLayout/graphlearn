import torch
from torch_geometric.data import Data
from client.flclient import FitLayoutClient, default_prefix_string, R, SEGM
from graph.creator import AreaGraphCreator
from graph.dataset import RemoteDataSet

# Disable IPv6 support if necessary (e.g. for the server running in docker containers)
#import requests
#requests.packages.urllib3.util.connection.HAS_IPV6 = False

# FitLayout client for a local development server
repoId = "03304483-bce5-45fd-88e7-cffa6875031f" # adjust the repoId depending on your server config
fl = FitLayoutClient("http://localhost:8080/fitlayout-web/api", repoId)

# Example of a local single-repository server (the repoId is "default")
#fl = FitLayoutClient("http://my.server.com:8400/api", "default")

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
print(dataset.num_classes)
print(dataset.num_features)
print(dataset.num_node_features)
print(dataset.num_edge_features)
#data = dataset[0]
#print(data.y)

# Simple example of training a GCN model
# Taken from https://pytorch-geometric.readthedocs.io/en/latest/get_started/introduction.html
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv

class GCN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = GCNConv(dataset.num_node_features, 16)
        self.conv2 = GCNConv(16, dataset.num_classes)

    def forward(self, data):
        x, edge_index = data.x, data.edge_index

        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, training=self.training)
        x = self.conv2(x, edge_index)

        return F.log_softmax(x, dim=1)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = GCN().to(device)
data = dataset[0].to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

model.train()
for epoch in range(200):
    optimizer.zero_grad()
    out = model(data)
    loss = F.nll_loss(out[data.train_mask], data.y[data.train_mask])
    loss.backward()
    print(f'Loss: {loss.item():.4f}')
    optimizer.step()

data = dataset[0].to(device)
model.eval()
pred = model(data).argmax(dim=1)
print(data.y)
print(pred)
correct = (pred[data.train_mask] == data.y[data.train_mask]).sum()
acc = int(correct) / int(data.train_mask.sum())
print(f'Accuracy: {acc:.4f}')
