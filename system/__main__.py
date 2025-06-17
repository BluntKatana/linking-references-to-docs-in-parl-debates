import argparse

from detection import detect_references
from reconciliation import reconcile_references
from featurebuilder import FEATURE_COMBOS
from system.vectordb.crud import setup_elasticsearch

def run_pipeline(minute_id, system):
    """
    Runs the recognision and reconciliation tasks for a parliamentary minute.
    """
    print(f"[INFO][run_pipeline] - Start: {minute_id} with system {system}")
    # Step 1: Recognize references in the minutes
    references = detect_references(minute_id, system)
    print(f"[INFO][run_pipeline] - {len(references)} references recognized for minute {minute_id}")

    # Step 2: Reconcile the recognized references with the database
    for feature_builder in FEATURE_COMBOS:
        print(f"[INFO][run_pipeline] - Start: feature builder {feature_builder.name}")
        reconcile_references(minute_id, references, feature_builder)

    print(f"[INFO][run_pipeline] - End: {minute_id} with system {system}")

    print("\t")

if __name__ == "__main__":
    """
    Example usage:
        python pipeline.py -id h-tk-20182019-64-32
    """
    parser = argparse.ArgumentParser(description="Run the detection and linking pipeline for parliamentary minutes.")
    parser.add_argument("-id", "--minute_id", help="The identifier of the minute to process.", required=True)
    parser.add_argument("-s", "--system", help="The system to use for processing",
                        choices=['fewshot-single', 'fewshot-two-pass', 'zeroshot-single', 'zeroshot-two-pass'],
                        default='fewshot-two-pass'
                    ),

    args = parser.parse_args()
    minute_id = args.minute_id
    system = args.system


    if minute_id:
        setup_elasticsearch(dangerously_overwrite_existing_index=False)
        run_pipeline(minute_id, system)
    else:
        print("[ERROR] Please provide a valid minute ID using the -id argument.")