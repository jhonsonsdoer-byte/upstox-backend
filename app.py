from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
# Super CORS fix for Render
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization", "X-Upstox-Token"])

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Upstox-Token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

UPSTOX_BASE = "https://api.upstox.com/v2"

@app.route("/")
def home():
    return jsonify({"status": "Upstox AI Backend LIVE", "version": "v4-fixed", "cors": "enabled"})

@app.route("/api/ltp")
def get_ltp():
    token = request.headers.get("X-Upstox-Token") or request.args.get("token")
    instrument = request.args.get("instrument", "NSE_INDEX|Nifty 50")
    if not token:
        return jsonify({"error": "Token missing"}), 400
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    url = f"{UPSTOX_BASE}/market-quote/ltp?instrument_key={instrument}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/candles")
def get_candles():
    token = request.headers.get("X-Upstox-Token") or request.args.get("token")
    instrument = request.args.get("instrument", "NSE_INDEX|Nifty 50")
    interval = request.args.get("interval", "15minute")
    if not token:
        return jsonify({"error": "Token missing"}), 400
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    to_date = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    url_hist = f"{UPSTOX_BASE}/historical-candle/{instrument}/{interval}/{from_date}/{to_date}"
    url_intraday = f"{UPSTOX_BASE}/historical-candle/intraday/{instrument}/{interval}"
    try:
        hist = requests.get(url_hist, headers=headers, timeout=15).json()
        intra = requests.get(url_intraday, headers=headers, timeout=15).json()
        return jsonify({"historical": hist, "intraday": intra})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
