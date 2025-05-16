import os
import requests
import csv
import urllib.parse
import time  # for rate limiting

def download_image(image_url, save_path):
    if not os.path.exists(save_path):
        try:  # added try-except for robustness
            response = requests.get(image_url, timeout=10)  # added timeout
            if response.status_code == 200:
                with open(save_path, 'wb') as img_file:
                    img_file.write(response.content)
                print(f"downloaded: {save_path}")
                return True  # indicate success
            else:
                print(f"failed to download image: {image_url}, status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"error downloading {image_url}: {e}")
    else:
        print(f"image already exists: {save_path}")
    return False  # indicate failure or already exists

def download_images_from_csv(csv_filename, download_directory="met_images"):
    if not os.path.exists(download_directory):
        os.makedirs(download_directory)

    downloaded_count = 0
    with open(csv_filename, mode='r', encoding='utf-8') as file:  # specify encoding
        reader = csv.DictReader(file)
        for row in reader:
            object_id = row["Object ID"]
            primary_image_url = row.get("Primary Image URL")
            additional_images_urls = row.get("Additional Images URLs")

            urls_to_download = []
            if primary_image_url:
                urls_to_download.append(primary_image_url)
            if additional_images_urls:
                urls_to_download.extend(additional_images_urls.split(';'))
            
            if not urls_to_download:
                print(f"no image urls found for object id: {object_id}")
                continue

            print(f"processing object id: {object_id}")
            for image_url in urls_to_download:
                if not image_url.strip():  # skip empty urls
                    continue
                try:
                    parsed_url = urllib.parse.urlparse(image_url)
                    image_filename = os.path.basename(parsed_url.path)
                    image_filename = "".join([c for c in image_filename if c.isalnum() or c in ('.', '_', '-')])[:100]
                    save_path = os.path.join(download_directory, f"{object_id}_{image_filename}")
                    if download_image(image_url, save_path):
                        downloaded_count += 1
                        if downloaded_count % 10 == 0:  # respectful api usage: pause after every 10 image downloads
                            print("pausing for 1 second to respect api rate limits...")
                            time.sleep(1)
                except Exception as e:
                    print(f"error processing image url {image_url} for object {object_id}: {e}")
        
        print(f"finished downloading images. total downloaded: {downloaded_count}")

def main(csv_file, image_dir):
    download_images_from_csv(csv_file, image_dir)

if __name__ == "__main__":
    print("this script is intended to be called from met_api_manager.py or with specific parameters.")
