import os
import json
from fastapi.testclient import TestClient
from backend.app import app

def main():
    print("==============================================")
    print("Testing Pipeline: HF API & Accuracy Metrics")
    print("==============================================\n")
    
    # Check if HF_TOKEN is present
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        print("⚠️ WARNING: 'HF_TOKEN' environment variable is not set.")
        print("The Hugging Face API will be called without authentication, which may lead to rate limiting or fallback behavior.")
        print("To set it in Powershell: $env:HF_TOKEN=\"your_token\"")
        print("----------------------------------------------\n")
    else:
        print("✅ HF_TOKEN is set! The Hugging Face API will be authenticated.")
        print("----------------------------------------------\n")

    client = TestClient(app)
    
    file_path = "sample_data.csv"
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} not found.")
        return

    print(f"Submitting {file_path} to the /analyze endpoint...")
    
    with open(file_path, "rb") as f:
        response = client.post("/analyze", files={"file": ("sample_data.csv", f, "text/csv")})
        
    if response.status_code != 200:
        print(f"❌ Error from API: {response.status_code} - {response.text}")
        return
        
    data = response.json()
    
    print("\n✅ Analysis Complete! Results:")
    print("==============================================")
    
    # Ground Truth Accuracy
    gt_metrics = data.get("ground_truth_metrics")
    if gt_metrics:
        print("\n📊 Accuracy & Ground Truth Metrics:")
        print(f"  - AI Model Accuracy:     {gt_metrics['ai_accuracy']*100:.1f}%")
        print(f"  - Human Accuracy:        {gt_metrics['human_accuracy']*100:.1f}%")
        print(f"  - Justified Overrides:   {gt_metrics['counts']['justified']} ({gt_metrics['justified_override_rate']*100:.1f}%)")
        print(f"  - Unjustified Overrides: {gt_metrics['counts']['unjustified']} ({gt_metrics['unjustified_override_rate']*100:.1f}%)")
        print(f"  - Missed Overrides:      {gt_metrics['counts']['missed']} ({gt_metrics['missed_override_rate']*100:.1f}%)")
    else:
        print("\n⚠️ No ground_truth_metrics returned. Make sure 'ground_truth' column exists in CSV.")

    # HF API RAG Themes
    rag_themes = data.get("rag_explanations", [])
    print("\n🧠 Hugging Face API TrustRAG Themes (Overridden Cases):")
    if not rag_themes:
        print("  - No themes detected.")
    for theme in rag_themes:
        print(f"  - [{theme['theme']}] Count: {theme['count']}")
        print(f"    Example: \"{theme['example']}\"")
        
    # Advanced Trust Metrics
    adv = data.get("advanced_analysis", {})
    print("\n📈 Advanced System Health:")
    print(f"  - System Health Label:      {adv.get('system_health')}")
    print(f"  - Human-AI Alignment Index: {adv.get('human_ai_alignment_index', 0)*100:.1f}%")
    print(f"  - Trust Volatility:         {adv.get('trust_volatility', 0):.3f}")
    
    print("\n==============================================")
    print("Done.")

if __name__ == "__main__":
    main()
