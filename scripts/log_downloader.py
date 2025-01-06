import os
import sys
import zipfile
from urllib.parse import urljoin

import click
import requests
from utils import normalize_url, prepare_directory


class LogDownloader:
    def __init__(self, url, repository_path, log_file, username, password, output_dir):
        self.url = url
        self.repository_path = repository_path
        self.log_file = log_file
        self.auth = (username, password) if username is not None else None
        self.output_dir = output_dir

    def download_logs(self):
        if self.log_file:
            self._download_and_unzip_file(
                normalize_url(f"{self.url}/{self.log_file}"), "ingest.zip"
            )
        else:
            self._download_logs_interactive()

    def _download_and_unzip_file(self, url, file_name):
        local_filename = self._download_file(url, file_name)
        if not local_filename:
            return

        # Prepare extraction directory
        extract_to = self.output_dir
        prepare_directory(extract_to)

        self._unzip_file(local_filename, extract_to)

        # Count files in repos
        file_count = len(
            [
                name
                for name in os.listdir(extract_to)
                if os.path.isfile(os.path.join(extract_to, name))
            ]
        )
        click.echo(
            f"Extracted {file_count} file{'s' if file_count != 1 else ''} to {extract_to}"
        )

        # Remove downloaded zip file
        os.remove(local_filename)

    def _download_logs_interactive(self, path=""):
        fetching_from_url = normalize_url(
            f"{self.url}/api/storage/{self.repository_path}/{path}"
        )
        print(fetching_from_url)

        items = self._collect_items(
            normalize_url(f"{self.url}/api/storage/{self.repository_path}"), path
        )
        sorted_items = sorted(items, key=lambda x: x["name"])[:20]

        if not sorted_items:
            print("No files found to download.")
            return

        if len(sorted_items) == 1:
            selected_item = sorted_items[0]
            if selected_item["name"].endswith(".zip"):
                self._download_and_unzip_file(
                    normalize_url(
                        f"{self.url}/{self.repository_path}/{selected_item['path']}"
                    ),
                    selected_item["name"],
                )
                return
            else:
                self._download_logs_interactive(selected_item["path"])
                return

        for idx, file in enumerate(sorted_items, 1):
            print(f"[{idx}] {file['path']}")

        try:
            choice = click.prompt("Select an item", default=1)

            if 1 <= choice <= len(sorted_items):
                selected_item = sorted_items[choice - 1]
                if selected_item["name"].endswith(".zip"):
                    self._download_and_unzip_file(
                        normalize_url(
                            f"{self.url}/{self.repository_path}/{selected_item['path']}"
                        ),
                        selected_item["name"],
                    )
                else:
                    self._download_logs_interactive(selected_item["path"])
            else:
                print(
                    "Invalid choice. Please rerun the script and select a number from the list."
                )
                self._download_logs_interactive(path)
        except ValueError:
            print("Invalid input. Please enter a number.")

    def _collect_items(self, url, path=""):
        results = []
        data = self._fetch_directory_contents(normalize_url(f"{url}/{path}"))
        if data is None:
            return results

        for child in data.get("children", []):
            if child["folder"]:
                results.append(
                    {"name": child["uri"][1:] + "/", "path": f"{path}{child['uri']}"}
                )
            elif child["uri"].endswith(".zip"):
                results.append(
                    {"name": child["uri"][1:], "path": f"{path}{child['uri']}"}
                )

        return results

    def _fetch_directory_contents(self, url):
        try:
            response = requests.get(url, auth=self.auth, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to fetch directory contents from {url}: {e}")
            sys.exit(1)

    def _download_file(self, url, local_filename):
        try:
            with requests.get(url, auth=self.auth, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(local_filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return local_filename
        except requests.RequestException as e:
            print(f"Failed to download file from {url}: {e}")
            sys.exit(1)

    def _unzip_file(self, zip_path, extract_to):
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
        except zipfile.BadZipFile as e:
            print(f"Bad zip file {zip_path}: {e}")
