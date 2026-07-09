import pandas as pd
import io
from backend.app import extract_nlp_features, calculate_metrics, detect_anomalies

# A tiny CSV with only 3 rows, and one has a garbage date ("unknown")
csv_data = """date,department,model_decision,human_decision,ground_truth,confidence_note
unknown,Underwriting,Approve,Approve,Approve,"Looks standard."
2023-10-02,Fraud,Reject,Reject,Reject,"Clear fraud."
N/A,Compliance,Approve,Reject,Reject,"Override."
"""

df = pd.read_csv(io.StringIO(csv_data))
df["override"] = df["model_decision"] != df["human_decision"]

# 1. Test the NLP feature extraction
df = extract_nlp_features(df)
print("--- NLP Features Generated ---")
print(f"Skepticism flags: {df['skepticism_flag'].tolist()}")

# 2. Test the Date parsing fix
try:
    metrics = calculate_metrics(df)
    print("\n--- Date Parsing Success! ---")
    print(metrics[["week", "total_cases"]])
except Exception as e:
    print(f"\n--- Date Parsing FAILED! ---")
    print(e)

# 3. Test the Small Dataset Scatter fix (<10 rows)
print(f"\nTesting anomalies with {len(df)} rows (should be < 10)...")
try:
    anomaly_output = detect_anomalies(df)
    print("--- Small Dataset Anomaly Success! ---")
    print(f"Anomalies found: {len(anomaly_output['list'])}")
    print(f"Scatter points returned: {len(anomaly_output['scatter'])}")
except Exception as e:
    print(f"\n--- Small Dataset Anomaly FAILED! ---")
    print(e)
