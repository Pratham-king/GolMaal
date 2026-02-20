import csv
from datetime import datetime
from typing import List, Dict
from src.models.transaction import Transaction

class DataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_transactions(self) -> Dict[str, Transaction]:
        transactions = []
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # handle potential whitespace in headers
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
                
                for row in reader:
                    # Parse timestamp format: YYYY-MM-DD HH:MM:SS
                    try:
                        timestamp_str = row['timestamp'].strip()
                        # Handles 2024-01-21 3:01:00 or 2024-01-21 03:01:00
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        print(f"Skipping row with invalid timestamp: {row}")
                        continue

                    # transaction_id is no longer in the model, but used as key
                    tx_id = row['transaction_id'].strip()
                    transaction = Transaction(
                        sender_id=row['sender_id'].strip(),
                        receiver_id=row['receiver_id'].strip(),
                        amount=float(row['amount']),
                        timestamp=timestamp
                    )
                    transactions.append((tx_id, transaction))
                    
            # Sort by time
            transactions.sort(key=lambda x: x[1].timestamp)
            
            # Convert to dictionary
            transaction_dict = {tx_id: tx for tx_id, tx in transactions}
            
            print(f"Loaded {len(transaction_dict)} transactions.")
            return transaction_dict

        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
            return {}
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}
