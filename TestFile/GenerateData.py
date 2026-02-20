import csv
import random
from datetime import datetime, timedelta

def generate_laundering_data(filename="transactions_10k.csv", total_rows=10000):
    data = []
    current_id = 1
    loop = 8
    fan_in = 2
    fan_out = 4
    shl = 2
    merch = 90
    payroll = 20


    def get_tid():
        nonlocal current_id
        tid = f"TX{current_id:05d}"
        current_id += 1
        return tid

    def get_ts(day=None, month=None, start_date=None,reverse=False):
        """Generates timestamp after start_date in DDMMYYYY:HHMMSS format."""
        if start_date:
            dt = datetime.strptime(start_date, "%d%m%Y:%H%M%S")
            # Add random days (0-365) and random time
            if reverse:
                dt -= timedelta(days=random.randint(0, 95), hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
            else :
                dt += timedelta(days=random.randint(0, 95), hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
        else:
            y, m = 2023, month or random.randint(1, 12)
            d = day or random.randint(1, 28)
            dt = datetime(y, m, d, random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))
        return dt.strftime("%d%m%Y:%H%M%S")

    # --- 1. Money Laundering Loops (A -> B -> C -> A) ---
    # Creating 15 different loops of varying lengths (3 to 9)
    for l_idx in range(loop):
        date = get_ts()
        length = random.randint(3, 9)
        loop_nodes = [f"NODE_L{l_idx}_{i}" for i in range(length)]
        amount = random.randint(5000, 15000)
        for i in range(length):
            sender = loop_nodes[i]
            receiver = loop_nodes[(i + 1) % length]
            data.append([get_tid(), sender, receiver, amount, get_ts(start_date=date)])

    # --- 2. Fan-In (Tree) & Fan-Out ---
    # Fan-In: 100 accounts sending to 1 central "Hub"
    
    for i in range(fan_in):
        date = get_ts()
        hub_in = f"CENTRAL_COLLECTOR_{i}"
        for i in range(random.randint(12,100)): # Each sender can have 1-3 transactions to the hub
            data.append([get_tid(), f"SENDER_FAN_{i}", hub_in, random.randint(100, 1000), get_ts(start_date=date, reverse=True)])
    
    # Fan-Out: 1 central account sending to 100 "Mules"
    
    for i in range(fan_out):
        date = get_ts()
        hub_out = f"CENTRAL_DISPERSER_{i}"
        for i in range(random.randint(12,100)):
            data.append([get_tid(), hub_out, f"MULE_REC_{i}", random.randint(100, 1000), get_ts()])
    
    # --- 3. Shell Accounts (Low volume middle-men) ---
    for s_idx in range(shl):
        shell = f"SHELL_ACC_{s_idx}"
        amt = random.randint(8000, 9000)
        # Sequence: Layering move
        data.append([get_tid(), "UNKNOWN_ORIGIN", shell, amt, get_ts()])
        data.append([get_tid(), shell, "OFFSHORE_EXIT", amt - 10, get_ts()])

    # --- 4. High Volume Merchants ---
    merchants = ["GLOBAL_RETAIL_X", "TECH_STORE_Y", "ENERGY_CORP_Z"]
    for m in merchants:
        for _ in range(int(merch // 3)): # 900 total merchant rows
            data.append([get_tid(), f"USER_{random.randint(100, 999)}", m, random.randint(1000, 20000), get_ts()])

    # --- 5. Payroll (Monthly cycles) ---
    company = ["BIG_CORP_A","BIG_CORP_B","BIG_CORP_C"]
    for c in company:
        staff = [f"STAFF_{i:02d}" for i in range(payroll // len(company))]
        for month in range(1, 13):
            for member in staff:
                data.append([get_tid(), c, member, 5000, get_ts(day=random.randint(2, 5), month=month)])

    # --- 6. Fill with Random Noise (Normal Transactions) ---
    remaining = total_rows - len(data)
    for _ in range(remaining):
        u1, u2 = f"U_{random.randint(1000, 9999)}", f"U_{random.randint(1000, 9999)}"
        if u1 != u2:
            data.append([get_tid(), u1, u2, random.randint(10, 5000), get_ts()])

    # Shuffle so patterns aren't grouped together
    random.shuffle(data)

    # Write to CSV
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['transaction_id', 'sender_id', 'receiver_id', 'amount', 'timestamp'])
        writer.writerows(data)

    print(f"Success! Generated {len(data)} rows in {filename}")

if __name__ == "__main__":
    generate_laundering_data()