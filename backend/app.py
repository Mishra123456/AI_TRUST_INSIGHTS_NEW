from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import pandas as pd
import numpy as np

# -----------------------------
# ML / NLP
# -----------------------------
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, IsolationForest
from sklearn.pipeline import Pipeline

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import defaultdict

# Safe NLTK init (no repeated downloads)
try:
    nltk.data.find("sentiment/vader_lexicon.zip")
except LookupError:
    nltk.download("vader_lexicon")

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="TrustScope – Human–AI Trust Intelligence")

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# NLP Feature Extraction
# -----------------------------
def extract_nlp_features(df):
    sia = SentimentIntensityAnalyzer()

    notes = df["confidence_note"].fillna("")

    # 1. Sentiment compound score: [-1, 1]
    df["sentiment"] = notes.apply(lambda x: sia.polarity_scores(x)["compound"])

    # 2. Negativity score: [0, 1]
    df["negativity"] = notes.apply(lambda x: sia.polarity_scores(x)["neg"])

    # 3. Skepticism flag: [0, 1] (Triggered by keywords OR highly negative sentiment)
    has_keywords = notes.str.contains(
        "wrong|missed|override|manual|human|uncertain|mismatch|bias|doubt|suspicious|confusing|weird",
        case=False,
        na=False,
    )
    df["skepticism_flag"] = (has_keywords | (df["sentiment"] < -0.2)).astype(int)

    # Complacency Flag: They were skeptical, but they DID NOT override (Rubber-stamping)
    df["is_complacent"] = (df["skepticism_flag"] == 1) & (df["override"] == False)

    # 4. Note character length (normalized)
    lengths = notes.str.len()
    max_len = lengths.max()
    df["note_length"] = (lengths / max_len).fillna(0.0) if max_len > 0 else 0.0

    return df

# -----------------------------
# ML Model (Ex-Post Attribution Mode)
# -----------------------------
def train_trust_model(df):
    X = df[["sentiment", "negativity", "skepticism_flag", "note_length"]]
    y = df["override"]

    # Handle cases where there is only 1 class in override
    if len(np.unique(y)) < 2:
        return None

    rf = RandomForestClassifier(
        n_estimators=50,
        max_depth=3,
        min_samples_leaf=2,
        random_state=42
    )
    gb = GradientBoostingClassifier(
        n_estimators=50,
        max_depth=2,
        min_samples_leaf=2,
        random_state=42
    )

    ensemble = VotingClassifier(
        estimators=[('rf', rf), ('gb', gb)],
        voting='soft'
    )

    pipeline = Pipeline(
        [
            ("model", ensemble),
        ]
    )
    pipeline.fit(X, y)
    return pipeline


def explain_model(pipeline):
    if pipeline is None:
        return {
            "sentiment_weight": 0.0,
            "negativity_weight": 0.0,
            "skepticism_weight": 0.0,
            "note_length_weight": 0.0,
        }
    
    ensemble = pipeline.named_steps["model"]
    # Get importances from fitted sub-estimators and average them
    rf_importances = ensemble.named_estimators_['rf'].feature_importances_
    gb_importances = ensemble.named_estimators_['gb'].feature_importances_
    importances = 0.5 * rf_importances + 0.5 * gb_importances

    return {
        "sentiment_weight": float(importances[0]),
        "negativity_weight": float(importances[1]),
        "skepticism_weight": float(importances[2]),
        "note_length_weight": float(importances[3]),
    }

# -----------------------------
# Trust Metrics
# -----------------------------
def calculate_metrics(df):
    df["date"] = pd.to_datetime(df["date"], errors="coerce").fillna(pd.Timestamp("today"))
    df["week"] = df["date"].dt.to_period("W").astype(str)

    grouped = (
        df.groupby("week")
        .agg(
            override_rate=("override", "mean"),
            trust_score=("override", lambda x: 1.0 - x.mean()),
            avg_sentiment=("sentiment", "mean"),
            skepticism_rate=("skepticism_flag", "mean"),
            complacency_risk=("is_complacent", "mean"),
            total_cases=("override", "count"),
        )
        .reset_index()
    )
    
    return grouped

# -----------------------------
# Advanced Trust Intelligence
# -----------------------------
def trust_volatility(metrics):
    val = metrics["trust_score"].std()
    if pd.isna(val) or np.isnan(val):
        return 0.0
    return float(val)


def trust_decay_rate(metrics):
    if len(metrics) < 2:
        return 0.0
    x = np.arange(len(metrics))
    y = metrics["trust_score"].values
    try:
        slope = float(np.polyfit(x, y, 1)[0])
        if pd.isna(slope) or np.isnan(slope):
            return 0.0
        # A negative slope represents trust decay. Returning -slope expresses decay as a positive rate.
        return -slope
    except Exception:
        return 0.0


def human_ai_alignment_index(metrics):
    if metrics.empty:
        return 1.0
    avg_trust = float(metrics["trust_score"].mean())
    avg_sentiment_normalized = float((metrics["avg_sentiment"].mean() + 1) / 2)
    avg_skepticism = float(metrics["skepticism_rate"].mean())
    
    # Balanced formulation: trust (50%), low skepticism (30%), positive sentiment (20%)
    return float(
        0.5 * avg_trust
        + 0.3 * (1.0 - avg_skepticism)
        + 0.2 * avg_sentiment_normalized
    )


def system_health_label(score):
    if score > 0.7:
        return "HEALTHY"
    if score > 0.45:
        return "AT RISK"
    return "CRITICAL"


def intervention_priority(metrics):
    rows = []
    for _, r in metrics.iterrows():
        # Score increases with: override rate (50%), skepticism rate (30%), negative sentiment penalty (20%)
        # Map sentiment [-1, 1] to penalty [1, 0]
        sentiment_penalty = (1.0 - r["avg_sentiment"]) / 2.0
        score = (
            r["override_rate"] * 0.5
            + r["skepticism_rate"] * 0.3
            + sentiment_penalty * 0.2
        )
        rows.append({"week": r["week"], "priority_score": round(score, 2)})
    return sorted(rows, key=lambda x: x["priority_score"], reverse=True)




# -----------------------------
# RAG-STYLE THEME ANALYSIS (HUGGING FACE API)
# -----------------------------
import requests
from sklearn.metrics.pairwise import cosine_similarity
import json
import time

class TrustRAG:
    _categories = []
    _category_vectors = None
    
    API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    
    @classmethod
    def get_embeddings(cls, texts):
        # Hugging Face Free API allows up to a certain rate limit.
        headers = {}
        HF_TOKEN = os.getenv("HF_TOKEN")
        if HF_TOKEN:
            headers["Authorization"] = f"Bearer {HF_TOKEN}"
            
        payload = {"inputs": texts}
        try:
            response = requests.post(cls.API_URL, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                return np.array(response.json())
            else:
                print(f"HF API Error: {response.text}")
                return None
        except Exception as e:
            print(f"HF API Request failed: {e}")
            return None

    @classmethod
    def initialize(cls):
        if cls._category_vectors is not None:
            return
        
        prototypes = {
            "Model Inaccuracy": [
                "wrong prediction", "incorrect outcome", "error in model", 
                "false positive", "hallucination", "bad output"
            ],
            "Context Failure": [
                "missed context", "didn't understand nuance", "sarcasm", 
                "ambiguous meaning", "domain mismatch", "out of distribution"
            ],
            "Human Preference": [
                "manual override", "human judgment", "stylistic choice", 
                "personal preference", "better phrasing", "editorial decision"
            ],
            "General Skepticism": [
                "uncertain", "doubt", "not sure", "verify later", "skeptical"
            ]
        }
        
        cls._categories = []
        phrases = []
        
        for category, p_list in prototypes.items():
            for p in p_list:
                cls._categories.append(category)
                phrases.append(p)
                
        vectors = cls.get_embeddings(phrases)
        if vectors is not None:
            cls._category_vectors = vectors
            print("Successfully initialized TrustRAG with Hugging Face API.")

    def __init__(self):
        if self._category_vectors is None:
            self.initialize()

    def classify_batch(self, texts):
        if not texts:
            return []
            
        # Keyword fallback function
        def keyword_fallback(text):
            text_lower = text.lower()
            if any(w in text_lower for w in ["wrong", "incorrect", "error", "false", "hallucination", "bad"]):
                return "Model Inaccuracy"
            if any(w in text_lower for w in ["context", "nuance", "sarcasm", "ambiguous", "mismatch", "domain"]):
                return "Context Failure"
            if any(w in text_lower for w in ["override", "manual", "preference", "phrasing", "editorial", "judgment"]):
                return "Human Preference"
            return "General Skepticism"
            
        if self._category_vectors is None:
            self.initialize()
            
        if self._category_vectors is None:
            return [keyword_fallback(t) for t in texts]
            
        # Bulk encode all texts in one API call
        text_vectors = self.get_embeddings(texts)
        if text_vectors is None:
            return [keyword_fallback(t) for t in texts]
            
        # Calculate cosine similarity against all prototype vectors
        similarities = cosine_similarity(text_vectors, self._category_vectors)
        
        # Get the closest category for each text
        results = []
        for i in range(len(texts)):
            best_idx = np.argmax(similarities[i])
            results.append(self._categories[best_idx])
            
        return results

    def build(self, notes):
        if not notes:
            return []
            
        buckets = defaultdict(list)
        classifications = self.classify_batch(notes)
        
        for note, category in zip(notes, classifications):
            buckets[category].append(note)

        return [
            {"theme": k, "count": len(v), "example": v[0]}
            for k, v in sorted(buckets.items(), key=lambda x: len(x[1]), reverse=True)
            if v
        ]

# (Initialization is now handled lazily on the first request to avoid boot-time network errors on Render)


# -----------------------------
# Executive Summary
# -----------------------------
def executive_summary(metrics, weights, rag, haai, complacency_risk=0.0):
    summary = []

    if not metrics.empty and metrics["trust_score"].min() < 0.5:
        summary.append("Trust declined during periods of elevated overrides.")

    if rag:
        summary.append(f"Primary trust failure driver: {rag[0]['theme']}.")
    else:
        summary.append("No major trust failure drivers detected.")

    if weights and any(w != 0.0 for w in weights.values()):
        strongest = max(weights, key=lambda k: abs(weights[k]))
        summary.append(f"ML attribution identifies '{strongest}' as the dominant predictor.")
    else:
        summary.append("ML attribution not available due to uniform alignment.")

    summary.append(f"Overall system health classified as {system_health_label(haai)}.")
    
    if complacency_risk > 0.1:
        summary.append(f"Warning: Complacency Risk is elevated ({complacency_risk:.1%}). Users may be rubber-stamping model outputs despite expressing reservations in their notes.")

    return " ".join(summary)


# -----------------------------
# Actionable Recommendations & Anomalies
# -----------------------------
def generate_recommendations(metrics, rag, haai, complacency_risk):
    recs = []
    
    if haai < 0.6:
        recs.append({
            "title": "Investigate AI-Human Alignment",
            "description": f"The overall Human-AI Alignment Index is critical ({(haai*100):.1f}%). Initiate a full audit of recent model updates to identify performance degradation.",
            "type": "critical"
        })
        
    if complacency_risk > 0.1:
        recs.append({
            "title": "Address Operator Complacency",
            "description": "High rates of skepticism without corresponding overrides indicate operators may be rubber-stamping AI decisions. Mandate secondary reviews for high-risk predictions.",
            "type": "warning"
        })
        
    if rag:
        top_theme = rag[0]
        recs.append({
            "title": f"Mitigate '{top_theme['theme']}'",
            "description": f"This theme accounted for {top_theme['count']} recent trust failures. For example: '{top_theme['example']}'. Update training data to cover these edge cases.",
            "type": "action"
        })
        
    if not recs:
        recs.append({
            "title": "Maintain Current Governance",
            "description": "System health is stable. Continue monitoring operator notes and override rates for emerging trends.",
            "type": "success"
        })
        
    return recs


def detect_anomalies(df):
    if len(df) < 10:
        # Still return scatter data so the frontend chart doesn't go blank!
        scatter_data = []
        for _, row in df.iterrows():
            scatter_data.append({
                "sentiment": float(row.get("sentiment", 0.0)),
                "note_length": float(row.get("note_length", 0.0)),
                "is_anomaly": False,
                "override": bool(row.get("override", False))
            })
        return {"list": [], "scatter": scatter_data}
    
    features = df[["sentiment", "negativity", "skepticism_flag", "note_length"]].fillna(0)
    
    # Train Isolation Forest
    iso_forest = IsolationForest(contamination=0.05, random_state=42)
    df["anomaly_score"] = iso_forest.fit_predict(features) # -1 for anomaly, 1 for normal
    
    # Get anomaly details
    anomalies = df[df["anomaly_score"] == -1].copy()
    
    # Sort by note length or sentiment extremity to surface interesting ones
    anomalies["extremity"] = abs(anomalies["sentiment"]) + anomalies["note_length"]
    anomalies = anomalies.sort_values("extremity", ascending=False).head(10)
    
    results = []
    for _, row in anomalies.iterrows():
        results.append({
            "date": str(row["date"]),
            "note": row["confidence_note"],
            "sentiment": float(row["sentiment"]),
            "note_length": float(row["note_length"]),
            "override": bool(row["override"])
        })
        
    # Also return scatter plot data (all points) for graph
    scatter_data = []
    for _, row in df.iterrows():
        scatter_data.append({
            "sentiment": float(row["sentiment"]),
            "note_length": float(row["note_length"]),
            "is_anomaly": bool(row["anomaly_score"] == -1),
            "override": bool(row["override"])
        })
        
    return {"list": results, "scatter": scatter_data}


# -----------------------------
# MAIN ENDPOINT
# -----------------------------
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    required = {"date", "model_decision", "human_decision", "confidence_note"}
    if not required.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain columns: {required}",
        )

    df["override"] = df["model_decision"] != df["human_decision"]
    df = extract_nlp_features(df)

    pipeline = train_trust_model(df)
    weights = explain_model(pipeline)

    if pipeline is not None:
        df["override_risk"] = pipeline.predict_proba(
            df[["sentiment", "negativity", "skepticism_flag", "note_length"]]
        )[:, 1]
    else:
        default_risk = 1.0 if df["override"].any() else 0.0
        df["override_risk"] = default_risk

    df["risk_tier"] = pd.cut(
        df["override_risk"], [0, 0.4, 0.7, 1.0], labels=["LOW", "MEDIUM", "HIGH"], include_lowest=True
    ).fillna("LOW")

    metrics = calculate_metrics(df)
    
    # Filter theme analysis only to overridden cases to capture why trust breaks down
    overridden_df = df[df["override"]]
    rag = TrustRAG().build(overridden_df["confidence_note"].dropna().tolist())
    
    haai = human_ai_alignment_index(metrics)
    avg_complacency = float(metrics["complacency_risk"].mean() if "complacency_risk" in metrics else 0.0)

    exec_summary = executive_summary(metrics, weights, rag, haai, avg_complacency)

    # Optional Ground Truth Evaluation
    has_ground_truth = "ground_truth" in df.columns
    ground_truth_metrics = None
    if has_ground_truth:
        df["ai_correct"] = df["model_decision"] == df["ground_truth"]
        df["human_correct"] = df["human_decision"] == df["ground_truth"]
        
        df["justified_override"] = df["override"] & df["human_correct"]
        df["unjustified_override"] = df["override"] & (~df["human_correct"])
        df["missed_override"] = (~df["override"]) & (~df["ai_correct"])
        
        ground_truth_metrics = {
            "ai_accuracy": float(df["ai_correct"].mean()),
            "human_accuracy": float(df["human_correct"].mean()),
            "justified_override_rate": float(df["justified_override"].mean()),
            "unjustified_override_rate": float(df["unjustified_override"].mean()),
            "missed_override_rate": float(df["missed_override"].mean()),
            "counts": {
                "justified": int(df["justified_override"].sum()),
                "unjustified": int(df["unjustified_override"].sum()),
                "missed": int(df["missed_override"].sum()),
                "total": len(df)
            }
        }

    # Department Fairness Analysis
    fairness = []
    if "department" in df.columns:
        dept_grouped = df.groupby("department").agg(
            override_rate=("override", "mean"),
            total_cases=("override", "count"),
            avg_sentiment=("sentiment", "mean")
        ).reset_index()
        
        for _, row in dept_grouped.iterrows():
            fairness.append({
                "department": str(row["department"]),
                "override_rate": float(row["override_rate"]),
                "trust_score": float(1.0 - row["override_rate"]),
                "total_cases": int(row["total_cases"]),
                "avg_sentiment": float(row["avg_sentiment"])
            })
            
    # Anomalies
    anomaly_data = detect_anomalies(df)
    
    # Recommendations
    recs = generate_recommendations(metrics, rag, haai, avg_complacency)

    return {
        "metrics": metrics.to_dict("records"),
        "ml_weights": weights,
        "top_risks": df.sort_values("override_risk", ascending=False)
        .head(5)[["confidence_note", "override_risk", "risk_tier"]]
        .to_dict("records"),
        "rag_explanations": rag,
        "executive_summary": exec_summary,
        "advanced_analysis": {
            "trust_volatility": trust_volatility(metrics),
            "trust_decay_rate": trust_decay_rate(metrics),
            "human_ai_alignment_index": haai,
            "system_health": system_health_label(haai),
            "intervention_priority": intervention_priority(metrics),
            "avg_complacency_risk": avg_complacency,
        },
        "ground_truth_metrics": ground_truth_metrics,
        "fairness_metrics": fairness,
        "anomalies": anomaly_data,
        "recommendations": recs,
    }


# -----------------------------
# API Health Check
# -----------------------------
@app.get("/")
def read_root():
    return {"status": "healthy", "message": "TrustScope API is live on Render!"}
