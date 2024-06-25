import argparse
import os
import shutil
import zipfile

import requests

BASE_API_URL = "https://artifactory.moderne.ninja/ui/api/v1/ui/nativeBrowser/moderne-ingest/io/moderne/ingest-log/" # replace with your artifactory
BASE_FILE_URL = "https://artifactory.moderne.ninja/artifactory/moderne-ingest/" # replace with your artifactory
BASIC_AUTH = ""  # Replace with base64(user:password)


def fetch_directory_contents(url):
    headers = {
        "Authorization": f"Basic {BASIC_AUTH}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to fetch directory contents from {url}: {e}")
        return None


def collect_files(url, files_list):
    data = fetch_directory_contents(url)
    if data is None:
        return

    for child in data.get('children', []):
        if child['folder']:
            # Recurse into subdirectory
            new_path = f"{url}/{child['name']}".replace(BASE_API_URL, '')
            collect_files(BASE_API_URL + new_path, files_list)
        else:
            files_list.append({
                'name': child['name'],
                'lastModified': child['lastModified'],
                'size': child['size'],
                'path': f"{data['path']}/{child['name']}"
            })


def download_file(url, local_filename):
    try:
        with requests.get(url, stream=True) as r:
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


def main():
    parser = argparse.ArgumentParser(description="Download and unzip ingest samples. If no url is provided, it will prompt the user to select a file.", )
    parser.add_argument("--url", help="URL of the file to download")
    args = parser.parse_args()

    if args.url:
        download_and_unzip_file(args.url, 'ingest.zip')
    else:
        download_logs_interactive()


def download_logs_interactive():
    collected_files = []
    collect_files(BASE_API_URL, collected_files)
    sorted_files = sorted(collected_files, key=lambda x: x['lastModified'], reverse=True)[:20]

    if not sorted_files:
        print("No files found to download.")
        return

    for idx, file in enumerate(sorted_files, 1):
        print(f"[{idx}] {file['path']}")

    try:
        choice = int(input("Choose a file to download: "))
        if 1 <= choice <= len(sorted_files):
            selected_file = sorted_files[choice - 1]
            download_and_unzip_file(BASE_FILE_URL + selected_file['path'], selected_file['name'])
        else:
            print("Invalid choice. Please rerun the script and select a number from the list.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def download_and_unzip_file(url, file_name):
    local_filename = download_file(url, file_name)
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


if __name__ == '__main__':
    main()
