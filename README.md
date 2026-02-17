FitLayout - GNN Integration Demo
================================

(c) 2026 Radek Burget (burgetr@fit.vut.cz)

A demo repository that demonstrates the integration of FitLayout as a data source for PyTorch Geometric ML applications.
It implements the dataset preparation and the training of a GCNC network on this data set. The dataset contains pages from
the imaginary bookstore available at https://books.toscrape.com/.

# Installation

All the scripts assume a FitLayout server running. See the [server](./server) folder for sample server configuration that is started
as a docker container. The server hostname should be configured in [src/config.py](src/config.py).

The scripts also require the dependencies listed in [requiremens.txt](./requirements.txt) that can be installed in the
usual way using `pip`. The communication with the FitLayout server is implenented using the [FitLayout Python Client](https://github.com/FitLayout/fitlayout-python-client) library.

# Dataset preparation

The dataset preparation including the page rendering and annotation is driven by scripts in the [src/prepare](src/prepare) folder. See the separate [README](src/prepare/README.md) for more information.

The [src/list_artifacts.py](src/list_artifacts.py) and [src/list_tags.py](src/list_tags.py) scripts can be used for reviewing the repository contents.

# Integration with PyTorch Geometric

The integration with PyG is implemented as two sample components:

- GraphCreator ([src/graph/creator.py](src/graph/creator.py)) that uses the FitLayout client to get the artifact data from the repository using SPARQL queries and creates a [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/en/latest/) graph from each artifact.
- RemoteDataSet ([src/graph/dataset.py](src/graph/dataset.py)) that implements the PyTorch Geometric [Dataset](https://pytorch-geometric.readthedocs.io/en/latest/tutorial/create_dataset.html) subclass using the GraphCreator.

Further the learning itself is implemented as the following scripts:

- [src/convert_all.py](src/convert_all.py) converts all the AreaTrees in the repository to PyG graphs using the `GraphCreator` and saves them as PyTorch files.
- [src/test_train.py](src/test_train.py) trains the GNN using the saved graphs and saves the trained network state.
- [src/test_predict.py](src/test_predict.py) tests the trained GNN using a testing dataset and evaluates the results.

# Dataset export and import

Advanced repository contents management such as export and import can be performed using the provided command line interface tool:

```bash
python -i src/prepare/cli.py
```

Then, the `cli.import()` and `cli.dump()` functions can be used the import and export.
