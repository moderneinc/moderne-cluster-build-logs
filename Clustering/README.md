Here's a README with the steps to set up a virtual environment and configure the project without using Docker.

# Adding repos

* before running, add repos in subfolder names `repos` inside the folder `Clustering`.
* ensure `build.xlsx` is in the folder `repos`.

Example folder set-up:
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

# Project Setup Instructions

Follow these steps to set up your project in a virtual environment.

## Prerequisites

Make sure you have the following installed on your system:

- Python 3.X (using [brew](https://docs.brew.sh/Homebrew-and-Python) or the official [python](https://www.python.org/downloads/) installer)
- GCC (GNU Compiler Collection) [(instructions)](#-install-gcc-by-running-these-commands)
- Git

## Steps

1. **Set up Python Virtual Environment**
   
   First verify you have the right version of python installed and check if output is `Python 3.X.X`

   ```bash
   python --version
   ```
   

   Then, create and activate a virtual environment.

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. **Install Dependencies**

   Make sure you have `pip` installed, then install the required Python packages.

   ```bash
   pip install -r requirements.txt
   ```

3. **Download and Set Up llama.cpp**

   Clone the llama.cpp repository and build the project. You can follow the instruction on the [llama.cpp](https://github.com/ggerganov/llama.cpp) repository. Consider using their accelerations such as Metal for macOS and CUDA if you use a NVIDIA GPU.

   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   make
   cd ..
   ```


6. **Download CodeLlama Model**

   Download the CodeLlama model.

   ```bash
   curl -L https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/codellama-7b-instruct.Q4_K_M.gguf?download=true --output codellama.gguf
   ```


## Start Server


Run in the terminal 
```bash
nohup llama.cpp/server -m "codellama.gguf" -c 8000 --port "8080" &
```
`nohup` and `&` keeps the process running in the background, although I recommend running the process in the foreground first to make sure it is set up correctly, and then stopping using `Ctrl+C` and starting it again with `nohup` and `&`. You might need to enter `enter` to after running `nohup` to be able to keep running other commands.

You can modify the path to server pased on where you install llama.cpp. You can also modify the path to the model you've downloaded.

### Killing the server after clustering is done

Since the server is running in the background, you can't use Ctrl+C to stop it. You'll need to go find the process ID to then kill it. 
You can get the process id by running. It will be marked under "server" in the terminal output:

#### For Mac or Linux:
```bash
lsof -i :8080
```

to then kill the process, replace `<PID>` with the process id, and run: 
```bash
kill -9 <PID>
```

#### For Windows:
```bash
netstat -ano | findstr :8080
```
to then kill the process, replace `<PID>` with the process id, and run:
```bash 
taskkill /PID <PID> /F
```


## Running the scripts

### Adding the logs

Copy the logs and the build.xlsx into the folder named "repos".

### Running the scripts

To run the scripts in order, use the following commands in your terminal. Make sure you are in the root folder of the project:

1. Load logs:
    ```bash
    python scripts/01.load_logs.py
    ```

2. Generate summaries from logs (this step will take the longest time):
    ```bash
    python scripts/02.generate_summaries_from_logs.py
    ```

3. Embed summaries and cluster:
    ```bash
    python scripts/03.embed_summaries_and_cluster.py
    ```

4. Cluster summaries results:
    ```bash
    python scripts/04.cluster_summaries_results.py
    ```

---

These commands should be executed one after the other in the specified order.


## Results

Once you have ran the 4 scripts, you can open cluster_id_reason.html and analysis_build_failures.html in your browser.



#### * Install GCC by running these commands

```bash
sudo apt-get update
sudo apt-get install -y gcc
sudo apt-get install -y gcc-11 g++-11
export CXX=/usr/bin/g++-11
sudo apt-get install -y build-essential```