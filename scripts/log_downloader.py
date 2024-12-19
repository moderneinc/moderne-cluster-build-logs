import os
import zipfile

import requests
from utils import prepare_directory


class LogDownloader:
    def __init__(self, url, repository_path, log_file, username, password, output_dir):
        self.url = url
        self.repository_path = repository_path
        self.log_file = log_file
        self.auth = (username, password) if username is not None else None
        self.output_dir = output_dir

    def download_logs(self):
        if self.log_file:
            self.download_and_unzip_file(
                f"{self.url}/{self.repository_path}/{self.log_file}", "ingest.zip"
            )
        else:
            self.download_logs_interactive(".", self.output_dir)

    def download_and_unzip_file(self, url, file_name):
        local_filename = self.download_file(url, file_name)
        if not local_filename:
            return

        # Prepare extraction directory
        extract_to = self.output_dir
        prepare_directory(extract_to)

        self.unzip_file(local_filename, extract_to)

        # Count files in repos
        file_count = len(
            [
                name
                for name in os.listdir(extract_to)
                if os.path.isfile(os.path.join(extract_to, name))
            ]
        )
        print(
            f"Extracted {file_count} file{'s' if file_count != 1 else ''} to {extract_to}"
        )

        # Remove downloaded zip file
        os.remove(local_filename)

    def download_logs_interactive(self, path, output_dir):
        print(
            f"Fetching files from {self.url}/api/storage/{self.repository_path}/{path}"
        )
        items = self.collect_items(
            f"{self.url}/api/storage/{self.repository_path}", path
        )
        sorted_items = sorted(items, key=lambda x: x["name"])[:20]

        if not sorted_items:
            print("No files found to download.")
            return

        if len(sorted_items) == 1:
            selected_item = sorted_items[0]
            if selected_item["name"].endswith(".zip"):
                self.download_and_unzip_file(
                    f"{self.url}/{self.repository_path}/{selected_item['path']}",
                    selected_item["name"],
                )
                return
            else:
                self.download_logs_interactive(selected_item["path"], output_dir)
                return

        for idx, file in enumerate(sorted_items, 1):
            print(f"[{idx}] {file['path']}")

        try:
            choice = int(input("Select an item: "))
            if 1 <= choice <= len(sorted_items):
                selected_item = sorted_items[choice - 1]
                if selected_item["name"].endswith(".zip"):
                    self.download_and_unzip_file(
                        f"{self.url}/{self.repository_path}/{selected_item['path']}",
                        selected_item["name"],
                    )
                else:
                    self.download_logs_interactive(selected_item["path"], output_dir)
            else:
                print(
                    "Invalid choice. Please rerun the script and select a number from the list."
                )
        except ValueError:
            print("Invalid input. Please enter a number.")

    def collect_items(self, url, path):
        results = []
        data = self.fetch_directory_contents(f"{url}/{path}")
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

    def fetch_directory_contents(self, url):
        try:
            response = requests.get(url, auth=self.auth, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to fetch directory contents from {url}: {e}")
            return None

    def download_file(self, url, local_filename):
        try:
            with requests.get(url, auth=self.auth, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(local_filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return local_filename
        except requests.RequestException as e:
            print(f"Failed to download file from {url}: {e}")
            return None

    def unzip_file(self, zip_path, extract_to):
        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)
        except zipfile.BadZipFile as e:
            print(f"Bad zip file {zip_path}: {e}")
