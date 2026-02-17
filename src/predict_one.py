import torch
from torch_geometric.data import Data
from flclient.flclient import default_prefix_string, R, SEGM
from graph.creator import AreaGraphCreator
from graph.dataset import LocalDataset

from models import GCNC, GAT, MLP
from models_simple import GCN, sMLP
from config import fl, tags, relations, params

# --- Configuration ---
# Index of the graph to classify from the dataset
GRAPH_INDEX = 0
# -------------------

# Create the graph creator
gc = AreaGraphCreator(fl, relations, tags)

# Load the dataset
dataset = LocalDataset('data/tmp')
print(f"Loaded dataset with {len(dataset)} graphs.")

if GRAPH_INDEX >= len(dataset):
    print(f"Error: GRAPH_INDEX ({GRAPH_INDEX}) is out of bounds for dataset with size {len(dataset)}.")
    exit(1)

# Select the graph to classify
data = dataset[GRAPH_INDEX]
print(f"Classifying graph {GRAPH_INDEX} for artifact: {data.artifact_iri}")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Initialize the model architecture
# Ensure this matches the architecture of the saved model
model = GCNC(dataset.num_node_features, dataset.num_classes, params).to(device)
#model = GAT(dataset.num_node_features, dataset.num_classes, hyper).to(device)
#model = MLP(dataset.num_node_features, dataset.num_classes, hyper).to(device)
#model = GCN(dataset.num_node_features, dataset.num_classes, hyper).to(device)
#model = sMLP(dataset.num_node_features, dataset.num_classes, hyper).to(device)

# Load the trained model state
model.load_state_dict(torch.load("models/last.pt"))
print("Loaded model from models/last.pt")

# Move data to the device
data = data.to(device)

# Use the model to predict on the single graph
model.eval()
with torch.no_grad():
    if hasattr(model, 'is_graph_nn') and model.is_graph_nn():
        out = model(data.x, data.edge_index)
    else:
        out = model(data.x)
    
    # Apply softmax to get probabilities
    probabilities = torch.nn.functional.softmax(out, dim=1)
    # Get the predicted class index and the corresponding probability
    pred_probs, pred_indices = torch.max(probabilities, dim=1)


# Print the URI and predicted class for each node
print("\n--- Classification Results ---")
node_uris = data.node_uris
for i in range(len(node_uris)):
    predicted_class = tags[pred_indices[i]]
    probability = pred_probs[i].item()
    print(f"Node URI: {node_uris[i]}")
    print(f"  -> Predicted Class: {predicted_class}, Probability: {probability:.4f}")

    # Print all class probabilities
    class_probs_str = ", ".join([f"{tags[j]}: {probabilities[i][j].item():.4f}" for j in range(len(tags))])
    print(f"     All Probabilities: {{{class_probs_str}}}")
