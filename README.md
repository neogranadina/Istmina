# Istmina Data Processing

This repository contains the code and data used to process materials from the project "[Stabilising and digitising 19th- and 20th-century materials now in precarious condition at the Circuit Court of Istmina, Chocó (EAP1477)](https://eap.bl.uk/project/EAP1477)" for incorporation into Neogranadina's [ABC](https://abcng.org/Detail/collections/16479).

Details about the project can be found [here](https://neogranadina.org/proyectos/istmina).

## Data

The data folder contains the following structure:

```
data/
├── raw/
│   ├── acc_import_v21.xslx # Original excel file provided by project collaborators
│   ├── AHJCI_MFC.csv # CSV version of the original excel file
├── processed/
│   ├── collections.csv # Collections-like structured data that replicates the archive structure
│   ├── objects.csv # All data prepared for import
│   ├── AHJCI.MFC.*.csv # Object level data segmented by collection
```

## Code

Code folder contains the following files:

```
code/
├── imageProcessing.py # Python script to reduce the size of images in the cloud and upload them without using local storage
├── processCollections.py # Python script to process the collections
├── processObjects.py # Python script to process the objects
├── runProcess.py # Script to handle the mapping and control the processing
├── utils.py # Utility functions
```

## Mappings

The importMappings folder contains the mapping files required for the Collective Access - Providence platform to import the data:

```
importMappings/
├── collections.csv # Mapping for the collections
├── objects.csv # Mapping for the objects
├── columns_renaming_mapping.csv # Dictionary with column numbers and source column names
```

## How to Replicate the Process

### Prerequisites

- Python 3.10+
- pip
- rclone
- Cloud storage account with access to the project's data

### Steps

1. Clone the repository

```
git clone https://github.com/neogranadina/Istmina.git
```

2. Create a virtual environment and install the dependencies

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure the config.conf file with the following variables:

```
[dropbox]
path = path/to/remote/dropbox/folder
path_safe = path/to/remote/safe/folder
```

4. Run the script

```
python runProcess.py
```

### Recommendations

- This code was tested on a Linux environment. It might need adjustments for Windows.
- The process of reducing image sizes can be time-consuming. It's recommended to run it inside a `tmux` session to avoid interruptions, or preferably on a server.

## License

This project is licensed under the [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) license.


## Contact

For any questions or feedback, please open an issue in the repository.
