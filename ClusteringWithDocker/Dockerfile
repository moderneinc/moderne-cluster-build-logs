# Use the official Python image from the Docker Hub
FROM eclipse-temurin:17-jdk
# FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

#set up C compilers for calling make on llama.cpp
RUN apt-get update && apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 && \
    apt-get install -y python3-dev && \
    apt-get install -y python2 && \
    apt-get install -y curl

RUN apt-get update && \
    apt-get install -y gcc
RUN apt-get install gcc-11 g++-11
ENV CXX=/usr/bin/g++-11
RUN apt-get install -y build-essential curl

ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"
# COPY $JAVA_HOME $JAVA_HOME

RUN wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py && rm get-pip.py

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install virtualenv
RUN pip install virtualenv

# Create a virtual environment in the container
RUN virtualenv venv

# Activate the virtual environment and install the dependencies
RUN . venv/bin/activate && pip install -r requirements.txt

# # Copy the rest
COPY scripts/llamacpp.sh .
RUN sh llamacpp.sh
RUN cd llama.cpp && make 
RUN curl -L https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/codellama-7b-instruct.Q4_K_M.gguf?download=true --output codellama.gguf

COPY scripts .
COPY repos repos

# Ensure the virtual environment is activated for all shell sessions
RUN echo "source /app/venv/bin/activate" >> ~/.bashrc

# Set the default command to start a bash shell
ENTRYPOINT ["/bin/bash"]

# Default command to execute when the container starts
CMD ["-c", "source /app/venv/bin/activate && exec bash"]