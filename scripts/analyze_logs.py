import argparse
import os
from pathlib import Path

from build_log_analyzer import BuildLogAnalyzer
from log_downloader import LogDownloader
from utils import copy_directory


def main(url, repository_path, log_file, username, password, logs_dir, output_dir):
    if not logs_dir:
        log_downloader = LogDownloader(
            url, repository_path, log_file, username, password, output_dir
        )
        log_downloader.download_logs()
    else:
        copy_directory(logs_dir, output_dir)

    analyzer = BuildLogAnalyzer(output_dir)
    analyzer.process_failure_logs()
    analyzer.load_failure_logs()
    analyzer.extract_failure_stacktraces()
    analyzer.analyze_and_visualize_clusters()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download and unzip ingest samples. If no url is provided, it will prompt the user to select a file.",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--logs",
        type=Path,
        help="Path to the local logs directory",
    )
    group.add_argument(
        "--url",
        help="Artifactory URL to download logs from",
    )

    download_group = parser.add_argument_group("Artifactory download options")

    download_group.add_argument(
        "--repository-path",
        default=os.environ.get("ARTIFACTORY_REPO_KEY"),
        help="The Artifactory repository key",
    )
    download_group.add_argument(
        "--log-file",
        default=None,
        help="The path of the file to download",
    )
    download_group.add_argument(
        "--username",
        default=os.environ.get("ARTIFACTORY_USER"),
        help="The Artifactory user",
    )
    download_group.add_argument(
        "--password",
        default=os.environ.get("ARTIFACTORY_PASSWORD"),
        help="The Artifactory password",
    )

    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory to store logs and results",
    )
    args = parser.parse_args()

    main(
        args.url,
        args.repository_path,
        args.log_file,
        args.username,
        args.password,
        args.logs,
        args.output_dir,
    )
