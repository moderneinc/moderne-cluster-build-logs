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

for cluster_id in tqdm(range(best_k)):
    all_summaries = "\n".join(df[df["kmeans_summary"] == cluster_id]["Extracted logs"])
    prompt = "[INST] Provide a short summary for the common reason for each of the following failures: " + all_summaries + "\n[/INST] Sure, here's a 5 words summary: \""
    data = {"stream": False, "n_predict": 35, "prompt": prompt}
    url = 'http://localhost:8080/completion'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers).text
    content = json.loads(response)["content"].split("\n")[0].strip("\"")
    cluster_id_reason[cluster_id] = content



df["common_reason_of_failure"] = [cluster_id_reason[int(fail)] for fail in df["kmeans_summary"]]
df["kmeans_summary"] = pd.Categorical(df["kmeans_summary"].astype(str), categories=[str(i) for i in range(best_k)], ordered=True)

df["build"] = ["maven" if not pd.isna(row) else "gradle" for row in df["Maven Version"]]
# Create scatter plot
fig = px.scatter(
    df,
    x="x",
    y="y",
    log_x=False,
    hover_name="Path",
    symbol="build",
    color="kmeans_summary",
    category_orders={"kmeans_summary": [str(i) for i in range(best_k)]},
    symbol_map={"maven": "circle", "gradle": "star"}
)

# Save scatter plot
fig.write_html("analysis_build_failures.html")

# Create and save summary table
table_df = pd.DataFrame({
    "Cluster ID": [str(i) for i in range(best_k)],
    "Reason for Failure": [cluster_id_reason[i] for i in range(best_k)]
})

fig_table = go.Figure(data=[go.Table(
    header=dict(values=list(table_df.columns), fill_color='paleturquoise', align='left'),
    cells=dict(values=[table_df["Cluster ID"], table_df["Reason for Failure"]], fill_color='lavender', align='left'))
])

fig_table.write_html("cluster_id_reason.html")

# Save final dataframe
df.to_csv("analysis_build_failures.csv")

# Save intermediate results
df.to_pickle("final_df.pkl")