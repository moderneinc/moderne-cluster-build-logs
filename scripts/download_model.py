# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "transformers",
#     "torch",  # required by transformers for model handling
# ]
# ///

from transformers import AutoModel, AutoTokenizer

# Model will download the first time they are initialized
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")
model = AutoModel.from_pretrained("BAAI/bge-small-en-v1.5")
