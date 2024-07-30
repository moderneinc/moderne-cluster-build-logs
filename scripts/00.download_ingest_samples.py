import argparse
import os
import shutil
import zipfile

import requests


def env(key, default=None):
    if key in os.environ:
        return os.environ[key]
    return default


def main():
    parser = argparse.ArgumentParser(description="Download and unzip ingest samples. If no url is provided, it will prompt the user to select a file.", )
    parser.add_argument("--url", default=env("ARTIFACTORY_URL", "https://artifactory.moderne.ninja/artifactory"), help="The Artifactory URL")
    parser.add_argument("--repo-key", default="moderne-ingest", help="The Artifactory repository key")
    parser.add_argument("--file", help="The path of the file to download")
    parser.add_argument("--username", default=env("ARTIFACTORY_USER"), help="The Artifactory user")
    parser.add_argument("--password", default=env("ARTIFACTORY_PASSWORD"), help="The Artifactory password")
    args = parser.parse_args()

    auth = (args.username, args.password) if args.username is not None else None
    if args.file:
        download_and_unzip_file(f"{args.url}/{args.repo_key}/{args.file}", auth, 'ingest.zip')
    else:
        download_logs_interactive(args.url, args.repo_key, auth, "io/moderne/ingest-log")


def download_and_unzip_file(url, auth, file_name):
    local_filename = download_file(url, auth, file_name)
    if not local_filename:
        return

    # Prepare extraction directory
    extract_to = 'repos'
    prepare_directory(extract_to)

    unzip_file(local_filename, extract_to)

    # Count files in repos
    file_count = len([name for name in os.listdir(extract_to) if os.path.isfile(os.path.join(extract_to, name))])
    print(f"Extracted {file_count} files to {extract_to}")

    # Remove downloaded zip file
    os.remove(local_filename)


def download_logs_interactive(url, repo_key, auth, path):
    items = collect_items(f"{url}/api/storage/{repo_key}", auth, path)
    sorted_items = sorted(items, key=lambda x: x['name'])[:20]

    if not sorted_items:
        print("No files found to download.")
        return

    for idx, file in enumerate(sorted_items, 1):
        print(f"[{idx}] {file['path']}")

    try:
        choice = int(input("Select an item: "))
        if 1 <= choice <= len(sorted_items):
            selected_item = sorted_items[choice - 1]
            if selected_item['name'].endswith(".zip"):
                download_and_unzip_file(f"{url}/{repo_key}/{selected_item['path']}", auth, selected_item['name'])
            else:
                download_logs_interactive(url, repo_key, auth, selected_item['path'])
        else:
            print("Invalid choice. Please rerun the script and select a number from the list.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def collect_items(url, auth, path):
    results = []
    data = fetch_directory_contents(f"{url}/{path}?list&listFolders=1", auth)
    if data is None:
        return results

    for child in data.get('files', []):
        if child['folder']:
            results.append({
                'name': child['uri'][1:] + "/",
                'lastModified': child['lastModified'],
                'size': child['size'],
                'path': f"{path}{child['uri']}"
            })
        elif child['uri'].endswith(".zip"):
            results.append({
                'name': child['uri'][1:],
                'lastModified': child['lastModified'],
                'size': child['size'],
                'path': f"{path}{child['uri']}"
            })

    return results


def fetch_directory_contents(url, auth):
    try:
        response = requests.get(url, auth=auth)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch directory contents from {url}: {e}")
        return None


def download_file(url, auth, local_filename):
    try:
        with requests.get(url, auth=auth, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_filename
    except requests.RequestException as e:
        print(f"Failed to download file from {url}: {e}")
        return None


def unzip_file(zip_path, extract_to):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    except zipfile.BadZipFile as e:
        print(f"Bad zip file {zip_path}: {e}")


def prepare_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)


if __name__ == "__main__":
    main()