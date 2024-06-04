import pandas as pd
import requests
import json
from tqdm import tqdm
import pickle

# Load intermediate result
df = pd.read_pickle("df_with_logs.pkl")

# Initialize prompt
beg_prompt = "Instruct: Summarize this build log in 50 words, focusing on the errors and the reasons for failure. Do not mention the name of the repository. The log is: "
end_prompt = "Output: The build failed because "

summaries = []
responses = []

# Generate summaries
for log in tqdm(df["logs"]):   
    log = log[:4*1800] # truncate if log is too long
    prompt = beg_prompt + "\n" + log + "\n" + end_prompt
    data = {"stream": False, "n_predict": 100, "prompt": prompt}
    url = 'http://localhost:8080/completion'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers).text
    responses.append(response)
    content = json.loads(response)["content"]
    summaries.append(content)

# Save summaries
df["Summaries"] = summaries
df.to_pickle("df_with_summaries.pkl")
pickle.dump(summaries, open("summaries.pkl", "wb"))