#!/bin/bash

#########################################################################################
#                                                                                       #   
# This script automates the process of importing data to the Neogranadina's ABC         #
# It transfers the data from dropbox to the server, renames the directories,            #
# and imports the data to CA                                                            #
#                                                                                       #
#########################################################################################

log_error() {
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - $1" >> /var/log/import_errors.log
    echo "[ERROR] $1"
}

FOLDER_NUMBERS=(02 03 04 05 06 07 08 09 10)
DATA_SEGMENTS=(002 003 004 005 006 007 008 009 010)

for i in "${!FOLDER_NUMBERS[@]}"; do
    FOLDER_NAME="MFC_B${FOLDER_NUMBERS[$i]}"
    DATA_SEGMENT="${DATA_SEGMENTS[$i]}"
    
    echo "Processing $FOLDER_NAME with data segment $DATA_SEGMENT"
    
    # step 1: transfer directory to import from dropbox
    if ! rclone copy "dropbox:/Archivos Comunes/Proyectos/Proyecto Istmina/Istmina_EAP/MFC_web/$FOLDER_NAME" /var/www/html/ac/import/$FOLDER_NAME --progress; then
        log_error "Failed to copy from Dropbox for $FOLDER_NAME"
        continue
    fi
    
    # step 2: rename directories
    if ! python3 /home/importHelper/dirRenaming.py --dir-path /var/www/html/ac/import/$FOLDER_NAME; then
        log_error "Failed to rename directories for $FOLDER_NAME"
        rm -rf /var/www/html/ac/import/$FOLDER_NAME
        continue
    fi
    
    # step 3: import data to CA
    if ! /var/www/html/ac/support/bin/caUtils import-data --source /var/www/html/ac/import/AHJCI.MFC.$DATA_SEGMENT.csv --mapping ahjci_mfc --format XLSX --log /var/log/ac_log --log-level DEBUG --add-to-set istmina --log-to-tmp-directory-as-fallback /home/fallback_log; then
        log_error "Failed to import data for $FOLDER_NAME"
        rm -rf /var/www/html/ac/import/$FOLDER_NAME
        continue
    fi
    
    # step 4: import media to CA
    if ! sudo /var/www/html/ac/support/bin/caUtils import-media -u administrator -s /var/www/html/ac/import --include-subdirectories true --match-mode DIRECTORY_NAME --import-mode ALWAYS_MATCH --import-target-idno-mode AUTO --import-target-status 4 --representation-access 1 --remove-media-on-import true -l /var/www/html/ac/import -d INFO --import-target ca_objects --import-target-type Item --log /var/log/ac_log --log-level DEBUG --log-to-tmp-directory-as-fallback /home/fallback_log --import-target-access 1 --representation-idno-mode DIRECTORY_AND_FILENAME; then
        log_error "Failed to import media for $FOLDER_NAME"
        rm -rf /var/www/html/ac/import/$FOLDER_NAME
        continue
    fi
    
    # step 5: remove media folder
    rm -rf /var/www/html/ac/import/$FOLDER_NAME
    
    echo "Successfully completed processing $FOLDER_NAME"
    echo "--------------------------------"
done

echo "All folders have been processed"