# Local Installation Guide

This project requires Python 3.12.x and manages dependencies using [`pyproject.toml`](pyproject.toml). Below are several methods to set up your environment.
## Using System Python with `venv`

1. Ensure Python 3.12.x is installed:
  ```bash
  python --version
  ```

2. Create a virtual environment:
  ```bash
  python -m venv .venv
  ```

3. Activate the virtual environment:
  ```bash
  # On Unix/macOS
  source .venv/bin/activate
  # On Windows
  .venv\Scripts\activate
  ```

4. Install dependencies:
  ```bash
  pip install .
  ```

## Using [uv](https://docs.astral.sh/uv/) (Fast Python Package Installer)

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/#installation-methods):
  ```bash
  pip install uv
  ```

2. Create a virtual environment and install dependencies:
  ```bash
  uv sync
  # or
  uv venv
  source .venv/bin/activate
  uv pip install .
  ```

## Using DevContainer

This project includes DevContainer configuration for VS Code:

1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) in VS Code
2. Open the project in VS Code
3. Click "Reopen in Container" when prompted or use the command palette (F1) and select "Dev Containers: Reopen in Container"

The container will automatically set up Python 3.12 and install all dependencies.

## Using Docker

Build and run the project using Docker:

```bash
# Build the image
docker build -t moderne-cluster-build-logs:latest .
```