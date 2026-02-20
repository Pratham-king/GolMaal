import sys
import os
import time

# Add local directory to path to allow imports if running directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.core.data_loader import DataLoader
from src.core.graph_builder import GraphBuilder
from src.patterns.loops import LoopDetector
from src.patterns.dispersal import DispersalDetector
from src.patterns.shells import ShellDetector
from src.patterns.payroll import PayrollDetector
from src.patterns.merchant import MerchantDetector
from src.clustering.network_builder import NetworkBuilder
from src.scoring.account_scorer import AccountScorer
from src.scoring.risk_engine import RiskEngine
from src.utils.json_exporter import JsonExporter


def main():
    
    # DONE file check
    if os.path.exists("DONE"):
        os.remove("DONE")

    start_time = time.time()
    
    # Default file path
    file_path = "transactions.csv"
    
    # 1. Load CSV
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    # Determine output directory based on input file location
    output_dir = os.path.dirname(file_path)
    outputfile = os.path.join(output_dir, "output.json")
    
    print(f"Starting pipeline with {file_path}")
    loader = DataLoader(file_path)
    transactions = loader.load_transactions()
    
    if not transactions:
        print("No transactions loaded. Exiting.")
        return -1

    # 2. Build Graph
    gb = GraphBuilder(transactions)
    accounts, adj_list, rev_adj_list = gb.build_graph()

    net_builder = NetworkBuilder(accounts, adj_list)

    # 3. Detect Patterns 
    # Merchant (Before Loops/Scoring)
    merchant_detector = MerchantDetector(accounts, adj_list, rev_adj_list)
    merchant_detector.detect()


    # Payroll (Before Dispersal)
    payroll_detector = PayrollDetector(accounts, adj_list)
    payroll_detector.detect()


    # Loops
    loop_detector = LoopDetector(accounts, adj_list, network_builder=net_builder)
    loop_detector.detect()
    loops = loop_detector.loops_detected

    # Dispersal
    dispersal_detector = DispersalDetector(accounts, adj_list, rev_adj_list, network_builder=net_builder)
    dispersal_detector.detect()

    # Shells
    shell_detector = ShellDetector(accounts, adj_list, network_builder=net_builder)
    shell_detector.detect()

    # 4. Score Accounts
    scorer = AccountScorer(accounts)
    scorer.score_accounts()

    # 5. Build Networks
    # Networks are built during pattern detection (e.g. loops) or explicitly here if needed.
    # We already have net_builder.
    networks = net_builder.networks

    # 6. Assess Network Risk
    risk_engine = RiskEngine(networks, accounts)
    risk_engine.evaluate_network_risk()

    # 7. Export
    JsonExporter.export(accounts, networks, outputfile)
    
    # 8. Download Report
    end_time = time.time()
    processing_time_seconds = end_time - start_time
    # Format processing time
    processing_time_str = f"{processing_time_seconds:.2f} seconds"
    
    download_file = os.path.join(output_dir, "download.json")
    if len(sys.argv) > 2:
        download_file = sys.argv[2]
        
    JsonExporter.export_download_report(accounts, networks, loops, processing_time_str, download_file, adj_list, rev_adj_list)

    # Create DONE file
    with open("DONE", "w") as f:
        pass

    print("Pipeline complete.")

if __name__ == "__main__":
    main()
