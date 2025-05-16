# this is a python based script that will generate index.html file with egyptian gallery

import os
import csv
import json
import re
from pathlib import Path

# define constants
BASE_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BASE_DIR / 'content'
TEMPLATE_DIR = BASE_DIR / 'builder' / 'templates'
OUTPUT_FILE = BASE_DIR / 'index.html'

def load_csv_data():
    """
    loads all csv files from content directory
    """
    data_by_category = {}
    
    # find all csv files in content dir
    csv_files = [f for f in os.listdir(CONTENT_DIR) if f.endswith('_info.csv')]
    
    for csv_file in csv_files:
        category = csv_file.replace('_info.csv', '')
        data_by_category[category] = []
        
        with open(CONTENT_DIR / csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # convert image urls to webp filenames
                image_files = []
                
                if row.get('Primary Image URL'):
                    primary_img = os.path.basename(row['Primary Image URL'])
                    primary_img = os.path.splitext(primary_img)[0] + '.webp'
                    image_files.append(primary_img)
                
                if row.get('Additional Images URLs'):
                    additional_imgs = row['Additional Images URLs'].split(';')
                    for img_url in additional_imgs:
                        if img_url:
                            img = os.path.basename(img_url)
                            img = os.path.splitext(img)[0] + '.webp'
                            image_files.append(img)
                
                # build item data object
                item = {
                    'object_id': row.get('Object ID', ''),
                    'title': row.get('Title', ''),
                    'date': row.get('Date', ''),
                    'materials': row.get('Materials', ''),
                    'culture': row.get('Culture', ''),
                    'place': row.get('Place', ''),
                    'department': row.get('Department', ''),
                    'object_name': row.get('Object Name', ''),
                    'measurements': row.get('Measurements', ''),
                    'classification': row.get('Classification', ''),
                    'category': category,
                    'images': image_files
                }
                
                data_by_category[category].append(item)
    
    return data_by_category

def generate_gallery_html(data_by_category):
    """
    generates html for the gallery view
    """
    # create container for gallery
    gallery_html = '''
    <div class="egypt-gallery">
        <div class="gallery-view">
            <div class="image-container"></div>
            <div class="nav-controls">
                <div class="nav-left">&lt;</div>
                <div class="nav-right">&gt;</div>
            </div>
        </div>
        <div class="info-panel">
            <div class="item-info"></div>
            <div class="category-selector"></div>
        </div>
    </div>
    
    <script>
    // gallery data
    const galleryData = ${GALLERY_DATA};
    
    // initialize gallery
    document.addEventListener('DOMContentLoaded', function() {
        // state variables
        let currentCategory = Object.keys(galleryData)[0];
        let currentItemIndex = 0;
        let currentImageIndex = 0;
        
        // dom elements
        const imageContainer = document.querySelector('.image-container');
        const itemInfoPanel = document.querySelector('.item-info');
        const categorySelector = document.querySelector('.category-selector');
        const navLeft = document.querySelector('.nav-left');
        const navRight = document.querySelector('.nav-right');
        
        // initialize category selector
        function initCategorySelector() {
            let html = '<div class="category-label">category:</div>';
            Object.keys(galleryData).forEach(category => {
                html += `<div class="category-item" data-category="${category}">${category}</div>`;
            });
            categorySelector.innerHTML = html;
            
            // add event listeners to category items
            document.querySelectorAll('.category-item').forEach(item => {
                item.addEventListener('click', function() {
                    const category = this.getAttribute('data-category');
                    changeCategory(category);
                });
            });
            
            // highlight current category
            updateCategoryHighlight();
        }
        
        // update category highlight
        function updateCategoryHighlight() {
            document.querySelectorAll('.category-item').forEach(item => {
                if (item.getAttribute('data-category') === currentCategory) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
        }
        
        // change category
        function changeCategory(category) {
            if (galleryData[category] && galleryData[category].length > 0) {
                currentCategory = category;
                currentItemIndex = 0;
                currentImageIndex = 0;
                updateCategoryHighlight();
                displayCurrentItem();
            }
        }
        
        // display current item
        function displayCurrentItem() {
            const items = galleryData[currentCategory];
            if (items.length === 0) return;
            
            const item = items[currentItemIndex];
            
            // display image
            if (item.images.length > 0) {
                const imgPath = `content/${currentCategory}_images/${item.object_id}_${item.images[currentImageIndex]}`;
                imageContainer.innerHTML = `<img src="${imgPath}" alt="${item.title}">`;
            } else {
                imageContainer.innerHTML = '<div class="no-image">No image available</div>';
            }
            
            // display info
            let infoHtml = `
                <h2>${item.title}</h2>
                <p class="object-id">ID: ${item.object_id}</p>
                <p>${item.date}</p>
                <p>${item.materials}</p>
                <p>${item.object_name}</p>
                <p>${item.place}</p>
                <p class="image-counter">${currentImageIndex + 1}/${item.images.length}</p>
            `;
            itemInfoPanel.innerHTML = infoHtml;
        }
        
        // next image
        function nextImage() {
            const item = galleryData[currentCategory][currentItemIndex];
            if (item.images.length === 0) return;
            
            currentImageIndex = (currentImageIndex + 1) % item.images.length;
            displayCurrentItem();
        }
        
        // previous image
        function prevImage() {
            const item = galleryData[currentCategory][currentItemIndex];
            if (item.images.length === 0) return;
            
            currentImageIndex = (currentImageIndex - 1 + item.images.length) % item.images.length;
            displayCurrentItem();
        }
        
        // next item
        function nextItem() {
            const items = galleryData[currentCategory];
            currentItemIndex = (currentItemIndex + 1) % items.length;
            currentImageIndex = 0;
            displayCurrentItem();
        }
        
        // previous item
        function prevItem() {
            const items = galleryData[currentCategory];
            currentItemIndex = (currentItemIndex - 1 + items.length) % items.length;
            currentImageIndex = 0;
            displayCurrentItem();
        }
        
        // initialize navigation
        navLeft.addEventListener('click', prevImage);
        navRight.addEventListener('click', nextImage);
        
        // enable keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft') {
                prevImage();
            } else if (e.key === 'ArrowRight') {
                nextImage();
            } else if (e.key === 'ArrowUp') {
                prevItem();
            } else if (e.key === 'ArrowDown') {
                nextItem();
            }
        });
        
        // initialize gallery
        initCategorySelector();
        displayCurrentItem();
    });
    </script>
    '''
    
    # convert data to json for embedding in javascript
    gallery_data_json = json.dumps(data_by_category)
    gallery_html = gallery_html.replace('${GALLERY_DATA}', gallery_data_json)
    
    return gallery_html

def generate_css():
    """
    generates css for the gallery
    """
    return '''
    <style>
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            font-family: Arial, sans-serif;
            overflow: hidden;
        }
        
        .egypt-gallery {
            position: relative;
            width: 100vw;
            height: 100vh;
            background-color: #000;
            color: #fff;
        }
        
        .gallery-view {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }
        
        .image-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .image-container img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }
        
        .nav-controls {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: space-between;
            pointer-events: none;
        }
        
        .nav-left, .nav-right {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 60px;
            height: 100%;
            font-size: 2rem;
            color: rgba(255, 255, 255, 0.6);
            cursor: pointer;
            pointer-events: auto;
        }
        
        .nav-left:hover, .nav-right:hover {
            color: rgba(255, 255, 255, 0.9);
            background-color: rgba(0, 0, 0, 0.3);
        }
        
        .info-panel {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            display: flex;
            justify-content: space-between;
            background-color: rgba(0, 0, 0, 0.7);
            z-index: 2;
        }
        
        .item-info {
            padding: 20px;
            max-width: 60%;
        }
        
        .item-info h2 {
            margin: 0 0 10px 0;
            font-size: 1.5rem;
        }
        
        .item-info p {
            margin: 5px 0;
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .object-id {
            font-size: 0.8rem !important;
            opacity: 0.5 !important;
        }
        
        .image-counter {
            font-size: 0.8rem !important;
            opacity: 0.7 !important;
            margin-top: 15px !important;
        }
        
        .category-selector {
            display: flex;
            flex-wrap: wrap;
            padding: 20px;
            align-items: flex-start;
            align-content: flex-start;
            max-width: 40%;
        }
        
        .category-label {
            width: 100%;
            font-size: 0.8rem;
            opacity: 0.6;
            margin-bottom: 10px;
        }
        
        .category-item {
            margin: 5px;
            padding: 5px 10px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            font-size: 0.8rem;
            cursor: pointer;
        }
        
        .category-item:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        .category-item.active {
            background-color: rgba(255, 255, 255, 0.3);
        }
        
        .no-image {
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
        }
    </style>
    '''

def generate_html(data_by_category):
    """
    generates the complete html page
    """
    # read template
    with open(TEMPLATE_DIR / 'template-home.html', 'r', encoding='utf-8') as f:
        template = f.read()
    
    # generate gallery
    gallery_html = generate_gallery_html(data_by_category)
    
    # generate css
    css = generate_css()
    
    # replace placeholders in template
    output_html = template
    
    # add title
    output_html = output_html.replace('<title>Document</title>', '<title>египетская коллаба</title>')
    
    # add css to head
    head_end_tag = '</head>'
    output_html = output_html.replace(head_end_tag, f'{css}\n{head_end_tag}')
    
    # insert gallery
    output_html = output_html.replace('<!-- this is a html file template that will be used to generate index.html -->', gallery_html)
    
    return output_html

def main():
    """
    main function to run the builder
    """
    print("Starting Egypt Gallery Builder...")
    
    # load data from csv files
    print("Loading data from CSV files...")
    data_by_category = load_csv_data()
    
    # generate html
    print("Generating HTML...")
    output_html = generate_html(data_by_category)
    
    # write output
    print(f"Writing output to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(output_html)
    
    print("Egypt Gallery Builder completed successfully!")

if __name__ == "__main__":
    main()