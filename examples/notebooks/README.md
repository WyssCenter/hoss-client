## Notebook Examples

These notebooks provide some examples of how to use the Hoss client library.

To run the notebooks, you need to install jupyter, the client library, and optionally ipywidgets to
load the upload tool inside a cell.

Note, some of the tests expect you are running with a local server that you are both free
to manipulate as an administrator and also have local access to create buckets. If this
is not the case, you may be only able to run some parts of the notebooks.

## Getting Started

1) Create a virtualenv
2) Install the client library (not yet in pypi)

    ```
    cd client
    pip install -U .
    ```
3) Install other dependencies

   ```
   pip install jupyterlab ipywidgets
   ```
   
4) Get a PAT from your server and set the env var. Start jupyter lab

   ```
   export HOSS_PAT=<token>
   cd client/examples/notebooks
   jupyter lab
   ```
   
   
