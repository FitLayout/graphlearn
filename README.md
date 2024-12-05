FitLayout - GNN Learning Algorithms
===================================

(c) 2024 Radek Burget (burgetr@fit.vut.cz)

Experimental code for the recognition of specific document parts using Graph Neural Networks.

This project demonstrates the use of FitLayout as a data source for training Graph Neural Networks in Python.
It provides a sample implementation of the following components:

- FitLayout client ([src/client/flclient.py](src/client/flclient.py)) that connects the FitLayout REST API and allows obtaining the [artifact](https://github.com/FitLayout/FitLayout/wiki/Basic-Concepts#artifacts) data and execute SPARQL queries against the [artifact repository](https://github.com/FitLayout/FitLayout/wiki/Basic-Concepts#artifact-repository).
- GraphCreator ([src/graph/creator.py](src/graph/creator.py)) that uses the FitLayout client to get the artifact data from the repository and creates a [PyTorch Geometric](https://pytorch-geometric.readthedocs.io/en/latest/) graph from each artifact.
- RemoteDataSet ([src/graph/dataset.py](src/graph/dataset.py)) that implements the PyTorch Geometric [Dataset](https://pytorch-geometric.readthedocs.io/en/latest/tutorial/create_dataset.html) subclass using the GraphCreator.

The [creategraph.py](creategraph.py) script shows a sample usage of the implemented clases with PyTorch Geometric.


## Preparing the Source FitLayout artifact repository

This code assumes an existing FitLyaout artifact repository that contains the rendered pages (Page artifacts) and derived AreaTree artifacts. The repository
must be accessible through the REST API provided by an instance of the FitLayoutWeb server.

### Requirements

All the script server and CLI srcipts below require Docker to be installed on the system.

### Artifact preparation

First, the `FL_STORAGE` environment variable is set to the path where the RDF artifacts will be stored, e.g.:

```bash
export FL_STORAGE="$HOME/.fitlayout/storage-demo"
```

The folder will be created automatically if it does not already exist.

The artifacts in the RDF storage may be prepared via the command-line interface (CLI) or via an interactive GUI. For using the CLI,
the [cli/fitlayout.sh](cli/fitlayout.sh) script may be used. E.g. for rendering a page and the corresponding AreaTree, the following
command may be used:

```bash
./fitlayout.sh \
    USE local \
    RENDER -b puppeteer https://cssbox.sourceforge.net \
    STORE \
    SEGMENT -m simple \
    STORE
```

See the [FitLayout Wiki](https://github.com/FitLayout/FitLayout/wiki/Command-line-Interface) for the CLI
usage instructions.

Alternatively, the GUI browser may be used for creating the artifacts interactively. See the [server/local](server/local) folder
for instructions on how to run the local server with a web GUI and open the GUI in your browser. Then use the *Render*
tab of the GUI to render the pages and subsequently *Segmentation* tab to create the AreaTree using the 
*Simple area tree construction* service.

### Running the server

The server is used as the data source for the python scripts. Again, the `FL_STORAGE` environment variable should be set 
to the path where the RDF artifacts are stored, e.g.:

```bash
export FL_STORAGE="$HOME/.fitlayout/storage-demo"
```

For acessing the repository on a local machine, the local GUI browser may be used as mentioned above.
See the [server/local](server/local) folder for instructions on how to run the local server. It is not necessary
to open the GUI in a browser since the python scripts will use the server instead.

Alternatively, a standalone server with no GUI may be used. See the [server/standalone](server/standalone) folder
for details.

The URL of the running server must be configured in the [src/config.py](src/config.py) configuration script. In both cases,
the servers can run on a local machine (use `localhost` as the hostname) or a remote server (use the hostname of
the server).

The [src/list_artifacts.py](src/list_artifacts.py) may be used for checking the connection and listing all
the AreaTree artifacts available in the repositoy.
