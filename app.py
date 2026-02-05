from flask import Flask, request, jsonify
from bson import ObjectId
from db import users_collection, chat_collection, assessment_collection, alerts_collection

app = Flask(__name__)

# ------------------ HOME ROUTE ------------------
@app.route("/")
def home():
    return "Mental Health AI Backend Running 🚀"


# ------------------ USER REGISTRATION ------------------
@app.route("/register", methods=["POST"])
def register_user():
    data = request.json

    user = {
        "fullName": data.get("fullName"),
        "email": data.get("email"),
        "age": data.get("age"),
        "gender": data.get("gender"),
        "profession": data.get("profession"),
        "workMode": data.get("workMode"),
        "stressLevel": data.get("stressLevel"),
        "sleepHours": data.get("sleepHours")
    }

    result = users_collection.insert_one(user)

    return jsonify({
        "message": "User Registered Successfully",
        "user_id": str(result.inserted_id)
    })


# ------------------ SAVE CHAT MESSAGE ------------------
@app.route("/chat", methods=["POST"])
def save_chat():
    data = request.json

    chat = {
        "userId": ObjectId(data.get("userId")),
        "message": data.get("message")
    }

    chat_collection.insert_one(chat)

    return jsonify({"message": "Chat Saved"})


# ------------------ RISK DETECTION FUNCTION ------------------
def check_user_risk(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    assessment = assessment_collection.find_one()

    if not user or not assessment:
        return "No data"

    risk_score = 0
    reasons = []

    if assessment.get("StressScore", 0) >= 8:
        risk_score += 1
        reasons.append("High Stress")

    if user.get("sleepHours", 8) < 6:
        risk_score += 1
        reasons.append("Low Sleep")

    if assessment.get("BurnoutRisk", "") == "High":
        risk_score += 1
        reasons.append("Burnout Risk")

    if risk_score >= 2:
        alert = {
            "userId": ObjectId(user_id),
            "riskLevel": "High",
            "reason": ", ".join(reasons)
        }
        alerts_collection.insert_one(alert)
        return "🚨 ALERT GENERATED"

    return "User Stable"


# ------------------ ANALYZE USER ------------------
@app.route("/analyze/<user_id>", methods=["GET"])
def analyze_user(user_id):
    result = check_user_risk(user_id)
    return jsonify({"status": result})


# ------------------ VIEW ALERTS ------------------
@app.route("/alerts/<user_id>", methods=["GET"])
def get_alerts(user_id):
    alerts = list(alerts_collection.find({"userId": ObjectId(user_id)}))
    for alert in alerts:
        alert["_id"] = str(alert["_id"])
        alert["userId"] = str(alert["userId"])

    return jsonify(alerts)


# ------------------ RUN SERVER ------------------
if __name__ == "__main__":
    app.run(debug=True)
