from client.flclient import FitLayoutClient

# Shared FitLayout server configuration
# These are placeholders and should be replaced with your actual server configuration

# Disable IPv6 support if necessary (e.g. for the server running in docker containers)
import requests
requests.packages.urllib3.util.connection.HAS_IPV6 = False

# A local server created using docker-images/fitlayout-local as described in the README.
# Replace localhost with your server's hostname or IP address if the server is running
# on a different host.
fl = FitLayoutClient("http://localhost:9000/api", "default")

# Example of a local development server containing multiple repositories
#repoId = "03304483-bce5-45fd-88e7-cffa6875031f" # adjust the repoId depending on your server config
#fl = FitLayoutClient("http://localhost:8080/fitlayout-web/api", repoId)

# Example of a remote single-repository server (the repoId is "default"). The server can
# be created using docker-images/fitlayout-server together with the config file
# provided in server/config/config.properties.
#fl = FitLayoutClient("http://demoserver:8400/api", "default")
