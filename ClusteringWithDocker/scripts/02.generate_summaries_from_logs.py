import pandas as pd
import requests
import json
from tqdm import tqdm
import pickle

# Load intermediate result
df = pd.read_pickle("df_with_logs.pkl")

# Initialize prompt
beg_prompt = "[INST] Summarize this build log in 100 words, focusing on the errors and the reasons for failure. Do not mention the name of the repository. The log is: "
end_prompt = "[/INST] The build failed"

summaries = []
responses = []

# Generate summaries
for log in tqdm(df["logs"]):   
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

pickle.dump(summaries, open("summaries.pkl", "wb"))
