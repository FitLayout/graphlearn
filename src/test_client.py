import torch
from torch_geometric.data import Data
from client.flclient import FitLayoutClient, default_prefix_string, R, SEGM
from graph.creator import AreaGraphCreator
from graph.dataset import RemoteDataSet

query1 = default_prefix_string() + """
    SELECT (?c AS ?uri) ?backgroundColor ?color ?contentLength ?documentOrder ?fontFamily ?fontSize ?fontStyle ?fontWeight ?lineThrough ?underline ?text
        ?x ?y ?w ?h
    WHERE {
        ?c rdf:type segm:TextChunk .
        ?c box:backgroundColor ?backgroundColor .
        ?c box:color ?color .
        ?c box:contentLength ?contentLength .
        ?c box:documentOrder ?documentOrder .
        ?c box:fontFamily ?fontFamily .
        ?c box:fontSize ?fontSize .
        ?c box:fontStyle ?fontStyle .
        ?c box:fontWeight ?fontWeight .
        ?c box:lineThrough ?lineThrough .
        ?c box:underline ?underline .
        ?c segm:text ?text .
        ?c box:bounds ?b . 

        ?b box:positionX ?x .
        ?b box:positionY ?y .
        ?b box:width ?w .
        ?b box:height ?h
    }
"""

query2 = default_prefix_string() + """
"""

#repoId = "dd212323-311e-47d1-9823-83158d579712"
#artUri = R.art20
repoId = "2e961c23-04a5-4735-b9e9-1e1751b8037e"
artUri = R.art5

#fl = FitLayoutClient("http://localhost:8080/fitlayout-web/api", repoId)

fl = FitLayoutClient("http://manicka.fit.vutbr.cz:8400/api", "default")

#result = fl.sparql(query2)
#result = fl.artifacts(str(SEGM.ChunkSet))
#for row in result:
#    print(row)

#art = fl.get_artifact(R.art8)
#print(art)

relations = [
    SEGM["isChildOf"],
    SEGM["isChildOf"], ## for parent
    R["rel-above"],
    R["rel-below"],
    R["rel-onLeft"],   ## TODO left-of, right-of
    R["rel-onRight"]
]

tags = [
    R["tag-klarna--none"],
    R["tag-klarna--cart"],
    R["tag-klarna--main_picture"],
    R["tag-klarna--name"],
    R["tag-klarna--price"],
    R["tag-klarna--add_to_cart"]
]

gc = AreaGraphCreator(fl, relations, tags)
#print(list(gc.get_artifact_iris()))
#csdata = gc.get_chunk_data(artUri)
#csdata = gc.get_chunk_relations(artUri)
#for row in csdata:
#    print(row)

#data = gc.get_artifact_graph(artUri)
#data.validate(raise_on_error=True)
#print(data.is_directed())

#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#data = data.to(device)

dataset = RemoteDataSet(gc, limit=5)
print(dataset.num_classes)
print(dataset.num_features)
print(dataset.num_node_features)
print(dataset.num_edge_features)
#data = dataset[0]
#print(data.y)

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
