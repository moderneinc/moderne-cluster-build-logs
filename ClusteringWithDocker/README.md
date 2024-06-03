# Creating clusters with Docker

## Prerequisites

Please ensure that you have [Docker](https://docs.docker.com/) installed on your machine. We recommend that you use [Docker Desktop](https://docs.docker.com/get-docker/) – but you are also welcome to install just the [Docker engine itself](https://docs.docker.com/engine/install/).

## Instructions

### Step 1: Clone this project

```shell
git clone git@github.com:moderneinc/moderne-cluster-build-logs.git
cd moderne-cluster-build-logs/ClusteringWithDocker
```

### Step 2: Gather the build logs

In order to perform an analysis on your build logs, all of them need to be copied over to this directory (`ClusteringWithDocker`). Please ensure that they are copied over inside a folder named `repos`. 

You will also need a `build.xlsx` file that provides details about the builds such as where the build logs are located, what the outcome was, and what the path to the project is. This file should exist inside of `repos` directory.

Here is an example of what your directory should be look like if everything was set up correctly:

```
ClusteringWithDocker
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

### Step 3: Confirm Docker is running

From your command line, run the following command:

```bash
docker ps
```

You should see: `CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES`. 

If you don't, please ensure that [you've started up the Docker daemon correctly](https://docs.docker.com/config/daemon/start/).

### Step 4: Build the image and run the Docker container

Build the image by running the following command:

```bash
docker build -t cluster_logs .
```

Then run the container:

```bash
docker run --rm -it --entrypoint bash cluster_logs
```

You should now be in a virtual environment inside of the Docker container.

### Step 4: Start the Llama server

From your virtual environment, start up the Llama server by running the following command:

```bash
nohup llama.cpp/server -m "codellama.gguf" -c 8000 --port "8080" &
```

You may notice that `nohup: ignoring input...` may appear on your command line. That is safe to ignore. Just press `enter` to get to a blank command line.

### Step 5: Run the scripts

_Please note these scripts won't function correctly if you haven't copied over the logs and `build.xlsx` file into the `repos` directory and put that inside of the `ClusteringWithDocker` directory you're working out of._

Run the following scripts in order:

1. Load the logs:

```bash
python 01.load_logs.py
```

2. Generate summaries from logs (this step can take **significant amount of time** – if you want to get summaries faster, consider following the [non-Docker clustering instructions](../Clustering/README.md)):
    
```bash
python 02.generate_summaries_from_logs.py
```

3. Embed summaries and cluster:

```bash
python 03.embed_summaries_and_cluster.py
```

4. Cluster summaries results:

```bash
python 04.cluster_summaries_results.py
```

### Step 6: Get the results

In a new terminal window, run the following command:

```bash
docker ps
```

This will list all of the containers running along with their IDs and names. Figure out which container ID/name corresponds to this clustering repository and then run the following commands to copy the necessary files from the container to your host machine:

```bash
docker cp <container_id_or_name>:/app/cluster_id_reason.html .
docker cp <container_id_or_name>:/app/analysis_build_failures.html .
```

You can then open those HTML files in the browser of your choice to get detailed information about your build failures.

### Step 7: Cleanup

Once you've obtained the reports, feel free to turn off Docker and stop the container. If you're using Docker desktop, this is as simple as quitting the application. Otherwise, you can use the [docker stop command](https://docs.docker.com/reference/cli/docker/container/stop/) and then the [docker rm command](https://docs.docker.com/reference/cli/docker/container/rm/).