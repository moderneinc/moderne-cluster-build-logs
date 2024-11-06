import pandas as pd
import re
import os 
from utils import PATH_TO_BUILDS, PATH_TO_FAILURES

def load_failure_logs():

    #check if repos/failure.csv exists
    if not os.path.exists(PATH_TO_FAILURES):
        #exit
        print("File not found: " + PATH_TO_BUILDS + ". Please run 00.download_ingest_samples.py and 01.extract_failures.py first.")
        exit(1)
    
    df = pd.read_csv(PATH_TO_FAILURES)
    number_of_logs = len(df)
    if "logs" not in df.columns:
        df["logs"] = None

    for idx, row in df.iterrows():
        logpath = row["Build log"]
        if not os.path.exists("repos/" + logpath):
            # if you cannot find the log, we can assume the user considers that type of failure as solved
            df.at[idx, "Solved"] = True
        elif row["logs"] is None:
            df.at[idx, "logs"] = open("repos/" + logpath, encoding='UTF-8').read()
            
    # only keep the logs of the failures that haven't been solved yet
    df = df[df["Solved"] == False]

    df.to_pickle("df_with_logs.pkl")
    print("Succesfully loaded " + str(len(df)) + " logs. There were " + str(number_of_logs - len(df)) + " logs that were already solved, therefore they are not loaded.")


#FOR BAZEL
def extract_stacktrace_bazel(row):
    log = row["logs"]
    splits = log.split("BUILD FAILED with an exception:")
    message = splits[-1].strip().split("\n")[0]
    if splits[-2].strip().split("\n")[-1].startswith("ERROR"):
        message += "\n" + splits[-2].strip().split("\n")[-1]
    return message

#FOR DOTNET
def extract_stacktrace_dotnet(row):
    log = row["logs"]
    get_caused_by = log.split("Caused by: ")[-1]
    if get_caused_by:
        return get_caused_by.split("\n")[0]
    return ""


#FOR MAVEN
def extract_stacktrace_maven(row):
    log = row["logs"]
    patterns = [
    re.compile(r"(\[INFO\] BUILD FAILURE.*?Re-run Maven using the -X switch to enable full debug logging\.)", re.DOTALL),
    re.compile(r"(BUILD FAILED with an exception:.*)", re.DOTALL)
    ]

    matches = []

    # Find matches using the patterns
    for pattern in patterns:
        matches = pattern.findall(log)
        if len(matches) > 0:
            break

    if len(matches) > 0:
        extracted_log = remove_lines_stacktrace_maven(matches[-1])
        return extracted_log 
    # print(log)
    return None

def remove_lines_stacktrace_maven(log):
    lines_to_keep = []
    start_removing = True
    for line in log.split("\n"):
        if "[INFO] BUILD FAILURE" in line or "Caused by:" in line or "BUILD FAILED with an exception" in line:
            start_removing = False
        elif ("at org.apache.maven.plugin.DefaultMojosExecutionStrategy" in line 
              or "at org.apache.maven.lifecycle.internal.LifecycleDependencyResolver" in line 
              or "at org.apache.maven.lifecycle.internal.MojoExecutor.doExecute" in line) :
            start_removing = True
        if not start_removing:
            lines_to_keep.append(line)
    
    return "\n".join(lines_to_keep)

#FOR GRADLE
def extract_stacktrace_gradle(row):
    log = row["logs"]

    # Define the regex patterns
    patterns = [
        re.compile(r"(\* Exception is:.*?\* Get more help at https://help\.gradle\.org)", re.DOTALL),
        re.compile(r"(\* Exception is:.*?BUILD FAILED in)", re.DOTALL),
        re.compile(r"(BUILD FAILED with an exception:.*)", re.DOTALL)
    ]

    matches = []

    # Find matches using the patterns
    for pattern in patterns:
        matches = pattern.findall(log)
        if len(matches) > 0:
            break

    if len(matches) > 0:
        extracted_log = remove_lines_stacktrace_gradle(matches[-1])
        return extracted_log # return last match
    else:
        print("Gradle log not found for ", str(row["Path"]))
        return None

def remove_lines_stacktrace_gradle(log):
    lines_to_keep = []
    start_removing = True
    for line in log.split("\n"):
        if "* Exception is" in line or "Caused by: " in line or "BUILD FAILED with an exception" in line:
            start_removing = False
        elif ("at org.gradle.api.internal" in line
              or "at org.gradle.process.internal.DefaultExecHandle" in line
              or "at org.gradle.internal.DefaultBuildOperationRunner" in line):
            start_removing = True
        if not start_removing:
            lines_to_keep.append(line)

    if len(lines_to_keep) == 0:
        print("No lines left after removing stacktrace")
        # print(log)
        return ""

    return "\n".join(lines_to_keep)


if __name__ == "__main__":
    load_failure_logs()

    # Load intermediate result
    df = pd.read_pickle("df_with_logs.pkl")

    extract_stacktraces = []
    for row in df.iloc :
        if not pd.isna(row["Maven version"]):
            extract_stacktraces.append(extract_stacktrace_maven(row))
        elif not pd.isna(row["Gradle version"]):
            extract_stacktraces.append(extract_stacktrace_gradle(row))
        elif not pd.isna(row["Bazel version"]):
            extract_stacktraces.append(extract_stacktrace_bazel(row))
        elif not pd.isna(row["Dotnet version"]):
            extract_stacktraces.append(extract_stacktrace_dotnet(row))
        else:
            #If unsure what type of build, try all of them and keep the first one
            extracted_as_gradle = extract_stacktrace_gradle(row)
            extracted_as_maven = extract_stacktrace_maven(row)
            extracted_as_bazel = extract_stacktrace_bazel(row)
            extracted_as_dotnet = extract_stacktrace_dotnet(row)

            for extracted in [extracted_as_gradle, extracted_as_maven, extracted_as_bazel, extracted_as_dotnet]:
                if extracted is not None:
                    extract_stacktraces.append(extracted)
                    break
            
            
    # Save summaries
    df["Extracted logs"] = extract_stacktraces
    any_failures = False
    for row in df.iloc:
        extract_stacktrace = row["Extracted logs"]
        if extract_stacktrace is None or len(extract_stacktrace) == 0:
            print("Failure to extract log's stack trace from ", str(row["Path"]))
            any_failures = True

    if not any_failures:
        print("Succesfully extracted logs for", len(df), "repos")
    df.to_pickle("df_with_summaries.pkl")
