import pandas as pd
from backend.app import extract_nlp_features, calculate_metrics

df = pd.read_csv("sample_data.csv")
df["override"] = df["model_decision"] != df["human_decision"]
df = extract_nlp_features(df)
metrics = calculate_metrics(df)
print("Is Complacent counts:")
print(df["is_complacent"].value_counts())
print("\nMetrics table:")
print(metrics[["week", "complacency_risk"]])
print("\nAvg complacency risk:")
print(metrics["complacency_risk"].mean())
