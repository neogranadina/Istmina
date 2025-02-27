import pandas as pd
from pathlib import Path
import utils

def assign_parent_collection(collection_id):
    parent_id = collection_id.split('.')[:-1]
    parent_id = '.'.join(parent_id)
    return parent_id


def process_collections(data_source, saveExcel=False, save_file_path=None):
    df = pd.read_csv(data_source, header=1)

    # remove rows 0 and 1
    df = df.iloc[2:]

    collections = df.loc[df['Nivel de descripción'] != 'Documento']

    useful_columns = ['Identificador', 'Título del documento', 'Fecha de inicio del proceso legal', 'Fecha final', 'Descripcion breve del documento: ¿Sobre que es?']

    renamed_columns = {
        'Identificador': 'collection_idno',
        'Título del documento': 'collection_title',
        'Fecha de inicio del proceso legal': 'start_date',
        'Fecha final': 'end_date',
        'Descripcion breve del documento: ¿Sobre que es?': 'collection_description'
    }

    collections = collections[useful_columns]

    collections = collections.rename(columns=renamed_columns)

    # join start_date and end_date
    collections['collection_date'] = collections.apply(utils.join_dates, axis=1)

    # remove start_date and end_date
    collections = collections.drop(columns=['start_date', 'end_date'])

    collections['parent_collection'] = collections['collection_idno'].apply(assign_parent_collection)

    # reorder columns
    collections = collections[['collection_idno', 'parent_collection', 'collection_title', 'collection_description', 'collection_date']]

    collections.to_csv(save_file_path, index=False)
    
    if saveExcel:
        collections.to_excel(save_file_path.with_suffix('.xlsx'), index=False)

if __name__ == "__main__":
    process_collections(Path(__file__).parent.parent / "data" / "raw" / "AHJCI_MFC.csv", saveExcel=True)
