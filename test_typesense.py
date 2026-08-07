import httpx

# Use your host and key
HOST = "fas0pie5tckr6g2hp-1.a2.typesense.net"
API_KEY = "dtOFl3ANkvNJr7DUrOAmIWTZO2AQSVNR" # Put your real API key here

url = f"https://{HOST}:443/health"
headers = {"X-TYPESENSE-API-KEY": API_KEY}

try:
    print(f"Connecting to {url}...")
    # We disable proxy usage explicitly here to rule out proxy interference
    with httpx.Client(verify=True, transport=httpx.HTTPTransport(local_address="0.0.0.0")) as client:
        response = client.get(url, headers=headers, timeout=15.0)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")