import asyncio
import argparse
import os
from get_info import main as get_info_main
from get_images import main as get_images_main
from get_info import search_objects # to get total count
from aiohttp import ClientSession, TCPConnector
import ssl

async def get_total_objects(search_term, geo_location):
    """gets the total number of objects for a given search."""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with ClientSession(connector=TCPConnector(ssl=ssl_context)) as session:
        _, total_objects = await search_objects(session, search_term, geo_location, has_images=True)
        return total_objects

async def manager():
    parser = argparse.ArgumentParser(description="manage met museum api scripts to fetch object info and download images.")
    parser.add_argument("search_term", help="the term to search for (e.g., horus, stamp, plate).")
    parser.add_argument("--geo", help="geographic location (e.g., egypt).", default=None)
    # use none as initial default to allow dynamic naming based on other args
    parser.add_argument("--info_csv", help="filename for the csv output of object information. default: <search_term>[_<geo>]_info.csv", default=None)
    parser.add_argument("--image_dir", help="directory to save downloaded images. default: <search_term>[_<geo>]_images", default=None)
    
    args = parser.parse_args()

    # construct dynamic default names if not provided by user
    base_name_parts = [args.search_term.replace(" ", "_")] # replace spaces for safer filenames
    if args.geo:
        base_name_parts.append(args.geo.replace(" ", "_"))
    base_name = "_".join(base_name_parts)

    if args.info_csv is None:
        args.info_csv = f"{base_name}_info.csv"
    
    if args.image_dir is None:
        args.image_dir = f"{base_name}_images"

    print(f"searching for objects matching term: '{args.search_term}'" + (f" in geo-location: '{args.geo}'" if args.geo else "") + " that have images.")
    
    total_objects_found = await get_total_objects(args.search_term, args.geo)
    
    if total_objects_found > 0:
        print(f"found {total_objects_found} objects matching your criteria.")
        
        # ensure the image directory exists or can be created
        if not os.path.exists(args.image_dir):
            try:
                os.makedirs(args.image_dir)
                print(f"created image directory: {args.image_dir}")
            except OSError as e:
                print(f"error: could not create image directory {args.image_dir}. {e}")
                return
        
        user_prompt = input(f"do you want to fetch information for these {total_objects_found} objects and save to '{args.info_csv}'? (yes/no): ").strip().lower()
        if user_prompt == 'yes':
            print(f"fetching object information for '{args.search_term}'...")
            await get_info_main(args.search_term, args.geo, args.info_csv)
            print(f"object information fetching complete. data saved to {args.info_csv}")

            if os.path.exists(args.info_csv):
                download_prompt = input(f"do you want to download images for the fetched objects into '{args.image_dir}'? (yes/no): ").strip().lower()
                if download_prompt == 'yes':
                    print(f"downloading images to '{args.image_dir}'...")
                    # get_images_main is synchronous, so we run it directly
                    # it needs to be called in a way that asyncio can handle if it were async
                    # for now, assuming it's okay to call directly if it's primarily i/o bound and not cpu bound in a way that blocks asyncio loop
                    # if get_images_main becomes async, it should be awaited.
                    # for simplicity, and given it's mostly requests and file i/o, direct call is fine.
                    # however, to be safe with asyncio, one might run it in a thread pool executor.
                    # for this case, let's assume it's fine or refactor get_images_main to be async if needed.
                    
                    # running synchronous function in a separate thread to avoid blocking asyncio loop
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, get_images_main, args.info_csv, args.image_dir)
                    print("image download process initiated.")
                else:
                    print("image download skipped by user.")
            else:
                print(f"csv file '{args.info_csv}' not found. cannot proceed with image download.")
        else:
            print("fetching object information skipped by user.")
    else:
        print("no objects found matching your criteria. nothing to fetch or download.")

if __name__ == "__main__":
    asyncio.run(manager())
