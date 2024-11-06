import pandas as pd
import re
import os 
from utils import PATH_TO_BUILDS, PATH_TO_FAILURES

def create_failures_tracker():
    # Load data
    df = pd.read_excel(PATH_TO_BUILDS)
    # Only keep the logs of the failures
    df = df[df["Outcome"] == "Failure"]
    # Add column "Solved" if not present, default to False
    if "Solved" not in df.columns:
        df["Solved"] = False
    len_df_before = len(df)
    df = df.drop_duplicates()
    print("Removed " + str(len_df_before - len(df)) + " duplicates")
    # Save logs
    df.to_csv(PATH_TO_FAILURES)
    print("Created " + PATH_TO_FAILURES + " with " + str(len(df)) + " rows")

if __name__ == "__main__":
    create_failures_tracker()