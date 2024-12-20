# Clustering build logs to analyze common build issues

When your company attempts to build [Lossless Semantic Trees (LSTs)](https://docs.moderne.io/administrator-documentation/moderne-platform/references/lossless-semantic-trees/) for all of your repositories, you may find that some of them do not build successfully. While you _could_ go through each of those by hand and attempt to figure out common patterns, there is a better way: [cluster analysis](https://en.wikipedia.org/wiki/Cluster_analysis).

You can think of cluster analysis as a way of grouping data into easily identifiable chunks. In other words, it can take in all of your build failures and then find what issues are the most common - so you can prioritize what to fix first.

This repository will walk you through everything you need to do to perform a cluster analysis on your build failures. By the end, you will have produced two HTML files:
1. [one that visually displays the clusters](#analysis_build_failureshtml)
2. [one that contains samples for each cluster](#cluster_id_reasonhtml). 

> [!NOTE]
> Clustering is currently limited to Maven, Gradle, .Net, and Bazel builds because our heuristic-based extraction of build errors is specific to these build types. Although build failures for other types won't cause error when clustering, the heuristic extraction may overlook valuable parts of the stack trace.

## Setup

Before you begin, you will need to complete one of the setup methods in [LOCAL_INSTALL.md](LOCAL_INSTALL.md). This will ensure that you have all the necessary dependencies installed.
1. [Using System Python with `venv`](LOCAL_INSTALL.md#using-system-python-with-venv)
2. [Using uv](LOCAL_INSTALL.md#using-uv-fast-python-package-installer) (Fast Python Package Installer)
3. [Using DevContainer](LOCAL_INSTALL.md#using-devcontainer)
4. [Using Docker](LOCAL_INSTALL.md#using-docker)


## Instructions

After [set-up / installation](LOCAL_INSTALL.md), you can run the analysis script in one of two ways: 
1. [Using an existing build log file](#using-an-existing-build-log-file)
2. [Downloading build logs from a Artifactory repository](#downloading-build-logs-from-an-artifactory-repository)

### Using an existing build log file

```bash
# System Python with venv / DevContainer
python script/analyze_logs.py \
  --logs <path_to_build_logs> \
  --output <output_directory>

# or using uv
uv run script/analyze_logs.py \
  --logs <path_to_build_logs> \
  --output <output_directory>

# or using Docker
docker run -rm -it \
  -v <path_to_build_logs>:/app/logs \
  -v <path_to_output_directory>:/app/output \
  moderne-cluster-build-logs:latest \
  python analyze_logs.py \
  --logs /app/logs \
  --output /app/output
```


### Downloading build logs from an Artifactory repository

The script can also download build logs from an Artifactory repository. You will need to provide the URL, repository path, username, and password to access the logs. You can also provide a specific log file to analyze. If you do not provide a specific log file, the script will provide an interactive selection for available logs.

```bash
# System Python with venv / DevContainer
python script/analyze_logs.py \
  --url <artifactory_url> \
  --repository-path <artifactory_repository_path_to_logs> \
  --username <artifactory_username> \
  --password <artifactory_passwd> \
  --log-file <specific_log_file> \ # Optional
  --output-dir ./output 

# or using uv
uv run script/analyze_logs.py \
  --url <artifactory_url> \
  --repository-path <artifactory_repository_path_to_logs> \
  --username <artifactory_username> \
  --password <artifactory_passwd> \
  --log-file <specific_log_file> \ # Optional
  --output-dir ./output 

# or using Docker
docker run -rm -it \
  -v <path_to_output_directory>:/app/output \
  moderne-cluster-build-logs:latest \
  python analyze_logs.py \
  --url <artifactory_url> \
  --repository-path <artifactory_repository_path_to_logs> \
  --username <artifactory_username> \
  --password <artifactory_passwd> \
  --log-file <specific_log_file> \ # Optional
  --output-dir /app/output
```


## Example results

Below you can see some examples of the HTML files produced by following the above steps.

### `clusters_scatter.html`

This file is a visual representation of the build failure clusters. Clusters that contain the most number of dots should generally be prioritized over ones that contain fewer dots. You can hover over the dots to see part of the build logs.

![expected_clusters](images/expected_clusters.gif)

### `cluster_logs.html`

To see the full extracted logs, you may use this file. This file shows all the logs that belong to a cluster.

![logs](images/expected_logs.png)
