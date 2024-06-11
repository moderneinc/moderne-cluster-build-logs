import pandas as pd
import re

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
    print(log)
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
        print(log)
        return ""

    return "\n".join(lines_to_keep)


if __name__ == "__main__":

    # Load intermediate result
    df = pd.read_pickle("df_with_logs.pkl")

    extract_stacktraces = []
    for row in df.iloc :
        # print(row["Maven Version"], row["Gradle Version"])
        if not pd.isna(row["Maven Version"]):
            extract_stacktraces.append(extract_stacktrace_maven(row))
        elif not pd.isna(row["Gradle Version"]):
            extract_stacktraces.append(extract_stacktrace_gradle(row))
        else:
            # print("Not Maven nor Gradle for",  str(row["Path"]))
            extract_stacktraces.append(None)

    

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