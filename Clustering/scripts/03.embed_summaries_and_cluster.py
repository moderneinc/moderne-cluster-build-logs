import pandas as pd
import torch
import pickle
from tqdm import tqdm
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import umap
from transformers import AutoTokenizer, AutoModel

# Initialize model
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-large-en-v1.5")
model = AutoModel.from_pretrained("BAAI/bge-large-en-v1.5")
model.eval()

def get_embedding(input_string):
    with torch.no_grad():
        encoded_input = tokenizer([input_string], padding=True, truncation=True, return_tensors='pt')
        model_output = model(**encoded_input)
        embedding = model_output[0][:, 0]
        embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)[0]
        return embedding.tolist()



# Load intermediate result
df = pd.read_pickle("df_with_summaries.pkl")

# Embed summaries
embds_summaries = [get_embedding(summary) for summary in tqdm(df["Extracted logs"])]
df["embds_summaries"] = embds_summaries

# Perform clustering
best_silhouette_score = -100
kmax = 15 # change back to 15
best_k = -1

for k in range(3, kmax + 1):
    kmeans = KMeans(n_clusters=k, random_state=0, n_init=10).fit_predict(embds_summaries)
    labels = kmeans
    score = silhouette_score(embds_summaries, labels, metric="euclidean")
    if score > best_silhouette_score:
        best_silhouette_score = score
        best_k = k
        best_kmeans = kmeans

df["kmeans_summary"] = best_kmeans

# 2D mapping to show the clusters
indices = umap.UMAP(n_neighbors=100, min_dist=0.7).fit_transform(embds_summaries)
df["x"] = indices[:, 0]
df["y"] = indices[:, 1]

# Save intermediate results
df.to_pickle("df_with_embeddings_clusters.pkl")