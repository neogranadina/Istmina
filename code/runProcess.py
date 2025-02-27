from processObjects import process_objects
from pathlib import Path

columns_renaming_mapping = {
    'Identificador': 'id',
    'Tu nombre (persona encargada de la catalogación)': 'cataloger',
    'Nombre de carpeta digital': 'digital_folder',
    'Nombre de archivo digital (primero)': 'digital_file_1',
    'Nombre de archivo digital (segundo)': 'digital_file_2',
    'Número de imágenes': 'image_count',
    'Nivel de descripción': 'description_level',
    'Volumen y soporte': 'volume_support',
    'Título del documento': 'document_title',
    'Referencia original de archivo físico': 'physical_reference',
    'Fecha de inicio del proceso legal': 'start_date',
    'Fecha final': 'end_date',
    'Lugares mencionados (Pueblos, regiones, paises, ríos, quebradas, cerros, minas, fincas y otros referentes geográficos)': 'locations_mentioned',
    'Nombres de personas mencionadas': 'people_mentioned',
    'Nombres de instituciones mencionadas': 'institutions_mentioned',
    'Temas relacionados': 'related_topics',
    'Descripcion breve del documento: ¿Sobre que es?': 'document_summary',
    'Problemas para resolver (documento físico)': 'physical_issues',
    'Problemas para resolver (digitalización)': 'digitization_issues',
    'Observaciones de catalogación': 'cataloging_notes',
    'Fecha de revisión': 'review_date'
}

non_required_columns = ['digital_file_1', 'digital_file_2', 'image_count']

save_file_path = Path(__file__).parent.parent / "data" / "processed"

process_objects(Path(__file__).parent.parent / "data" / "raw" / "AHJCI_MFC.csv", 
                save_file_path=save_file_path, 
                columns_renaming_mapping=columns_renaming_mapping, 
                non_required_columns=non_required_columns, 
                split_by_collection=True)

