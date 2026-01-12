import requests
import json
import math

url = "http://localhost:8000/predict"

# 1. Valid Payload
valid_payload = {
    "Open": 150.0,
    "High": 155.0,
    "Low": 149.0,
    "Close": 153.0,
    "Volume": 1000000,
    "Adj_Close": 153.0
}
print("--- TEST 1: Valid Payload ---")
try:
    r = requests.post(url, json=valid_payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(e)


# 2. Payload with NaN (simulating missing data)
# Note: standard json module does not produce NaN, but simplejson or others might, 
# or if we construct dict manualy and pass to requests using data=str(payload)
# requests 'json' parameter handles NaN by producing valid JSON 'null' ONLY IF allow_nan is False?
# Actually default json encoder produces NaN which is invalid JSON.
nan_payload = {
    "Open": 150.0,
    "High": 155.0,
    "Low": 149.0,
    "Close": 153.0,
    "Volume": 1000000,
    "Adj_Close": float('nan')
}
print("\n--- TEST 2: NaN Payload (Uncleaned) ---")
try:
    # requests uses json.dumps which ALLOWS NaN by default, producing invalid JSON "Adj_Close": NaN
    r = requests.post(url, json=nan_payload) 
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Exception: {e}")

# 3. Payload with Cleaned NaNs (My Fix)
def clean_float(val):
    return float(val) if not math.isnan(val) else 0.0

cleaned_payload = {
    "Open": 150.0,
    "High": 155.0,
    "Low": 149.0,
    "Close": 153.0,
    "Volume": 1000000,
    "Adj_Close": clean_float(float('nan')) 
}
print("\n--- TEST 3: Cleaned Payload ---")
try:
    r = requests.post(url, json=cleaned_payload)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(e)
