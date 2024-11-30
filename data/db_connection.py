from sqlalchemy import create_engine
import pandas as pd
import io

def write_to_db(file):
    engine = create_engine(
        'postgresql+psycopg2://postgres:1dunSG7x@localhost:5432/energy')
    
    df_energy = pd.read_csv(file)
    
    # Drop old table and create new empty table
    print('Drop table from database and create a new empty table...')
    df_energy.head(0).to_sql('energy_balance', engine, if_exists='replace',index=False)    
    conn = engine.raw_connection()
    cur = conn.cursor()
    output = io.StringIO()
    print('Load data from csv...')
    df_energy.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    #contents = output.getvalue()
    cur.copy_from(output, 'energy_balance', null="") # null values become ''
    print('New data was push to the database...')
    conn.commit()
    cur.close()
    conn.close()