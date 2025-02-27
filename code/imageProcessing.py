import os
import subprocess
from PIL import Image
import configparser
import logging
from datetime import datetime
import json
import time

config = configparser.ConfigParser()
config.read('config.conf')

rclone_log_file = "logs/rclone.log"

source_folder = config['dropbox']['path']
destination_folder = config['dropbox']['path_safe']

def get_folder_structure(source_folder, cache_file="folder_cache.json", cache_ttl=3600):
    """Get folder structure from Dropbox or cache if available and not expired"""
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
            if time.time() - cache_data['timestamp'] < cache_ttl:
                logging.info("Using cached folder structure")
                return cache_data['structure']
    
    logging.info("Building folder structure from Dropbox")
    structure = {}
    
    try:
        # Get main folders (MFC_B01, MFC_B02, etc.)
        result = subprocess.run(
            ["rclone", "lsd", f"dropbox:{source_folder}", "--log-file", rclone_log_file, 
             "--log-level", "INFO"],
            capture_output=True, text=True, check=True
        )
        main_folders = [line.split()[-1] for line in result.stdout.strip().split("\n") if line]
        
        for main_folder in main_folders:
            structure[main_folder] = {}
            
            # Get document folders (EAP1477_MFC_B01_Doc01_HurtadovsCastillo, etc.)
            result = subprocess.run(
                ["rclone", "lsd", f"dropbox:{source_folder}/{main_folder}",
                 "--log-file", rclone_log_file, "--log-level", "INFO"],
                capture_output=True, text=True, check=True
            )
            doc_folders = [line.split()[-1] for line in result.stdout.strip().split("\n") if line]
            
            for doc_folder in doc_folders:
                # Get TIFF files in document folder
                result = subprocess.run(
                    ["rclone", "lsf", f"dropbox:{source_folder}/{main_folder}/{doc_folder}", 
                     "--files-only", "--include", "*.tif", "--log-file", rclone_log_file, 
                     "--log-level", "INFO"],
                    capture_output=True, text=True, check=True
                )
                files = [f for f in result.stdout.strip().split("\n") if f]
                if files:  # Only add folders that contain TIFF files
                    structure[main_folder][doc_folder] = files
        
        # Save to cache
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'structure': structure
            }, f)
        
        return structure
        
    except subprocess.CalledProcessError as e:
        logging.error(f"Error building folder structure: {e}")
        return None

def process_images(source_folder, destination_folder, temp_folder="/tmp/imgs", dry_run=False, cache_ttl=3600):
    """Process images from source to destination, maintaining folder structure"""
    logging.info(f"Starting image processing job with source: {source_folder}")
    logging.info(f"Destination: {destination_folder}")
    logging.info(f"Dry run: {dry_run}")

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
        logging.info(f"Created temporary folder: {temp_folder}")
    
    folder_structure = get_folder_structure(source_folder, cache_ttl=cache_ttl)
    if not folder_structure:
        logging.error("Failed to get folder structure")
        return
    
    logging.info(f"Found {len(folder_structure)} main folders")
    
    for main_folder, doc_folders in folder_structure.items():
        logging.info(f"Processing main folder: {main_folder}")
        logging.info(f"Found {len(doc_folders)} document folders")
        
        main_folder_path = f"{destination_folder}/{main_folder}"
        if dry_run:
            logging.info(f"[DRY RUN] Would create directory: {main_folder_path}")
        else:
            logging.info(f"Creating directory: {main_folder_path}")
            subprocess.run(["rclone", "mkdir", f"dropbox:{main_folder_path}"], check=True)
            
        for doc_folder, files in doc_folders.items():
            logging.info(f"Processing document folder: {doc_folder}")
            logging.info(f"Found {len(files)} TIFF files")
            
            doc_folder_path = f"{main_folder_path}/{doc_folder}"
            if dry_run:
                logging.info(f"[DRY RUN] Would create directory: {doc_folder_path}")
            else:
                logging.info(f"Creating directory: {doc_folder_path}")
                subprocess.run(["rclone", "mkdir", f"dropbox:{doc_folder_path}"], check=True)
            
            for tiff_file in files:
                source_path = f"{source_folder}/{main_folder}/{doc_folder}/{tiff_file}"
                jpg_file = tiff_file.replace('.tif', '.jpg').replace('.tiff', '.jpg')
                dest_path = f"{doc_folder_path}" 
                
                if dry_run:
                    logging.info(f"[DRY RUN] Would process: {source_path}")
                    logging.info(f"[DRY RUN] Would save to: {dest_path}/{jpg_file}")
                    continue
                
                try:
                    # Download TIFF file
                    logging.info(f"Downloading: {source_path}")
                    temp_tiff = os.path.join(temp_folder, tiff_file)
                    subprocess.run(
                        ["rclone", "copy", f"dropbox:{source_path}", temp_folder],
                        check=True
                    )
                    
                    # Convert to JPG
                    if os.path.exists(temp_tiff):
                        logging.info(f"Converting {tiff_file} to JPEG")
                        temp_jpg = os.path.join(temp_folder, jpg_file)
                        with Image.open(temp_tiff) as img:
                            img.convert('RGB').save(temp_jpg, 'JPEG', quality=85)
                        
                        # Upload JPG
                        logging.info(f"Uploading: {dest_path}/{jpg_file}")
                        subprocess.run(
                            ["rclone", "copy", temp_jpg, f"dropbox:{dest_path}"],
                            check=True
                        )
                        
                        # Clean up temp files
                        os.remove(temp_tiff)
                        os.remove(temp_jpg)
                        logging.info(f"Processed {tiff_file} successfully")
                    else:
                        logging.error(f"Failed to download {tiff_file}")
                        
                except Exception as e:
                    logging.error(f"Error processing {tiff_file}: {e}")
                    continue
    
    if not dry_run:
        try:
            os.rmdir(temp_folder)
            logging.info("Removed temporary folder")
        except Exception as e:
            logging.error(f"Error removing temporary folder: {e}")

    logging.info("Image processing job completed")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/processing.log'),
            logging.StreamHandler() 
        ]
    )
    
    process_images(source_folder, destination_folder, dry_run=False)
