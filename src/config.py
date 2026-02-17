from flclient import FitLayoutClient, R, SEGM

# Shared FitLayout server configuration
# These are placeholders and should be replaced with your actual server configuration

# Disable IPv6 support if necessary (e.g. for the server running in docker containers)
import requests
requests.packages.urllib3.util.connection.HAS_IPV6 = False

# Example of a remote server with localdir storage (the repoId is the directory name). The server can
# be created using docker-images/fitlayout-server together with the config file
# provided in server/config/config.properties.
fl = FitLayoutClient("http://localhost:8400/api", "booksp")

# The relations among visual areas that are included in the graphs
relations = [
    SEGM["isChildOf"],
    SEGM["isChildOf"], ## for parent
    R["rel-above"],
    R["rel-below"],
    R["rel-leftOf"],
    R["rel-rightOf"]
]

# The visual area tags that are used as classes
tags = [
    R["tag-generic--none"],
    R["tag-book--title"],
    R["tag-book--price"],
]

# Hyperparameters for training the model
params = {
    "batch_size": 32,
    "shuffle": True,
    "learning_rate": 0.001,
    "weight_decay": 0.0,
    "eps": 1e-08,
    "epochs": 3000,
}
