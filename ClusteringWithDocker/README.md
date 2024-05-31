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
