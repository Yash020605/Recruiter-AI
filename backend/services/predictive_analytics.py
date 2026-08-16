from backend.database.models import Candidate
import random

def calculate_predictive_analytics(candidate: Candidate):
    """
    Heuristic algorithm to predict hiring success and retention.
    In a real production environment, this would call an ML model (e.g. Scikit-learn, TensorFlow).
    """
    
    # 1. Calculate Hiring Success Probability (0-100)
    base_success = 50.0
    
    # Factor in AI match score
    if candidate.match_score:
        # Match score is usually 0-100, we add its weight
        base_success += (candidate.match_score - 50) * 0.4
        
    # Factor in experience
    if candidate.total_experience_years:
        # 1-10 years adds up to 15 points
        base_success += min(candidate.total_experience_years * 1.5, 15)
        
    # Factor in assessment score if available
    if candidate.hackerearth_score:
        base_success += (candidate.hackerearth_score - 50) * 0.3
        
    # Education boost
    if candidate.highest_education_level in ["Masters", "PhD"]:
        base_success += 5.0
        
    # Add a bit of random variation to simulate complex features
    base_success += random.uniform(-5.0, 5.0)
    
    # Clamp between 10 and 98
    hiring_success = max(10.0, min(98.0, base_success))
    
    # 2. Predict Retention Months
    base_retention = 12  # baseline 1 year
    
    if candidate.total_experience_years:
        # People with more experience tend to stay slightly longer (up to a point)
        base_retention += min(candidate.total_experience_years * 2, 24)
        
    if candidate.employment_type and "contract" in candidate.employment_type.lower():
        base_retention = min(base_retention, 6) # contractors stay shorter
        
    if candidate.notice_period:
        # those with longer notice periods are often more stable, heuristic
        if "60" in candidate.notice_period or "90" in candidate.notice_period or "2 month" in candidate.notice_period.lower():
            base_retention += 6
            
    # Add random variation (simulating unmeasured factors like culture fit)
    base_retention += int(random.uniform(-4, 8))
    
    predicted_retention = max(3, int(base_retention))
    
    # Update candidate model
    candidate.hiring_success_probability = round(hiring_success, 1)
    candidate.predicted_retention_months = predicted_retention
    
    return {
        "hiring_success_probability": candidate.hiring_success_probability,
        "predicted_retention_months": candidate.predicted_retention_months
    }
