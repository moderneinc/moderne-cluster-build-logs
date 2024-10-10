import pandas as pd
import torch
from tqdm import tqdm
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import umap
from transformers import AutoTokenizer, AutoModel
import plotly.express as px
import plotly.graph_objects as go

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


def embed_summaries_cluster():
    # Load intermediate result
    df = pd.read_pickle("df_with_summaries.pkl")

    # Embed summaries
    embds_summaries = [get_embedding(summary) for summary in tqdm(df["Extracted logs"])]
    df["embds_summaries"] = embds_summaries

    # Perform clustering
    best_silhouette_score = -100

    kmax = 20
    assert kmax<len(df), "Number of clusters is set at " + str(kmax) + " which is lower than the number of rows, which is " + str(len(df)) + "."

    random_state = 42

    for k in range(3, kmax + 1):
        kmeans = KMeans(n_clusters=k, n_init=10, random_state=random_state).fit_predict(embds_summaries)
        labels = kmeans
        score = silhouette_score(embds_summaries, labels, metric="euclidean")
        if score > best_silhouette_score:
            best_silhouette_score = score
            best_kmeans = kmeans

    df["kmeans_summary"] = best_kmeans

    # 2D mapping to show the clusters
    n_neighbors = 100 if len(df) > 100 else len(df)-1
    indices = umap.UMAP(n_neighbors=n_neighbors, min_dist=0.7, random_state=random_state).fit_transform(embds_summaries)
    df["x"] = indices[:, 0]
    df["y"] = indices[:, 1]

    # Save intermediate results
    df.to_pickle("df_with_embeddings_clusters.pkl")

if __name__ == "__main__":
    embed_summaries_cluster()

    # plot and show results
    # Load intermediate result
    df = pd.read_pickle("df_with_embeddings_clusters.pkl")

    # Generate cluster summaries
    cluster_id_reason = {}
    best_k = df["kmeans_summary"].nunique()

    df["Cluster label"] = pd.Categorical(df["kmeans_summary"].astype(str), categories=[str(i) for i in range(best_k)], ordered=True)

    df["Build"] = ["maven" if not pd.isna(row) else "gradle" for row in df["Maven version"]]

    def wrap_line(text, max_len=200, max_lines=8):
        lines = text.split("\n")
        wrapped_lines = []
        for line in lines:
            while len(line) > max_len:
                wrapped_lines.append(line[:max_len])
                line = line[max_len:]
            wrapped_lines.append(line)
            if len(wrapped_lines) >= max_lines:
                wrapped_lines = wrapped_lines[:max_lines]
                wrapped_lines[-1] += "(...)"  # Add ellipsis if truncated
                break
        return "<br>".join(wrapped_lines)

    df["Extracted logs"] = df["Extracted logs"].apply(lambda row: wrap_line(str(row)))
    # Create scatter plot
    fig = px.scatter(
        df,
        x="x",
        y="y",
        log_x=False,
        hover_data={
        "x": False,    # Exclude x from hover data
        "y": False,    # Exclude y from hover data
        "Path": True,
        "Branch": True,
        "Extracted logs": True}, # Rename column in hover
        symbol="Build",
        color="Cluster label",
        category_orders={"Cluster label": [str(i) for i in range(best_k)]},
        symbol_map={"maven": "circle", "gradle": "star"}
    )

    # Save scatter plot
    fig.write_html("clusters_scatter.html")


    # Function to create dropdown options
    def create_dropdown_options(data, cluster_id):
        samples = data[data["kmeans_summary"] == str(cluster_id)]["Extracted logs"]
        samples = [str(sample).replace('\n', '<br>') for sample in samples]  # Replace \n with <br> for HTML formatting
        return samples

    # Create dropdowns for each cluster
    dropdowns = []
    for cluster_id in range(best_k):
        dropdowns.append(create_dropdown_options(df, str(cluster_id)))

    # Create figures for samples view
    sample_figs = []
    for cluster_id in range(best_k):
        sample_fig = go.Figure(data=[go.Table(
            header=dict(values=["Samples"], fill_color='paleturquoise', align='left'),
            cells=dict(
                values=[dropdowns[cluster_id]],
                fill_color='lavender', 
                align='left',
                height=30
            )
        )])
        sample_figs.append(sample_fig)

    # Generate dropdown options for Plotly
    dropdown_buttons = [
        {
            "label": f"Logs for cluster ID {cluster_id}. Total Count : {len(df[df['kmeans_summary'] == str(cluster_id)])}",
            "method": "update",
            "args": [
                {"visible": [i == cluster_id for i in range(best_k)]},
            ]
        } for cluster_id in range(best_k)
    ]

    # Combine all sample figures into a single figure
    fig = go.Figure(data=[item for sublist in [fig.data for fig in sample_figs] for item in sublist])

    # Add dropdown menu to the figure
    fig.update_layout(
        updatemenus=[
            {
                "buttons": dropdown_buttons,
                "direction": "down",
                "showactive": True,
                "x": 0.5,
                "xanchor": "center",
                "y": 1.2,
                "yanchor": "top"
            }
        ],
        showlegend=False
    )

    # Set initial visibility
    initial_visibility = [True] + [False] * (best_k - 1)
    for i, data in enumerate(fig.data):
        data.visible = initial_visibility[i]

    # Save the table to HTML
    fig.write_html("clusters_logs.html")

    # Save final dataframe
    df.to_pickle("final_df.pkl")