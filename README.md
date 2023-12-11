FitLayout - GNN Learning Algorithms
===================================

(c) 2023 Radek Burget (burgetr@fit.vut.cz)

Experimental code for the recognition of specific document parts using Graph Neural Networks.

This project demonstrates the use of FitLayout as a data source for training Graph Neural Networks in Python.
It provides a sample implementation of the following components:

- FitLayout client ([src/client/flclient.py](src/client/flclient.py)) that connects the FitLayout REST API and allows obtaining the [artifact](https://github.com/FitLayout/FitLayout/wiki/Basic-Concepts#artifacts) data and execute SPARQL queries against the [artifact repository](https://github.com/FitLayout/FitLayout/wiki/Basic-Concepts#artifact-repository).
- GraphCreator ([src/graph/creator.py](src/graph/creator.py)) that uses the FitLayout client to get the artifact data from the repository and creates a [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/en/latest/) graph from each artifact.
- RemoteDataSet ([src/graph/dataset.py](src/graph/dataset.py)) that implements the PyTorch Geometric [Dataset](https://pytorch-geometric.readthedocs.io/en/latest/tutorial/create_dataset.html) subclass using the GraphCreator.

The [creategraph.py](creategraph.py) script shows a sample usage of the implemented clases with PyTorch Geometric.


## Source FitLayout artifact repository

This code assumes an existing FitLyaout artifact repository that contains the rendered pages and derived artifacts (AreaTrees) that is accessible through the REST API provided by an instance of the [FitLayoutWeb](https://github.com/FitLayout/FitLayoutWeb) server. Sample server configuration is provided in the [server](server) folder.

