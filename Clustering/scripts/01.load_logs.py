import pandas as pd
import os

# Load data
df = pd.read_excel("repos/builds.xlsx")

# Only keep the logs of the failures
df = df[df["Outcome"] == "Failure"]

# Extract logs
logs = []
for logpath in df["Build Log"]:
    # Construct the file path
    with open("repos/" + logpath, encoding='UTF-8') as f:
        logs.append(f.read())

# Save logs
df["logs"] = logs

df.to_pickle("df_with_logs.pkl")
