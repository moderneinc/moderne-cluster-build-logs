from transformers import AutoTokenizer, AutoModel

# Model will download the first time they are initiallized
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-large-en-v1.5")
model = AutoModel.from_pretrained("BAAI/bge-large-en-v1.5")

