# FitLayout local server with a web GUI

This folder contains an example of a script for running a local instance of the 
FitLayoutWeb server together with the PageView web interface. See the
[docker-images/fitlayout-local](https://github.com/FitLayout/docker-images/tree/main/fitlayout-local) repository
for current version of the script and more information.

## Usage

Set the FL_STORAGE variable to the storage path to be used, e.g.

```bash
export FL_STORAGE="/opt/fitlayout/storage-demo"
```

Then, start the server by running the script:

```bash
./flbrowser.sh
```

(alternatively, the storage path may be provided as the first argument of the script)

Finally, open your web browser and point it to `http://localhost:9000`.

You may want to edit the `flbrowser.sh` script to change the default parametres such as the
default port.

## Requirements

The script requires Docker to be installed on the system.
