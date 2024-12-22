import psycopg2
import pandas as pd

def fetch_data():
    database = {'user': '',
                'pass': '',
                'name': '',
                'host': '',
                'port': ''}

    pgConnectString = f"""host={database['host']}
    port={database['port']}
    dbname={database['name']}
    user={database['user']}
    password={database['pass']}"""

    # Connect to the PostgreSQL database
    pgConnection=psycopg2.connect(pgConnectString)

    # SQL query to fetch data
    query = "select * from project;"
    result = pd.read_sql_query(query, pgConnection)

    # Close connection
    pgConnection.close()

    # Convert date column to datetime format
    result['saledate'] = pd.to_datetime(result['saledate'])

    # Add total sales column (assuming you want to calculate sales value as itemssold * (1 - discount))
    #result['total_sales'] = result['itemssold'] * (1 - result['discount'])
    #result = result.drop(columns=['total_sales'])

    # Create a column for whether shipping is free
    result['is_freeship'] = result['freeship'].apply(lambda x: 'Free' if x == 1 else 'Paid')

    # Preview the data (optional)
    # print(result.head())

    # Return the result DataFrame
    return result

    # Convert the DataFrame to a dictionary for JSON serialization
    # return result.to_dict(orient="records")