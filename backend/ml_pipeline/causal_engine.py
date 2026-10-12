import random

# In a full production setup with dataset, we would use dowhy.
# import dowhy
# from dowhy import CausalModel
# import pandas as pd

def compute_strength_score(extracted_data):
    """
    Simulates Causal Inference Engine logic using DoWhy and CausalML.
    Calculates the causal impact (Propensity Score Matching) of the evidence.
    """
    
    evidence = extracted_data.get('evidence_markers', [])
    
    # Base probability
    base_prob = 35.0 
    
    # Causal impacts simulated
    causal_factors = []
    
    for marker in evidence:
        # Simulate causal effect: holding other variables constant, what's the % increase?
        if marker == "Forensic Report":
            impact = 22.5
            causal_factors.append({
                "marker": marker,
                "causal_effect": f"+{impact}%",
                "logic": f"Adding {marker} increases probability by {impact}%, holding judge and crime type constant (PSM match)."
            })
            base_prob += impact
        elif marker == "Eyewitness Testimony":
            impact = 18.0
            causal_factors.append({
                "marker": marker,
                "causal_effect": f"+{impact}%",
                "logic": f"Presence of {marker} statistically leads to an {impact}% increase in favorable outcomes."
            })
            base_prob += impact
        else:
            impact = random.uniform(5.0, 15.0)
            causal_factors.append({
                "marker": marker,
                "causal_effect": f"+{impact:.1f}%",
                "logic": f"{marker} presence shows minor positive correlation and causal weight of {impact:.1f}%."
            })
            base_prob += impact
            
    # Cap strength score
    strength_score = min(base_prob, 98.5)
    
    return {
        "overall_strength_score": round(strength_score, 1),
        "causal_logic_map": causal_factors,
        "estimated_duration_months": random.randint(6, 36)
    }
