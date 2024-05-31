### Clustering build logs to analyse common build issues

# Adding repos

* before running, add repos in subfolder names `repos` inside the folder `ClusteringWithDocker`.
* ensure `build.xlsx` is in the folder `repos`.

Example folder set-up:
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


# Docker

Install docker by following the steps [here](https://docs.docker.com/engine/install/). Make sure your docker daemon is running by running `docker ps`. If it isn't, you will have to start it, as explained [here](https://docs.docker.com/config/daemon/start/).

* build the image using `docker build -t cluster_logs . `
* run the container using `docker run --rm -it --entrypoint bash cluster_logs`

# Start LLM server

Run in the terminal `nohup llama.cpp/server -m "codellama.gguf" -c 8000 --port "8080" &` 
`nohup` and `&` keeps the process running in the background, although I recommend running the process in the foreground first to make sure it is set up correctly, and then stopping using `Ctrl+C` and starting it again with `nohup` and `&`. You might need to enter `enter` after running `nohup` to be able to keep running other commands.


# Run clustering
Run in order in the terminal 
* `python 01.load_logs.py`
* `python 02.generate_summaries_from_logs.py` // this step will take the longest time
* `python 03.embed_summaries_and_cluster.py`
* `python 04.cluster_summaries_results.py`


# Open Results

### Get docker ID
Open a new terminal and run:
```bash
docker ps
```

This command will list all running containers along with their IDs and names.

### Copy files

Once you have the container ID or name, you can use the docker cp command to copy the file from the container to your host machine. The syntax is:

```bash
docker cp <container_id_or_name>:<path_inside_container> <path_on_host>
```

For example, to copy the files `cluster_id_reason.html` and `analysis_build_failures.html` from the container to the host machine, you can run:

```bash
docker cp <container_id_or_name>:/cluster_id_reason.html .
docker cp <container_id_or_name>:/analysis_build_failures.html .
```

You can now open the files in your browser on your local machine.