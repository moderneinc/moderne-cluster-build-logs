Here's a README with the steps to set up a virtual environment and configure the project without using Docker.

# Project Setup Instructions

Follow these steps to set up your project in a virtual environment.

## Prerequisites

Make sure you have the following installed on your system:

- Python 3.X
- GCC (GNU Compiler Collection)
- Git

## Steps

1. **Set up Python Virtual Environment**

   Create and activate a virtual environment.

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

   Clone the llama.cpp repository and build the project.

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

7. **Activate Virtual Environment on Shell Start**

   Add the virtual environment activation command to your shell's startup file.

   ```bash
   echo "source $(pwd)/venv/bin/activate" >> ~/.bashrc
   source ~/.bashrc
   ```

Now you have your project set up in a virtual environment. You can start working on it by activating the virtual environment.

```bash
source venv/bin/activate
```


## Start Server


Run in the terminal 
```bash
nohup llama.cpp/server -m "codellama.gguf" -c 8000 --port "8080" &
```
`nohup` and `&` keeps the process running in the background, although I recommend running the process in the foreground first to make sure it is set up correctly, and then stopping using `Ctrl+C` and starting it again with `nohup` and `&`. You might need to enter `enter` to after running `nohup` to be able to keep running other commands.

You can modify the path to server pased on where you install llama.cpp. You can also modify the path to the model you've downloaded.


## Running the scripts

### Adding the logs

Copy the logs and the build.xlsx into the folder named "repos".

### Running the scripts

To run the scripts in order, use the following commands in your terminal. Make sure you are in the root folder of the project:

1. Load logs:
    ```bash
    python 01.load_logs.py
    ```

2. Generate summaries from logs (this step will take the longest time):
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

---

These commands should be executed one after the other in the specified order.


## Results

Once you have ran the 4 scripts, you can open cluster_id_reason.html and analysis_build_failures.html in your browser.