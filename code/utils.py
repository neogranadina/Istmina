import pandas as pd

def join_dates(row):
    start_date = row['start_date']
    end_date = row['end_date']
    
    if pd.isna(end_date) or str(end_date).strip() == '':
        return str(start_date)
    else:
        return f"{str(start_date)} - {str(end_date)}"
