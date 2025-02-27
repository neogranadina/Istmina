import pandas as pd
from pathlib import Path
import utils

from processCollections import process_collections, assign_parent_collection

def sequence_columns(df, mappings_dir=None):
    header = ['seq', 'column_name']
    header_df = pd.DataFrame(columns=header)

    for i, col in enumerate(df.columns):
        header_df.loc[i] = [i + 1, col]

    if not mappings_dir:
        return header_df
    
    mappings_dir = Path(mappings_dir)
    if not mappings_dir.exists():
        raise FileNotFoundError(f"Mappings directory {mappings_dir} does not exist")
    
    mappings_file = mappings_dir / "columns_renaming_mapping.csv"
    
    header_df.to_csv(mappings_file, index=False)
        
    

def process_objects(data_source, save_file_path=None, non_required_columns=None, columns_renaming_mapping=None, split_by_collection=False):
    df = pd.read_csv(data_source, header=1)

    # remove rows 0 and 1
    df = df.iloc[2:]
    
    df = df.rename(columns=columns_renaming_mapping)
    df = df.drop(columns=non_required_columns)
    
    objects = df.loc[df['description_level'] == 'Documento'].copy()

    objects['collection_idno'] = objects['id'].apply(assign_parent_collection)
    
    collections_source = Path(__file__).parent.parent / "data" / "processed" / "collections.csv"
    if not collections_source.exists():
        process_collections(Path(__file__).parent.parent / "data" / "raw" / "AHJCI_MFC.csv", save_file_path=collections_source)

    collections = pd.read_csv(collections_source)
    
    objects_with_collections = objects.merge(collections, on='collection_idno', how='left')
    
    objects_with_collections['date'] = objects_with_collections.apply(utils.join_dates, axis=1)
    
    objects_with_collections = objects_with_collections.drop(columns=['start_date', 'end_date'])
    
    if save_file_path:
        if split_by_collection:
            for collection in objects_with_collections['collection_idno'].unique():
                collection_objects = objects_with_collections[objects_with_collections['collection_idno'] == collection]
                collection_objects.to_csv(save_file_path / f"{collection}.csv", index=False)
        else:
            objects_with_collections.to_csv(save_file_path, index=False)
        
        columns_df = sequence_columns(objects_with_collections, mappings_dir=Path(__file__).parent.parent / "importMappings")
        print(columns_df)
    else:
        print(objects_with_collections.head())

