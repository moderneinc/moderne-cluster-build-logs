import pandas as pd
import os

# Load data
df = pd.read_excel("repos/builds.xlsx")

# Only keep the logs of the failures
df = df[df["Outcome"] == "Failure"]
len_df = len(df)
df = pd.concat([df.dropna(subset=["Maven Version"]), df.dropna(subset=["Gradle Version"])])
print("Removed " + str(len_df - len(df)) + " rows for repos built without Maven nor Gradle")

# Extract logs
logs = []
for logpath in df["Build Log"]:
    # Construct the file path
    with open("repos/" + logpath, encoding='UTF-8') as f:
        logs.append(f.read())

# Save logs
df["logs"] = logs
df.to_pickle("df_with_logs.pkl")

print("Succesfully loaded " + str(len(df)) + " logs")