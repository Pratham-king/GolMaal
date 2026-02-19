import csv
from datetime import datetime
from typing import List
from src.models.transaction import Transaction

class DataLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_transactions(self) -> List[Transaction]:
        transactions = []
        try:
            with open(self.file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # handle potential whitespace in headers
                reader.fieldnames = [name.strip() for name in reader.fieldnames]
                
                for row in reader:
                    # Parse timestamp format: DDMMYYYY:hhmmss
                    try:
                        timestamp_str = row['timestamp'].strip()
                        timestamp = datetime.strptime(timestamp_str, "%d%m%Y:%H%M%S")
                    except ValueError:
                        print(f"Skipping row with invalid timestamp: {row}")
                        continue

                    transaction = Transaction(
                        transaction_id=row['transaction_id'].strip(),
                        sender_id=row['sender_id'].strip(),
                        receiver_id=row['receiver_id'].strip(),
                        amount=float(row['amount']),
                        timestamp=timestamp
                    )
                    transactions.append(transaction)
                    
            # Sort by time
            transactions.sort(key=lambda x: x.timestamp)
            print(f"Loaded {len(transactions)} transactions.")
            return transactions

        except FileNotFoundError:
            print(f"Error: File not found at {self.file_path}")
            return []
        except Exception as e:
            print(f"Error loading data: {e}")
            return []
