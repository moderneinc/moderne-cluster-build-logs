# Creating clusters without Docker

## Prerequisites

Please ensure you have the following tools installed on your system:

* Python 3.X 
    * [Homebrew installation](https://docs.brew.sh/Homebrew-and-Python) 
    * [Official Python installer](https://www.python.org/downloads/)
* GCC (GNU Compiler Collection)
    * [Homebrew installation](https://formulae.brew.sh/formula/gcc)
    * [GCC Binaries](https://gcc.gnu.org/install/binaries.html)
    * Linux systems should come with this pre-installed. If not, try running `sudo apt-get install gcc` (for Debian based distributions) or `sudo yum install gcc` (for RPM based distributions).
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

Depending on your operating system and how you've installed Python, you will run Python in the terminal by typing `python` or `python3`. Please ensure that the output from one of the following commands returns `Python 3.X.X`. **You will then use that command to run the rest of the Python commands in this repository**. 

```bash
python --version
python3 --version
```

### Step 4: Set up the Python virtual environment

You will be creating a server and running clustering inside of a Python virtual environment. To create said environment, please run:

```bash
python -m venv venv

## For Mac or Linux users
source venv/bin/activate

## For Windows users
source venv\Scripts\activate
```

After running the `source` command, you should see that you're in a Python virtual environment.

### Step 5: Install dependencies

Double-check that `pip` is pointing to the correct Python version by running the following command. The output should include `python 3.X`. If it doesn't, try using `pip3` instead.

```bash
pip --version
```

Once you've confirmed which `pip` works for you, install dependencies by running the following command:

```bash
pip install -r requirements.txt
```

If you can't find `requirements.txt`, please ensure that you're in the `Clustering` directory.

### Step 6: Download and set up Llama

Clone the [llama.cpp repository](https://github.com/ggerganov/llama.cpp) and `cd` into the directory:

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
```

Follow the [instructions in their repository to build llama](https://github.com/ggerganov/llama.cpp?tab=readme-ov-file#build). You may wish to customize hardware acceleration depending on your OS and hardware.

Once you've run the `make` command inside of your clone, `cd` back to the `Clustering` directory:

```bash
make
cd ..
```

### Step 7: Download the CodeLlama model

You will use the CodeLlama model to analyze your code. Download the model by running:

```bash
curl -L https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf?download=true--output phi-2.gguf
```

### Step 8: Start the server

You will need to start up the llama server before you can run the scripts to analyze your code. We'd recommend you start by running the following command and then interrupting it if it started successfully (typically via `ctrl + c`):

```bash
# Abort after confirming it works
llama.cpp/server -m "phi-2.gguf" -c 8000 --port "8080"
```

Once you've confirmed it worked correctly, we'd encourage you to use [nohup](https://en.wikipedia.org/wiki/Nohup) to keep the server running in the background:

```bash
nohup llama.cpp/server -m "phi-2.gguf" -c 8000 --port "8080" &
```

This will return a process ID that you can later kill when you're done analyzing your builds. For more information on how to kill the server or how to get the process ID at a later time, please see the [additional server information section](#additional-server-information)

Please note that you can modify the server startup command to meet your needs – such as changing the path to the server or the path to the model.

### Step 9: Run the scripts

_Please note these scripts won't function correctly if you haven't copied over the logs and `build.xlsx` file into the `repos` directory and put that inside of the `Clustering` directory you're working out of._

Run the following scripts in order:

1. Load the logs:

```bash
python scripts/01.load_logs.py
```

2. Generate summaries from logs (this step can take a bit of time depending on how many repositories you're analyzing):
    
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

### Step 10: Analyze the results

Once you've run the four scripts, you should find that a `cluster_id_reason.html` and `analysis_build_failures.html` file was produced. Open those in the browser of your choice to get detailed information about your build failures.

Success! You can now freely exit out of the Python virtual environment by typing `exit` into the command line. You should also [turn off the llama server](#additional-server-information).

## Additional server information

If you've started the server using `nohup`, you can look for the process ID by running one of the following commands:

**For Mac or Linux users:**

```bash
lsof -i :8080
```

**Windows users:**

```bash
netstat -ano | findstr :8080
```

These commands will return a process ID that you can then use to kill the server by running one of the following commands (replacing `<PID>` with the process ID returned from the above command):

**For Mac or Linux users:**

```bash
kill -9 <PID>
```

**Windows users:**

```bash
taskkill /PID <PID> /F
```
