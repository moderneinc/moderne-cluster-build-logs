# Creating clusters without Docker

## Prerequisites

Please ensure you have the following tools installed on your system:

* Python 3.10 (newer versions will not work)
    * [Homebrew installation](https://formulae.brew.sh/formula/python@3.10) 
    * [Official Python installer](https://www.python.org/downloads/release/python-31014/)
* [Git](https://git-scm.com/downloads)

## Instructions

### Step 1: Clone this project

```shell
git clone git@github.com:moderneinc/moderne-cluster-build-logs.git
cd moderne-cluster-build-logs/Clustering
```

### Step 2: Gather build logs

In order to perform an analysis on your build logs, all of them need to be copied over to this directory (`Clustering`). Please ensure that they are copied over inside a folder named `repos`. 

You will also need a `build.xlsx` file that provides details about the builds such as where the build logs are located, what the outcome was, and what the path to the project is. This file should exist inside of `repos` directory.

Here is an example of what your directory should be look like if everything was set up correctly:

```
Clustering
│
├───scripts
│       (4 files)
│
└───repos
    │   builds.xlsx
    │
    ├───Org1
    │   ├───Repo1
    │   │   └───main
    │   │           build.log
    │   │
    │   └───Repo2
    │       └───master
    │               build.log
    │
    ├───Org2
    │   ├───Repo1
    │   │   └───main
    │   │           build.log
    │   │
    │   └───Repo2
    │       └───master
    │               build.log
    │
    └───Org3
        └───Repo1
            └───main
                    build.log
```

### Step 3: Confirm that you have the right version of Python

Depending on your operating system and how you've installed Python, you will run Python in the terminal by typing `python` or `python3.10`. Please ensure that the output from one of the following commands returns `Python 3.10.X`. **You will then use that command to run the rest of the Python commands in this repository**. 

```bash
python --version
python3.10 --version
```

### Step 4: Set up the Python virtual environment

You will be creating a server and running clustering inside of a Python virtual environment. To create said environment, please run:

```bash
## Pick the one that applies to your system
python -m venv venv
python3.10 -m venv venv 

## For Mac or Linux users
source venv/bin/activate

## For Windows users
source venv\Scripts\activate
```

After running the `source` command, you should see that you're in a Python virtual environment.

### Step 5: Install dependencies

Double-check that `pip` is pointing to the correct Python version by running the following command. The output should include `python 3.10.X`. If it doesn't, try using `pip3` instead.

```bash
pip --version
```

Once you've confirmed which `pip` works for you, install dependencies by running the following command:

```bash
pip install -r requirements.txt
```

If you can't find `requirements.txt`, please ensure that you're in the `Clustering` directory.

### Step 6: Run the scripts

_Please note these scripts won't function correctly if you haven't copied over the logs and `build.xlsx` file into the `repos` directory and put that inside of the `Clustering` directory you're working out of._

**Run the following scripts in order**:

1. Load the logs and extract relevant error messages and stacktraces from the logs:

```bash
python scripts/01.load_logs_and_extract.py
```

_Please note that the loaded logs only include those generated from failures to build Maven or Gradle projects. You can open `build.xlsx` if there are less logs loaded than expected_

2. Embed logs and cluster:

```bash
python scripts/02.embed_summaries_and_cluster.py
```

### Step 7: Analyze the results

Once you've run the two scripts, you should find that a `cluster_id_reason.html` and `analysis_build_failures.html` file was produced. Open those in the browser of your choice to get detailed information about your build failures.

Success! You can now freely exit out of the Python virtual environment by typing `exit` into the command line.

