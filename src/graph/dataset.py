import torch
from torch_geometric.data import Dataset

class RemoteDataSet(Dataset):

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
        print("Loading sample: ", self.iris[idx])
        return self.creator.get_artifact_graph(self.iris[idx])
