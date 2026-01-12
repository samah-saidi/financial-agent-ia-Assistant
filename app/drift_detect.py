import random
from typing import Dict, Any

def detect_drift(reference_file: str, production_file: str, threshold: float = 0.05) -> Dict[str, Any]:
    """
    Mock implementation of drift detection for STOCK MARKET data.
    """
    # Features typiques d'un dataset boursier
    features = ["Open", "High", "Low", "Close", "Volume", "Adj Close"]
    results = {}
    
    for feature in features:
        # Simulation d'un drift aléatoire
        is_drift = random.random() < 0.15 
        
        results[feature] = {
            "drift_detected": is_drift,
            "p_value": round(random.random(), 4),
            "statistic": round(random.uniform(0, 1), 4),
            "type": "ks_test"
        }
    
    return results
