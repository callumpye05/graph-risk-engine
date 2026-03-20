import csv 
from database import db 



def export_tx_tocsv(filename="training_data.csv"):
    query ="""
    MATCH (a:Account)-[r:TRANSFERRED_TO]->(b:Account)
    RETURN a.id AS from_account, r.amount AS amount , r.time AS timestamp
    LIMIT 1000
    """

    try: 
        with db.driver.session() as session:
            result = session.run(query)
            records = list(result)

            if not records :
                print("No transactions found in the database")
            
            with open(filename, mode='w', newline='') as file:
                fieldnames = ['account_id', 'amount', 'timestamp', 'is_fraud']
                writer = csv.writer(file)
                writer.writerow(fieldnames)

                for record in records:
                    amt = float(record['amount'])
                    is_fraud = 1 if amt > 800 else 0
                    writer.writerow([record['from_account'], amt,record['timestamp'], is_fraud])
        print(f"Exported {len(records)} transactions to {filename}")
    except Exception as e:
        print(f"error exporting transactions: {e}")
    
if __name__ == "__main__":
     export_tx_tocsv()





            





 