# FitLayout - Python GNN Demo
# (c) 2026 Radek Burget <burgetr@fit.vut.cz>

# Graph dataset implementations.

import os
from abc import ABC

import torch
import torch_geometric.data as data
from torch_geometric.data import Dataset, InMemoryDataset

class RemoteDataset(Dataset):
    """
    A minimalistic dataset implementation that fetches page graphs directly from a remote FitLayout remote
    server using the FitLayout client library.
    """

    def __init__(self, creator, limit=None):
        super().__init__()
        self.creator = creator
        self.iris = creator.get_artifact_iris()
        if limit is not None:
            self.iris = self.iris[:limit]
        
    def len(self):
        """
        Returns the number of samples in the dataset.

        :return: The number of samples in the dataset
        """
        return len(self.iris)
    
    def get(self, idx):
        """
        Returns the sample at the given index.

        :param idx: The index of the sample to return
        :return: The sample at the given index
        """
        #print("Loading sample: ", self.iris[idx])
        return self.creator.get_artifact_graph(self.iris[idx])


class LocalDataset(InMemoryDataset, ABC):
    """
    A custom dataset implementation that loads graphs from a local directory.
    """

    def __init__(self, dataset_path):
        """
        Creates a new LocalDataset instance.

        :param dataset_path: Input dataset path. The directory should contain *.pt files representing graphs.
        """
        super().__init__()

        cuda = torch.cuda.is_available()

        # load graphs
        self.graphs = []
        for i, graph in enumerate(os.listdir(dataset_path)):
            # Load only *.pt
            if graph.endswith(".pt"):
                if cuda:
                    g = torch.load(os.path.join(dataset_path, graph), weights_only=False)
                else:
                    g = torch.load(os.path.join(dataset_path, graph), weights_only=False, map_location='cpu')

                self.graphs.append(g)
        self.data = self.get_batch(16)

    def __len__(self):
        """
        Returns the number of samples in the dataset.

        :return: The number of samples in the dataset
        """
        return len(self.graphs)

    def __getitem__(self, item):
        """
        Loads and returns a sample from the dataset at the given index.

        :param item: Id of requested sample
        :return: Sample at the given index
        """
        return self.graphs[item]

    def get_batch(self, batch_size):
        """
        Returns batch object, representing multiple graphs as a single disconnected graph.

        :param batch_size: Batch size
        :return: batch
        """
        return data.Batch().from_data_list(self.graphs[0:batch_size])

    def get_cluster(self, n):
        """
        Returns cluster object, grouping graphs into specific number of clusters
        :param n: Number of graphs in one cluster
        :return: cluster loader
        """
        return data.ClusterLoader(data.ClusterData(self.graphs,  n))

    def get_sampler(self, item, num_neigh, batch_size, shuffle):
        """
        Returns sampler which for each convolutional layer samples a max number of nodes from each neighborhood.

        :param item: Index of graph
        :param num_neigh: List of numbers of max neighbors for each convolution layer
        :param batch_size: Number of graphs
        :param shuffle: Randomly shuffle graphs
        :return: Sampler
        """
        return data.NeighborSampler(self.graphs[item].edge_index, sizes=num_neigh, batch_size=batch_size,
                                    shuffle=shuffle)
