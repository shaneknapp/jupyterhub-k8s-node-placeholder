# jupyterhub-k8s-node-placeholder

This repository contains a Helm chart for deploying a JupyterHub Node Placeholder service on a Kubernetes cluster. The Node Placeholder service is designed to manage and allocate placeholder nodes for JupyterHub users, ensuring efficient resource utilization and improved user experience.

## Features

## Working with this repository

You will need Python 3.8+ and `pip` installed on your system. You can manage Python
environments using tools like `venv` or `conda`.

For basic development, you will need to install the dependencies listed in
`dev-requirements.txt`. You can do this by running:

``` bash
pip install -r dev-requirements.txt
```

For more advanced development, including testing any changes you make, you will
need to install the dependencies listed in
[`requirements.txt`](node-placeholder-scaler/requirements.txt).

``` bash
pip install -r node-placeholder-scaler/requirements.txt
```

### Pre-Commit hooks: Installing

The previous step, `pip install -r dev-requirements.txt`, installs the package
[`pre-commit`](https://pre-commit.com/). This is used to run a series of
commands defined in the file [`.pre-commit-config.yaml`](.pre-commit-config.yaml)
to help ensure no mistakes are committed to the repo.

After you've installed `dev-requirements.txt`, execute the following two
commands:

``` bash
pre-commit install
pre-commit run --all-files
```

### Development

When working with this repo, you should create a fork and work on a feature
branch. When you're ready to submit your changes, create a pull request against
your fork, and open a PR against the `main` branch of this repo.

#### Changing the Python imports

If you need to change or update the scaler's Python imports, you will need to
recompile the scaler's `requirements.txt` file. You can do this by running:

``` bash
cd node-placeholder-scaler
pip-compile --output-file=requirements.txt requirements.in
```

Create a PR with your changes, and these will be added to the latest image created.

#### Testing your changes

Right now, there are no automated tests for this repo. You can test your changes
to the Python code by running [test.py](node-placeholder-scaler/test.py):

``` bash
python node-placeholder-scaler/test.py
```

This will test the scaler's ability to read and parse calendar events from a known
iCal URL.
