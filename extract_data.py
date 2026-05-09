import csv 
from database import db 

def export_tx_tocsv(filename="training_data.csv"):
    #reconstruct the multi dim matrix 
    query= """
    MATCH (a:Account)-[r:TRANSFERRED_TO]->(b:Account)
    WITH a, r,toFloat(r.amount) AS tx_amount, toFloat(r.time) AS tx_time, coalesce(r.is_fraud, 0) AS is_fraud
    ORDER BY tx_time DESC  
    LIMIT 5000

    //reconstruct 24h outboudn
    OPTIONAL MATCH (a)-[out24:TRANSFERRED_TO]->()
    WHERE toFloat(out24.time) <= tx_time AND toFloat(out24.time) > (tx_time - 86400)
    WITH a, tx_amount, tx_time, is_fraud, coalesce(sum(out24.amount), 0.0) AS total_out_24h

    //reconstruct 24h inbound
    OPTIONAL MATCH ()-[in24:TRANSFERRED_TO]->(a)
    WHERE toFloat(in24.time) <= tx_time AND toFloat(in24.time) > (tx_time - 86400)
    WITH a, tx_amount, tx_time, is_fraud, total_out_24h, coalesce(sum(in24.amount), 0.0) AS total_in_24h

    // reconstuct 30d outbound (for baseline)
    OPTIONAL MATCH (a)-[out30:TRANSFERRED_TO]->()
    WHERE toFloat(out30.time) <= tx_time AND toFloat(out30.time) > (tx_time - 2592000)
    WITH a, tx_amount, tx_time, is_fraud, total_out_24h, total_in_24h, coalesce(sum(out30.amount), 0.0) AS total_out_30d

    RETURN 
        a.id AS account_id, 
        tx_amount AS amount, 
        tx_time AS timestamp,
        total_out_24h,
        total_in_24h,
        total_out_30d,
        is_fraud
    """
    try: 
        with db.driver.session() as session:
            result= session.run(query)
            records =list(result)

            if not records:
                print("No transactions found in the database")
                return
            
            with open(filename, mode='w', newline='') as file:
                fieldnames = ['account_id', 'amount', 'timestamp', 'total_out_24h', 'total_in_24h', 'total_out_30d', 'is_fraud']
                writer = csv.writer(file)
                writer.writerow(fieldnames)

                for record in records:
                    writer.writerow([
                        record['account_id'], 
                        record['amount'],
                        record['timestamp'], 
                        record['total_out_24h'],
                        record['total_in_24h'],
                        record['total_out_30d'],
                        record['is_fraud']
                    ])
                    
        print(f"Exported {len(records)} matrix profiles to {filename}")
    except Exception as e:
        print(f"Error exporting transactions: {e}")
    
if __name__ == "__main__":
     export_tx_tocsv()