import os
import re

import click
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import torch
import umap
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from tqdm import tqdm
from transformers import AutoModel, AutoTokenizer


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
            wrapped_lines[-1] += "(...)"
            break
    return "<br>".join(wrapped_lines)


class BuildLogAnalyzer:
    def __init__(self, output_dir="output"):
        self.tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")
        self.model = AutoModel.from_pretrained("BAAI/bge-small-en-v1.5")
        self.model.eval()
        self.random_state = 42
        self.data_frames: pd.DataFrame | None = None

        self.output_dir = output_dir
        self.build_manifest_path = os.path.join(output_dir, "builds.xlsx")
        self.failures_path = os.path.join(output_dir, "failures.csv")
        self.final_cluster_html_path = os.path.join(output_dir, "clusters_scatter.html")
        self.final_logs_html_path = os.path.join(output_dir, "clusters_logs.html")

    def get_embedding(self, input_string):
        if input_string is None or not isinstance(input_string, str):
            # Return zeros for invalid input
            return [0.0] * 384  # BGE-small model has 384 dimensions

        # Clean input string
        cleaned_input = str(input_string).strip()
        if not cleaned_input:
            return [0.0] * 384

        with torch.no_grad():
            encoded_input = self.tokenizer(
                [cleaned_input], padding=True, truncation=True, return_tensors="pt"
            )
            model_output = self.model(**encoded_input)
            embedding = model_output[0][:, 0]
            embedding = torch.nn.functional.normalize(embedding, p=2, dim=1)[0]
            return embedding.tolist()

    def _embed_summaries_cluster(self):
        df = self.data_frames

        # Clean and validate extracted logs
        df["Extracted logs"] = df["Extracted logs"].apply(
            lambda x: str(x).strip() if pd.notna(x) else ""
        )

        # Get embeddings
        embds_summaries = [
            self.get_embedding(summary) for summary in tqdm(df["Extracted logs"])
        ]
        df["embds_summaries"] = embds_summaries

        best_silhouette_score = -100
        kmax = 20
        assert kmax < len(
            df
        ), f"Number of clusters ({kmax}) must be lower than number of rows ({len(df)})."

        best_kmeans = None
        for k in range(3, kmax + 1):
            kmeans = KMeans(
                n_clusters=k, n_init=10, random_state=self.random_state
            ).fit_predict(embds_summaries)
            score = silhouette_score(embds_summaries, kmeans, metric="euclidean")
            if score > best_silhouette_score:
                best_silhouette_score = score
                best_kmeans = kmeans

        df["kmeans_summary"] = best_kmeans

        n_neighbors = 100 if len(df) > 100 else len(df) - 1
        indices = umap.UMAP(
            n_neighbors=n_neighbors, min_dist=0.7, random_state=self.random_state
        ).fit_transform(embds_summaries)
        df["x"] = indices[:, 0]
        df["y"] = indices[:, 1]

        self.data_frames = df

    def _create_scatter_plot(self):
        df = self.data_frames
        best_k = df["kmeans_summary"].nunique()
        df["Cluster label"] = pd.Categorical(
            df["kmeans_summary"].astype(str),
            categories=[str(i) for i in range(best_k)],
            ordered=True,
        )
        df["Build"] = df.apply(lambda row: get_build_type(row), axis=1)
        df["Extracted logs"] = df["Extracted logs"].apply(
            lambda row: wrap_line(str(row))
        )

        fig = px.scatter(
            df,
            x="x",
            y="y",
            hover_data={
                "x": False,
                "y": False,
                "Path": True,
                "Branch": True,
                "Extracted logs": True,
            },
            symbol="Build",
            color="Cluster label",
            category_orders={"Cluster label": [str(i) for i in range(best_k)]},
            symbol_map={
                "maven": "circle",
                "gradle": "star",
                "bazel": "diamond",
                "dotnet": "hexagon",
                "unknown/other": "cross",
            },
        )

        with open("templates/scatter_plot.html", "r", encoding="utf-8") as f:
            scatter_plot_template = f.read()

        with open("templates/tooltip_script.html", "r", encoding="utf-8") as f:
            tooltip_script_template = f.read()

        html_content = scatter_plot_template.format(
            plotly_js="https://cdn.plot.ly/plotly-latest.min.js",
            plotly_fig=fig.to_html(full_html=False, include_plotlyjs=False),
            tooltip_script=tooltip_script_template,
        )

        with open(self.final_cluster_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        click.echo(
            f"Scatter plot analysis saved to {click.format_filename(self.final_cluster_html_path)}"
        )

    def _create_cluster_logs(self):
        df = self.data_frames
        best_k = df["kmeans_summary"].nunique()

        def create_dropdown_options(data, cluster_id):
            samples = data[data["Cluster label"] == str(cluster_id)]["Extracted logs"]
            return [str(sample).replace("\n", "<br>") for sample in samples]

        dropdowns = [
            create_dropdown_options(df, str(cluster_id)) for cluster_id in range(best_k)
        ]
        sample_figs = []

        for cluster_id in range(best_k):
            sample_fig = go.Figure(
                data=[
                    go.Table(
                        header=dict(
                            values=["Samples"], fill_color="paleturquoise", align="left"
                        ),
                        cells=dict(
                            values=[dropdowns[cluster_id]],
                            fill_color="lavender",
                            align="left",
                            height=30,
                        ),
                    )
                ]
            )
            sample_figs.append(sample_fig)

        dropdown_buttons = [
            {
                "label": f"Logs for cluster ID {cluster_id}. Total Count : {len(df[df['Cluster label'] == str(cluster_id)])}",
                "method": "update",
                "args": [
                    {"visible": [str(i) == str(cluster_id) for i in range(best_k)]}
                ],
            }
            for cluster_id in range(best_k)
        ]

        fig = go.Figure(
            data=[
                item
                for sublist in [fig.data for fig in sample_figs]
                for item in sublist
            ]
        )
        fig.update_layout(
            updatemenus=[
                {
                    "buttons": dropdown_buttons,
                    "direction": "down",
                    "showactive": True,
                    "x": 0.5,
                    "xanchor": "center",
                    "y": 1.2,
                    "yanchor": "top",
                }
            ],
            showlegend=False,
        )

        for i, data in enumerate(fig.data):
            data.visible = i == 0

        fig.write_html(self.final_logs_html_path)
        click.echo(
            f"Cluster logs saved to {click.format_filename(self.final_logs_html_path)}"
        )

    def analyze_and_visualize_clusters(self):
        self._embed_summaries_cluster()
        self._create_scatter_plot()
        self._create_cluster_logs()

    def process_failure_logs(self):
        # Load data
        df = pd.read_excel(self.build_manifest_path)
        # Only keep the logs of the failures
        df = df[df["Outcome"] == "Failure"]
        # Add column "Solved" if not present, default to False
        if "Solved" not in df.columns:
            df["Solved"] = False
        len_df_before = len(df)
        df = df.drop_duplicates()
        click.echo("Removed " + str(len_df_before - len(df)) + " duplicates")
        # Save logs
        df.to_csv(self.failures_path)
        click.echo("Created " + self.failures_path + " with " + str(len(df)) + " rows")

    def load_failure_logs(self):
        # check if repos/failure.csv exists
        click.echo("Loading logs from " + click.format_filename(self.failures_path))
        if not os.path.exists(self.failures_path):
            # exit
            click.echo("File not found: " + self.failures_path, err=True)
            exit(1)
        df = pd.read_csv(self.failures_path)
        number_of_logs = len(df)
        if "logs" not in df.columns:
            df["logs"] = None
        for idx, row in df.iterrows():
            log_path = row["Build log"]
            if not os.path.exists(os.path.join(self.output_dir, log_path)):
                # if you cannot find the log, we can assume the user considers that type of failure as solved
                df.at[idx, "Solved"] = True
            elif row["logs"] is None:
                df.at[idx, "logs"] = open(
                    os.path.join(self.output_dir, log_path), encoding="UTF-8"
                ).read()
        # only keep the logs of the failures that haven't been solved yet
        df = df[df["Solved"] == False]
        self.data_frames = df

        click.echo("Successfully loaded " + str(len(df)) + " logs.")
        if number_of_logs > len(df):
            click.echo(
                "There were "
                + str(number_of_logs - len(df))
                + " logs that were already solved, therefore they are not loaded."
            )

    def _extract_stacktrace_bazel(self, row):
        log = row["logs"]
        parts = log.split("BUILD FAILED with an exception:")
        message = parts[-1].strip().split("\n")[0]

        error_line = parts[-2].strip().split("\n")[-1]
        if error_line.startswith("ERROR"):
            message += "\n" + error_line

        return message

    def _extract_stacktrace_dotnet(self, row):
        log = row["logs"]
        get_caused_by = log.split("Caused by: ")[-1]
        if get_caused_by:
            return get_caused_by.split("\n")[0]
        return ""

    def _extract_stacktrace_maven(self, row):
        log = row["logs"]
        patterns = [
            re.compile(
                r"(\[INFO\] BUILD FAILURE.*?Re-run Maven using the -X switch to enable full debug logging\.)",
                re.DOTALL,
            ),
            re.compile(r"(BUILD FAILED with an exception:.*)", re.DOTALL),
        ]
        matches = []
        # Find matches using the patterns
        for pattern in patterns:
            matches = pattern.findall(log)
            if len(matches) > 0:
                break
        if len(matches) > 0:
            extracted_log = self._remove_lines_stacktrace_maven(matches[-1])
            return extracted_log
        return None

    def _remove_lines_stacktrace_maven(self, log):
        lines_to_keep = []
        start_removing = True
        for line in log.split("\n"):
            if (
                "[INFO] BUILD FAILURE" in line
                or "Caused by:" in line
                or "BUILD FAILED with an exception" in line
            ):
                start_removing = False
            elif (
                "at org.apache.maven.plugin.DefaultMojosExecutionStrategy" in line
                or "at org.apache.maven.lifecycle.internal.LifecycleDependencyResolver"
                in line
                or "at org.apache.maven.lifecycle.internal.MojoExecutor.doExecute"
                in line
            ):
                start_removing = True
            if not start_removing:
                lines_to_keep.append(line)
        return "\n".join(lines_to_keep)

    def _extract_stacktrace_gradle(self, row):
        log = row["logs"]
        # Define the regex patterns
        patterns = [
            re.compile(
                r"(\* Exception is:.*?\* Get more help at https://help\.gradle\.org)",
                re.DOTALL,
            ),
            re.compile(r"(\* Exception is:.*?BUILD FAILED in)", re.DOTALL),
            re.compile(r"(BUILD FAILED with an exception:.*)", re.DOTALL),
        ]
        matches = []
        # Find matches using the patterns
        for pattern in patterns:
            matches = pattern.findall(log)
            if len(matches) > 0:
                break
        if len(matches) > 0:
            extracted_log = self._remove_lines_stacktrace_gradle(matches[-1])
            return extracted_log  # return last match
        else:
            click.echo("Gradle log not found for ", str(row["Path"]))
            return None

    def _remove_lines_stacktrace_gradle(self, log):
        lines_to_keep = []
        start_removing = True
        for line in log.split("\n"):
            if (
                "* Exception is" in line
                or "Caused by: " in line
                or "BUILD FAILED with an exception" in line
            ):
                start_removing = False
            elif (
                "at org.gradle.api.internal" in line
                or "at org.gradle.process.internal.DefaultExecHandle" in line
                or "at org.gradle.internal.DefaultBuildOperationRunner" in line
            ):
                start_removing = True
            if not start_removing:
                lines_to_keep.append(line)
        if len(lines_to_keep) == 0:
            click.echo("No lines left after removing stacktrace")
            return ""
        return "\n".join(lines_to_keep)

    def extract_failure_stacktraces(self):
        # Load intermediate result
        df = self.data_frames
        extract_stacktraces = []
        for row in df.iloc:
            if not pd.isna(row["Maven version"]):
                extract_stacktraces.append(self._extract_stacktrace_maven(row))
            elif not pd.isna(row["Gradle version"]):
                extract_stacktraces.append(self._extract_stacktrace_gradle(row))
            elif not pd.isna(row["Bazel version"]):
                extract_stacktraces.append(self._extract_stacktrace_bazel(row))
            elif not pd.isna(row["Dotnet version"]):
                extract_stacktraces.append(self._extract_stacktrace_dotnet(row))
            else:
                # Try each build type and keep the first successful extraction
                extractors = [
                    self._extract_stacktrace_gradle,
                    self._extract_stacktrace_maven,
                    self._extract_stacktrace_bazel,
                    self._extract_stacktrace_dotnet,
                ]
                for extractor in extractors:
                    try:
                        extracted = extractor(row)
                        if extracted is not None:
                            extract_stacktraces.append(extracted)
                            break
                    except IndexError:
                        continue
        # Save summaries
        df["Extracted logs"] = extract_stacktraces
        any_failures = False
        for row in df.iloc:
            extract_stacktrace = row["Extracted logs"]
            if extract_stacktrace is None or len(extract_stacktrace) == 0:
                click.echo(
                    f"Failure to extract log's stack trace from {row['Path']}", err=True
                )
                any_failures = True
        if not any_failures:
            click.echo(
                f"Successfully extracted logs for {len(df)} in {self.output_dir}"
            )
        self.data_frames = df
