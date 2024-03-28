# jack-connection-manager
a jack connection manager aimed at setups with jack clients with lots of in/outputs.

# Installation
``` bash
python -m venv venv
source venv/bin/activate
pip install .
jack-connection-manager -h
```

# Configuration
Jack connections are read from a connection file, some example connection files can be found in the `connection_files` directory.
The connection file is a yaml file containing a list of clients for which connections should be made, that follows the following format:
```yaml
# the clientname contains the whole portname with the number/specifier at the end removed
- client: clientname:portname_ 

  # the number of consecutive channels, that should be connected to connected clients
  n_channels: 8

  # the first channel that should be connected to a client
  # OPTIONAL, default value is 1
  start_index: 0 

  # list of clients to connect to
  connections:

    # keys follow the same structure as for the outer client
    # only client and start_index are supported
    - client: otherclientname:portname_
      start_index: 10
```
The connection file can contain any number of clients, clients can also be listed several times.

# Releasing

Releases are published automatically when a tag is pushed to GitHub.

``` bash

# Set next version number
export RELEASE=x.x.x

git tag -a $RELEASE -m "Version $RELEASE"

# Push
git push --tags