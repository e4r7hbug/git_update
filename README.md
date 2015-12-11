# Git Update

Use this to update a bunch of repositories in a directory. By default, the
current working directory is scanned for repositories.


## Install Modules

The preferred scenario is to use a virtual environment.

```bash
virtualenv venv
source ./venv/bin/activate
pip install -U -r requirements.txt
```


## Usage

Will use the current directory if none supplied.

```bash
# Check command help
./git_update.py --help

# Running repository updates
./git_update.py [DIR]
```
