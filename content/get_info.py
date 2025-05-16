import requests
import csv
import pandas as pd
import asyncio
import aiohttp
import ssl
from aiohttp import ClientSession, TCPConnector
import time
import urllib.parse

async def search_objects(session, search_term, geo_location=None, has_images=True):
    base_url = "https://collectionapi.metmuseum.org/public/collection/v1/search"
    params = {'q': search_term, 'hasImages': str(has_images).lower()}
    if geo_location:
        params['geoLocation'] = geo_location
    
    query_string = urllib.parse.urlencode(params)
    search_url = f"{base_url}?{query_string}"
    
    print(f"Searching with URL: {search_url}")
    try:
        async with session.get(search_url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('objectIDs', []), data.get('total', 0)
            else:
                print(f"Error searching objects: {response.status} - {await response.text()}")
                return [], 0
    except Exception as e:
        print(f"Exception during search: {e}")
        return [], 0

async def get_object_details(session, object_id):
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        print(f"Failed to get details for object ID {object_id}: status {response.status}")
        return None

async def fetch_and_save_object_info(object_ids, output_csv="object_info.csv"):
    data = []
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        for i in range(0, len(object_ids), 50):
            batch = object_ids[i:i + 50]
            tasks = [get_object_details(session, object_id) for object_id in batch]
            responses = await asyncio.gather(*tasks)

            for object_info in responses:
                if object_info and (object_info.get('primaryImage') or object_info.get('additionalImages')):
                    title = object_info.get('title', 'No title')
                    object_date = object_info.get('objectDate', 'No date')
                    materials = object_info.get('medium', 'Unknown')
                    culture = object_info.get('culture', 'Unknown')
                    primary_image_url = object_info.get('primaryImage', '')
                    additional_images_urls = ';'.join(object_info.get('additionalImages', []))
                    total_images = 1 if primary_image_url else 0
                    total_images += len(object_info.get('additionalImages', []))
                    place = "Origin unknown"
                    if object_info.get('country', '').strip():
                        place = object_info['country']
                    elif object_info.get('region', '').strip():
                        place = object_info['region']
                    elif object_info.get('period', '').strip():
                        place = object_info['period']
                    department = object_info.get('department', 'Unknown')
                    object_name = object_info.get('objectName', 'Unknown')
                    measurements_raw = object_info.get('measurements')
                    measurements_str = str(measurements_raw) if measurements_raw else 'Unknown'
                    classification = object_info.get('classification', 'Unknown')

                    data.append({
                        "Object ID": object_info['objectID'],
                        "Title": title,
                        "Date": object_date,
                        "Materials": materials,
                        "Culture": culture,
                        "Place": place,
                        "Department": department,
                        "Object Name": object_name,
                        "Measurements": measurements_str,
                        "Classification": classification,
                        "Total Images": total_images,
                        "Primary Image URL": primary_image_url,
                        "Additional Images URLs": additional_images_urls
                    })

            print(f"Processed batch {i // 50 + 1} of {(len(object_ids) - 1) // 50 + 1}")
            await asyncio.sleep(1)

    if not data:
        print("No data to save to CSV.")
        return
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f"Object information saved to {output_csv}")

async def main(search_term, geo_location=None, output_csv="object_info.csv"):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        object_ids, total_objects = await search_objects(session, search_term, geo_location)
        if total_objects > 0 and object_ids:
            print(f"Found {total_objects} objects. Fetching details for {len(object_ids)} object IDs.")
            await fetch_and_save_object_info(object_ids, output_csv)
        else:
            print("No objects found matching your criteria.")

if __name__ == "__main__":
    print("This script is intended to be called from met_api_manager.py or with specific parameters.")
