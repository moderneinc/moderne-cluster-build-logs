from pathlib import Path
from typing import Optional

import click
from build_log_analyzer import BuildLogAnalyzer
from log_downloader import LogDownloader
from utils import copy_directory


def download_logs(
    url: str,
    repository_path: Optional[str],
    log_file: Optional[str],
    username: Optional[str],
    password: Optional[str],
    output_dir: Path,
) -> None:
    log_downloader = LogDownloader(
        url, repository_path, log_file, username, password, output_dir
    )
    log_downloader.download_logs()


def analyze_logs(
    output_dir: Path,
    logs_dir: Optional[Path] = None,
    skip_process_failure_logs: bool = False,
) -> None:
    analyzer = BuildLogAnalyzer(output_dir)

    if logs_dir:
        copy_directory(logs_dir, output_dir)

    if not skip_process_failure_logs:
        analyzer.process_failure_logs()
    analyzer.load_failure_logs()
    analyzer.extract_failure_stacktraces()
    analyzer.analyze_and_visualize_clusters()


@click.group()
def cli() -> None:
    """Analyze mass ingest build logs from Artifactory or local directories."""
    pass


@cli.command()
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option(
    "--url",
    required=True,
    show_envvar=True,
    prompt=True,
    envvar="ARTIFACTORY_URL",
)
@click.option(
    "--repository-path",
    show_envvar=True,
    envvar="ARTIFACTORY_REPOSITORY_PATH",
    help="Repository path. Will interactively prompt for log file.",
)
@click.option(
    "--log-file",
    show_envvar=True,
    envvar="ARTIFACTORY_LOG_FILE",
    help="Path to the log zip file in the repository.",
)
@click.option(
    "--username",
    required=False,
    show_envvar=True,
    envvar="ARTIFACTORY_USERNAME",
)
@click.option(
    "--password",
    required=False,
    show_envvar=True,
    envvar="ARTIFACTORY_PASSWORD",
)
def download(
    output_dir: Path,
    url: str,
    repository_path: Optional[str],
    log_file: Optional[str],
    username: Optional[str],
    password: Optional[str],
) -> None:
    """Download logs from Artifactory."""
    if not (repository_path or log_file) or (repository_path and log_file):
        raise click.UsageError(
            "Either --repository-path or --log-file must be provided"
        )

    download_logs(url, repository_path, log_file, username, password, output_dir)


# https://artifactory.moderne.ninja/artifactory/moderne-ingest/io/moderne/ingest-log/9-20/202412190022/ingest-log-202412190022-9.zip
@cli.command()
@click.argument("output_dir", type=click.Path(path_type=Path))
@click.option(
    "--from",
    "logs_dir",
    type=click.Path(exists=True, path_type=Path),
    help="Path to existing mass ingest logs directory",
)
@click.option(
    "--skip-process-failure-logs",
    is_flag=True,
    help="Skip creating failures.csv file",
)
def analyze(
    output_dir: Path,
    logs_dir: Optional[Path] = None,
    skip_process_failure_logs: bool = False,
) -> None:
    """Perform K-Means clustering on Mass Ingest build failure logs."""
    analyze_logs(output_dir, logs_dir, skip_process_failure_logs)


if __name__ == "__main__":
    cli()
