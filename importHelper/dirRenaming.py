import re
import logging
import argparse
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def setup_logging(log_file: str) -> None:
    """
    Set up logging to a file and the console.
    Args:
        log_file (str): The path to the log file.
    """
    logger.handlers.clear()
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def rename_dir(origin: str) -> str:
    """
    Rename a directory based on its name.
    Args:
        origin (str): The original directory name.
    Returns:
        str: The new directory name.
    """
    try:
        elements = origin.split("_")
        if len(elements) < 4:
            raise ValueError(f"Invalid directory name format: {origin}")
            
        box = elements[2].replace("B", "").zfill(3)
        doc = elements[3].replace("Doc", "").zfill(3)
        
        return f"AHJCI.MFC.{box}.{doc}"
    except Exception as e:
        logger.error(f"Error processing directory name {origin}: {str(e)}")
        return origin

def rename_dir_in_dir(dir_path: str, dry_run: bool = False) -> None:
    """
    Rename all directories in a given directory path based on their name.
    Args:
        dir_path (str): The path to the directory to process.
        dry_run (bool): Whether to show what would be renamed without making any changes.
    Returns:
        None
    """
    try:
        dir_path = Path(dir_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {dir_path}")
            
        for path in dir_path.iterdir():
            if path.is_dir():
                rename_dir_in_dir(str(path), dry_run)
                
                if re.match(r'EAP\d+_MFC_B\d+_Doc\d+.*', path.name):
                    new_name = rename_dir(path.name)
                    if new_name != path.name:
                        try:
                            new_path = path.parent / new_name
                            if new_path.exists():
                                logger.warning(f"Target directory already exists: {new_path}")
                                continue
                            
                            if dry_run:
                                logger.info(f"[DRY RUN] Would rename: {path.name} -> {new_name}")
                            else:
                                path.rename(new_path)
                                logger.info(f"Renamed directory: {path.name} -> {new_name}")
                        except Exception as e:
                            logger.error(f"Error renaming directory {path}: {str(e)}")
                else:
                    logger.warning(f"Skipping directory with invalid format: {path.name}")
                        
    except Exception as e:
        logger.error(f"Error processing directory {dir_path}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rename directories following a specific pattern')
    parser.add_argument('--dry-run', action='store_true', 
                        help='Show what would be renamed without making any changes')
    parser.add_argument('--log-file', type=str,
                        default=f'rename_dirs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
                        help='Path to the log file')
    parser.add_argument('--dir-path', type=str,
                        default="/var/www/html/ac/import/",
                        help='Path to the directory to process')
    
    args = parser.parse_args()
    
    setup_logging(args.log_file)
    
    logger.info(f"Starting directory rename operation")
    logger.info(f"Dry run: {args.dry_run}")
    logger.info(f"Target directory: {args.dir_path}")
    
    rename_dir_in_dir(args.dir_path, args.dry_run)
    
    logger.info("Directory rename operation completed")
