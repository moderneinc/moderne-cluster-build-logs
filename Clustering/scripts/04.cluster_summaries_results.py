import pandas as pd
import requests
import json
from tqdm import tqdm
import plotly.express as px
import plotly.graph_objects as go

# Load intermediate result
df = pd.read_pickle("df_with_embeddings_clusters.pkl")

# Generate cluster summaries
cluster_id_reason = {}
best_k = df["kmeans_summary"].nunique()

df["kmeans_summary"] = pd.Categorical(df["kmeans_summary"].astype(str), categories=[str(i) for i in range(best_k)], ordered=True)

df["build"] = ["maven" if not pd.isna(row) else "gradle" for row in df["Maven Version"]]

df["Extracted logs with line break"] = ["<br>".join(str(row).split("\n")[:8]) for row in df["Extracted logs"]]
# Create scatter plot
fig = px.scatter(
    df,
    x="x",
    y="y",
    log_x=False,
    # hover_name=["Path"],
    hover_data=["Path", "Extracted logs with line break"],
    symbol="build",
    color="kmeans_summary",
    category_orders={"kmeans_summary": [str(i) for i in range(best_k)]},
    symbol_map={"maven": "circle", "gradle": "star"}
)

# Save scatter plot
fig.write_html("analysis_build_failures.html")


# Function to create dropdown options
def create_dropdown_options(data, cluster_id, k=7):
    samples = data[data["kmeans_summary"] == str(cluster_id)]["Extracted logs"]
    samples = [str(sample).replace('\n', '<br>') for sample in samples]  # Replace \n with <br> for HTML formatting
    return samples[:k]

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
        "label": f"Samples for cluster ID {cluster_id}",
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
fig.write_html("cluster_samples.html")

# Save final dataframe
df.to_pickle("final_df.pkl")