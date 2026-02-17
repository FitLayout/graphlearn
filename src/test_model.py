import torch
from torch_geometric.data import Data
from flclient.flclient import default_prefix_string, R, SEGM
from graph.creator import AreaGraphCreator, ChunkGraphCreator
from graph.dataset import RemoteDataset

from models import GCNC, GAT, MLP
from config import fl, relations, tags, params

# Create the graph creator
#gc = AreaGraphCreator(fl, relations, tags)
gc = ChunkGraphCreator(fl, relations, tags)

# Examine the remote dataset using the last trained model
dataset = RemoteDataset(gc, limit=None)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
num_classes = len(tags)

model = GCNC(dataset.num_node_features, num_classes, params).to(device)
#model = GAT(dataset.num_node_features, num_classes, hyper).to(device)
#model = MLP(dataset.num_node_features, num_classes, hyper).to(device)

# Load the last trained model
model.load_state_dict(torch.load('models/last.pt', weights_only=False))

err_count = 0
for i, data in enumerate(dataset):
    print(i, data.artifact_iri)
    # Get the area data for the current artifact
    #area_data = [data for data in gc.get_area_data(data.artifact_iri)]
    area_data = [data for data in gc.get_node_data(data.artifact_iri)]
    #print("\n".join([str(data['uri']) for data in area_data]))
    model.eval()
    with torch.no_grad():
        if model.is_graph_nn():
            pred = model(data.x, data.edge_index).argmax(dim=1)
        else:
            pred = model(data.x).argmax(dim=1)
    acc = torch.sum(pred == data.y).item() / len(data.y)
    print(f"Accuracy on validation example: {acc}")
    if acc < 1:
        err_count += 1
        # Print the differences between the predicted and actual labels
        for j in range(len(data.y)):
            if pred[j]!= data.y[j]:
                # Get the area data for the current node by its URI
                node_uri = data.node_uris[j]
                node_area_data = [chunk for chunk in area_data if str(chunk["uri"]) == node_uri]
                text = node_area_data[0]['text'] if node_area_data else "???"
                print(f"Label mismatch: predicted {tags[pred[j]]}, actual {tags[data.y[j]]}, text: {text}")
