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
def get_build_type(row):
    if not pd.isna(row["Maven version"]):
        return "maven"
    elif not pd.isna(row["Gradle version"]):
        return "gradle"
    elif not pd.isna(row["Bazel version"]):
        return "bazel"
    elif not pd.isna(row["Dotnet version"]):
        return "dotnet"
    else:
        return "unknown/other"

if __name__ == "__main__":
    embed_summaries_cluster()

    # plot and show results
    # Load intermediate result
    df = pd.read_pickle("df_with_embeddings_clusters.pkl")

    # Generate cluster summaries
    cluster_id_reason = {}
    best_k = df["kmeans_summary"].nunique()

    df["Cluster label"] = pd.Categorical(df["kmeans_summary"].astype(str), categories=[str(i) for i in range(best_k)], ordered=True)

    df["Build"] = df.apply(lambda row: get_build_type(row), axis=1)

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
        symbol_map={"maven": "circle", "gradle": "star", "bazel": "diamond", "dotnet": "hexagon", "unknown/other": "cross"},
    )

    # Convert the DataFrame to an HTML table format with embedded JavaScript for interactivity
    table = df.drop(columns=["Build log", "logs", "embds_summaries", "kmeans_summary", "x", "y", "Cluster label", "Build time (sec)", "Maven version", "Gradle version", "Bazel version", "Dotnet version", "Total sources"]) # Remove unnecessary columns
    table_html = table.to_html(classes="table table-striped", index=False, table_id="dataTable")

    # Save the scatter plot and table to HTML with embedded JavaScript
    html_content = f"""
<html>
<head>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        /* Tooltip styling */
        #hover-tooltip {{
            position: absolute;
            background-color: white;
            border: 1px solid #ccc;
            padding: 10px;
            box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.2);
            display: none; /* Initially hidden */
            z-index: 10;
        }}
    </style>
</head>
<body>
    
    {fig.to_html(full_html=False, include_plotlyjs=False)}

    <!-- Tooltip div for persistent hover data -->
    <div id="hover-tooltip"></div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var scatterPlot = document.getElementsByClassName('plotly-graph-div')[0];
            var tooltip = document.getElementById('hover-tooltip');

            scatterPlot.on('plotly_click', function(data) {{
                // Display tooltip near the clicked point
                tooltip.innerHTML = `
                    <strong>Path:</strong> ${{data.points[0].customdata[0]}}<br>
                    <strong>Branch:</strong> ${{data.points[0].customdata[1]}}<br>
                    <strong>Extracted logs:</strong> ${{data.points[0].customdata[2]}}
                `;
                tooltip.style.display = 'block';
                tooltip.style.left = data.event.pageX + 10 + 'px';
                tooltip.style.top = data.event.pageY + 10 + 'px';
            }});

            // Hide the tooltip when clicking outside of the plot area
            document.addEventListener('click', function(event) {{
                if (!scatterPlot.contains(event.target) && !tooltip.contains(event.target)) {{
                    tooltip.style.display = 'none';
                }}
            }});
        
            // Hide the tooltip when pressing the Escape key
            document.addEventListener('keydown', function(event) {{
                if (event.key === 'Escape') {{
                    tooltip.style.display = 'none';
                }}
            }});
        }});
    </script>
</body>
</html>
"""



    # Save HTML to file
    with open("clusters_scatter.html", "w") as f:
        f.write(html_content)



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