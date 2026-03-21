import csv 
from database import db 



def export_tx_tocsv(filename="training_data.csv"):
    query = """
    MATCH (a:Account)-[r:TRANSFERRED_TO]->(b:Account)
    WITH a,r, b, toInteger(r.time) AS tx_time
    OPTIONAL MATCH (a)-[recent:TRANSFERRED_TO]->()
    WHERE toInteger(recent.time)< tx_time 
    AND toInteger(recent.time) >(tx_time -3600)
    RETURN 
        a.id AS account_id, 
        r.amount AS amount, 
        r.time AS timestamp,
        count(recent) AS tx_count_1h
    LIMIT 1000
    """

    try: 
        with db.driver.session() as session:
            result = session.run(query)
            records = list(result)

            if not records :
                print("No transactions found in the database")
            
            with open(filename, mode='w', newline='') as file:
                fieldnames = ['account_id', 'amount', 'timestamp', 'is_fraud' , 'tx_count_1h']
                writer = csv.writer(file)
                writer.writerow(fieldnames)

                for record in records:
                    amt = float(record['amount'])
                    is_fraud = 1 if amt > 800 else 0
                    writer.writerow([record['account_id'], amt,record['timestamp'], is_fraud, record['tx_count_1h']])
        print(f"Exported {len(records)} transactions to {filename}")
    except Exception as e:
        print(f"error exporting transactions: {e}")
    
if __name__ == "__main__":
     export_tx_tocsv()





            





 