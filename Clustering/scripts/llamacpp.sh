#!/bin/bash
curl -L https://github.com/ggerganov/llama.cpp/archive/refs/tags/b1961.zip --output llama.cpp-b1961.zip
jar xvf llama.cpp-b1961.zip
mv llama.cpp-b1961 llama.cpp
# curl -L https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/codellama-7b-instruct.Q4_K_M.gguf?download=true --output codellama.gguf