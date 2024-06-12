# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install virtualenv
RUN pip install virtualenv

# Create a virtual environment in the container
RUN virtualenv venv

# Activate the virtual environment and install the dependencies
RUN . venv/bin/activate && pip install -r requirements.txt

COPY scripts .
COPY repos repos

# Ensure the virtual environment is activated for all shell sessions
RUN echo "source /app/venv/bin/activate" >> ~/.bashrc

# Set the default command to start a bash shell
ENTRYPOINT ["/bin/bash"]

# Default command to execute when the container starts
CMD ["-c", "source /app/venv/bin/activate && exec bash"]