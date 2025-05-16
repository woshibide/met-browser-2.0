# met museum api manager

this directory contains scripts to interact with the metropolitan museum of art's public api, allowing you to search for objects, fetch their information, and download associated images.

## scripts

- `met_api_manager.py`: main script to manage the workflow of searching, fetching object info, and downloading images.
- `get_info.py`: script/module to fetch object information and save it as a csv file.
- `get_images.py`: script/module to download images for objects listed in a csv file.

## requirements

- python 3.7+
- aiohttp

install dependencies:
```
pip install -r requirements.txt
```

## usage

run the manager script from the command line:

```
python met_api_manager.py "search_term" [--geo "geographic_location"] [--info_csv "output.csv"] [--image_dir "images_folder"]
```


```
To fetch stamps from egypt
python met_api_manager.py "stamp" --geo "egypt" --info_csv "stamps_info.csv" --image_dir "stamps"
```

- `search_term`: the term to search for (e.g., horus, stamp, plate)
- `--geo`: (optional) filter by geographic location (e.g., egypt)
- `--info_csv`: (optional) output csv filename (default: `met_object_info.csv`)
- `--image_dir`: (optional) directory to save downloaded images (default: `met_images_downloaded`)

the script will:
1. search for objects matching your criteria that have images.
2. prompt you to fetch and save object information to a csv file.
3. optionally, prompt you to download images for those objects.

## example

```
python met_api_manager.py "cat" --geo "egypt"
```

## notes

- ensure you have network access to reach the met's api.
- image downloads and info fetching may take time depending on the number of objects found.
- all user prompts require a yes/no response.

