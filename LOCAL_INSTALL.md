## Prerequisites

Please ensure you have the following tools installed on your system:

* Python 3.12 (newer versions will not work)
  * [pyenv](https://github.com/pyenv/pyenv) is recommended
  * [Homebrew installation](https://formulae.brew.sh/formula/python@3.10) 
  * [Official Python installer](https://www.python.org/downloads/release/python-31014/)
* [Git](https://git-scm.com/downloads)

## Instructions

### Step 1: Clone this project

```bash
git clone git@github.com:moderneinc/moderne-cluster-build-logs.git
cd moderne-cluster-build-logs
```

### Step 2: Set up the Python virtual environment

You will be creating a server and running clustering inside of a Python virtual environment. To create said environment, please run:

```bash
## Pick the one that applies to your system
python -m venv venv

## For Mac or Linux users
source venv/bin/activate

## For Windows users
source venv\Scripts\activate
```

After running the `source` command, you should see that you're in a Python virtual environment.

### Step 3: Install dependencies

Double-check that `pip` is pointing to the correct Python version by running the following command. The output should include `python 3.12.X`. If it doesn't, try using `pip3` instead.

```bash
pip --version
```

Once you've confirmed which `pip` works for you, install dependencies by running the following command:

```bash
pip install -r requirements.txt
```

### Step 4: Download the model

Download the model which will assist with tokenizing and clustering of the build log data.

```bash
python scripts/download_model.py
```

### Step 5: Gather build logs

In order to perform an analysis on your build logs, all of them need to be copied over to this directory. Please ensure that they are copied over inside a folder named `repos`. 

You will also need a `build.xlsx` file that provides details about the builds such as where the build logs are located, what the outcome was, and what the path to the project is. This file should exist inside of `repos` directory.

Here is an example of what your directory should be look like if everything was set up correctly:

```
moderne-cluster-build-logs
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


#### Using Moderne mass ingest logs

If you want to use Moderne's mass ingest logs to run this scripts, you may use the following script to download a sample.

```bash
python scripts/00.download_ingest_samples.py
```

You will be prompted which of the slices you want to download. Enter the corresponding number and press `Enter`.


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

## Example results

Below you can see some examples of the HTML files produced by following the above steps.

### clusters_scatter.html

This file is a visual representation of the build failure clusters. Clusters that contain the most number of dots should generally be prioritized over ones that contain fewer dots. You can hover over the dots to see part of the build logs.

![expected_clusters](images/expected_clusters.gif)

#### cluster_logs.html

To see the full extracted logs, you may use this file. This file shows all the logs that belong to a cluster.

![logs](images/expected_logs.png)
