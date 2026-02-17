# FitLayout - Python GNN Demo
# (c) 2026 Radek Burget <burgetr@fit.vut.cz>

# A sample implementation of Graph Convolutional Network (GCN) using PyTorch Geometric library.

import torch
import torch.nn.functional as func
from torch.nn import Linear
from torch_geometric.nn import GCNConv

class GCNC(torch.nn.Module):
    """
    A sample implementation of Graph Convolutional Network (GCN).
    """

    def __init__(self, num_features, num_classes):
        """
        Init model.

        :param num_features: Number of input features for a node
        :param num_classes: Number of output labels
        """
        super().__init__()
        torch.manual_seed(25)
        self.dropout_rate = 0.0 # dropout rate
        self.nlayers = 4 # number of layers
        self.hidden_channels = 128 # number of hidden channels
        self.em_size = 10 # embedding size
        if self.nlayers <= 2:
            self.em_size = self.hidden_channels
        # convolutional layers
        self.layers = []
        # input layer
        self.conv1 = GCNConv(num_features, self.hidden_channels)
        # hidden layers
        for i in range(1, self.nlayers - 1):
            if i == self.nlayers - 2: # output layer
                self.layers.append(GCNConv(self.hidden_channels, self.em_size))
            else: # hidden layer
                self.layers.append(GCNConv(self.hidden_channels, self.hidden_channels))
        self.layers = torch.nn.ModuleList(self.layers)

        # classifier
        self.classifier = Linear(self.em_size, num_classes)

    def forward(self, x, edge_index):
        """
        Perform forward pass.

        :param x: Input features
        :param edge_index: Edge index
        :return: output of NN, final embeddings
        """
        # input layer
        x = func.dropout(x, p=self.dropout_rate, training=self.training)
        x = self.conv1(x, edge_index)
        x = x.relu()
        x = func.dropout(x, p=self.dropout_rate, training=self.training)
        # hidden layers
        for layer in self.layers:
            x = layer(x, edge_index)
            x = x.relu()
            x = func.dropout(x, p=self.dropout_rate, training=self.training)
        # output layer
        x = self.classifier(x)

        return x
