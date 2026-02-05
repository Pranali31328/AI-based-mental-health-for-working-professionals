from db import users_collection, assessment_collection, alerts_collection

def check_user_risk(user_id):
    user = users_collection.find_one({"_id": user_id})
    assessment = assessment_collection.find_one({"userId": user_id})

    if not user or not assessment:
        return "No data"

    risk_score = 0
    reasons = []

    if assessment.get("stressScore", 0) >= 8:
        risk_score += 1
        reasons.append("High Stress")

    if user.get("sleepHours", 8) < 6:
        risk_score += 1
        reasons.append("Low Sleep")

    if assessment.get("burnoutRisk", "") == "High":
        risk_score += 1
        reasons.append("Burnout Risk")

    if risk_score >= 2:
        alert = {
            "userId": user_id,
            "riskLevel": "High",
            "reason": ", ".join(reasons)
        }
        alerts_collection.insert_one(alert)
        return "ALERT GENERATED"

    return "User Stable"
