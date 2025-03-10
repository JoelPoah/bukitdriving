import json
import httpx
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import time
from selenium_stealth import stealth
from random import choice, randint
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
from seleniumwire.utils import decode as sw_decode
import jwt
import sys ,os

from selenium.webdriver.chrome.options import Options


import sys
import contextlib
import logging

log_file_path = 'joel.log'

# Configure logging to only write to the log file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
    ]
)

# Define a custom print function that logs messages and prints to console
def print(*args, **kwargs):
    message = ' '.join(map(str, args))
    logging.info(message)
    __builtins__.print(message, **kwargs)
    
    
# Open the log file in append mode and redirect stdout and stderr
with open(log_file_path, 'a') as log_file:
    with contextlib.redirect_stdout(log_file), contextlib.redirect_stderr(log_file):
        # Your script goes here
        print("This is a standard output message.")
        sys.stdout.flush()
        logging.info("This is an info message.")
        try:
            raise Exception("This is an error message.")
        except Exception as e:
            logging.error("An error occurred", exc_info=True)



people_msg = [
    "https://api.callmebot.com/text.php?user=@JoelPP&text=",
]


# browser = webdriver.Chrome()

chrome_options = Options()
chrome_options.add_argument("window-size=1920,1080")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

proxies = ["172.104.56.209:9050","188.166.239.48:3128","110.34.166.183:4153","167.71.220.29:7497","128.199.218.40:29492"]
proxy_string = proxies[randint(0,len(proxies)-1)]
chrome_options.add_argument("proxy-server="+proxy_string)

# Example User-Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

chrome_options.add_argument(f"user-agent={choice(user_agents)}")

browser = webdriver.Chrome(options=chrome_options)
# Use Selenium-Stealth to make this browser instance stealthy
# Updated list of random platforms
random_platforms = [
    "Win32",
    "Win64",
    "MacIntel",
    "Windows NT 10.0; Win64; x64",
]

random_platform = random_platforms[randint(0,len(random_platforms)-1)]

print("Random Platform: ",random_platform)


# Use Selenium-Stealth to make this browser instance stealthy
stealth(
    browser,
    languages=["en-US", "en"],  # Specify the languages supported by the browser
    vendor="Google Inc.",       # Set the vendor of the browser
    platform=random_platform,           # Specify the platform on which the browser is running
    webgl_vendor="Intel Inc.",   # Spoof the WebGL rendering engine vendor
    renderer= "Intel Iris OpenGL Engine",  # Spoof the WebGL rendering engine renderer
    fix_hairline= False         # Enable fixing a specific issue related to headless browsing
)

# Additional stealth configurations
browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
browser.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": choice(user_agents)})
browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
    "source": """
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3],
        });
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
    """
})




def init_stop():
    with open('./stop_signal.txt','w') as f:
        f.write('stop')

def SendNotification(text):
    max_chunk_size = 1000  # Maximum characters per batch
    length_of_text = len(text)
    current_index = 0

    while current_index < length_of_text:
        # Determine the end index for the current batch
        end_index = min(current_index + max_chunk_size, length_of_text)
        
        # Extract the current chunk of text
        current_chunk = text[current_index:end_index]
        
        #Sends the message
        for i in people_msg:
            url = i + current_chunk
            requests.post(url)
        
        # Move to the next chunk
        current_index = end_index        
    

def captcha_code():
    try:
        # browser.minimize_window()
        # time.sleep(0.5)
        # browser.maximize_window()
        catpcha = WebDriverWait(browser, 100).until(EC.presence_of_element_located((By.XPATH, "//div[@class='v-image__image v-image__image--cover']")))
        for request in browser.requests:
            if "getLoginCaptchaImage" in request.url or "getCaptchaImage" in request.url:
                data = sw_decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                data = data.decode("utf8")
                jwt_token = data
                pattern = r'"captchaToken":"([^"]*)"'
                match = re.search(pattern, jwt_token)
                captcha_token = match.group(1)
                decode_token = jwt.decode(captcha_token, options={"verify_signature": False})
                capatcha_input = browser.find_element(By.XPATH,"//label[normalize-space()='Captcha']/following::input[1]")
                capatcha_input.send_keys(decode_token["VER"])
                # send_keys_slowly(capatcha_input,decode_token["VER"])
                verify_button = ""
                print(browser.current_url)
                print("/login" in browser.current_url)
                if "/login" in browser.current_url:
                    verify_button = browser.find_element(By.XPATH,"//span[text()=' Verify ']")
                else:
                    verify_button = browser.find_element(By.XPATH,"//span[text()=' CONFIRM ']")
                    verify_button.click()
                verify_button.click()
                del browser.requests
                return
    except:
        pass        
    
def AUTH_Decrypt():
    print('executing AUTH_Decrypt()')
    for request in reversed(browser.requests):
        if "account/getUserProfile" in request.url:
                authToken = request.headers['Authorization']
                cookie = request.headers['Cookie']
                jsessionid = request.headers['jsessionid']
                return authToken, cookie,jsessionid
        else:
            pass
    return authToken,cookie,jsessionid

def CHECK_AUTO_MANUAL(authToken,cookie,jsessionid):
    print('DETECTING AUTO MANUAL')
    
    response = POST_REQ(authToken,cookie,jsessionid,"https://booking.bbdc.sg/bbdc-back-service/api/account/getUserProfile",{})
    
    data = response
    courseType = data['data']['enrolDetail']['courseType']
    
    print('courseType:',courseType)

    return courseType

    

def POST_REQ(auth, cookie, jsessionid, url, data={}):
    headers = {
        'Origin':'https://booking.bbdc.sg',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Authorization': auth,
        'Cookie': cookie,
        'Jsessionid': jsessionid
    }

    try:
        response = httpx.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        print('Response from POST request:', response.status_code, response.text)
        
        slots = response.json()

        
        return slots
    except httpx.RequestError as e:
        print(f"An error occurred: {e}")
        return None

def check_test(tests):
    
    month =[0]
    weekends = [2,3,9,10,16,17,23,24,30]
    try:
        date_now = datetime.now()
        slot_data = tests['data']['releasedSlotListGroupByDay']
        
        for key, value in slot_data.items():
            for index, slot_row in enumerate(value):
                date = slot_row['slotRefDate']
                # Convert date to a proper date format
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                start_time = slot_row['startTime']
                end_time = slot_row['endTime']
                

                if date.month in month and date.day in weekends:
                    SendNotification("test slot found in " + str(date) + " " + str(start_time) + " " + str(end_time))
                
    except Exception as e:
        print('error in check()')
        print(e)
    
    return None
    return

def check(slots):
    print('executing check()')

    # Define the desired days for each month
    wanted_days = {
        11: [23,24],
        12: [8,9]
    }

    try:
        date_now = datetime.now()
        slot_data = slots['data']['releasedSlotListGroupByDay']
        
        for key, value in slot_data.items():
            for index, slot_row in enumerate(value):
                date = slot_row['slotRefDate']
                # Convert date to a proper date format
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                # Filter only the wanted days for the specified month
                if date.month in wanted_days and date.day in wanted_days[date.month]:
                    start_time = slot_row['startTime']
                    start_time = datetime.strptime(start_time, '%H:%M')
                    start_time_1_5_hours = start_time - timedelta(hours=1.5)
                    date_now_str = date_now.strftime('%H:%M')
                    
                    # Debug prints to trace the computation values
                    print(f"Current time: {date_now_str}")
                    print(f"Slot time: {start_time.strftime('%H:%M')}")
                    print(f"Slot time minus 1.5 hours: {start_time_1_5_hours.strftime('%H:%M')}")

                    # Check the condition for time and day
                    if date.date() == date_now.date() and 1==2:
                        # Slot is today
                        if start_time.hour >= 6 and date_now_str <= start_time_1_5_hours.strftime('%H:%M'):
                            print('found the slot for today')
                            SendNotification("Attempting to book slot for Joel")
                            return slot_row
                    else:
                        # Slot is not today
                        if start_time.hour >= 6:
                            print('found the slot for another day')
                            SendNotification("Attempting to book slot for Joel")
                            return slot_row
    except Exception as e:
        print('error in check()')
        print(e)
    
    return None

# Send keys with a delay between each character
def send_keys_slowly(element, text, delay=0):
    for char in text:
        element.send_keys(char)
        time.sleep(delay)
        

wait_time = 100
try:
    browser.get('https://booking.bbdc.sg/#/login?redirect=%2Fbooking')
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    error = str(exc_type) + "\n" + str(fname) + "\n" + str(exc_tb.tb_lineno) + "\n" + str(e)
    # requests.post(f"https://api.callmebot.com/text.php?user=@JoelPP&text={urllib.parse.quote_plus(str(error))}")
    browser.quit()

running3 = True
while True:
    try:
        while running3:
            time.sleep(randint(1,3))
            username="105F02262004"
            password="020975"
            WebDriverWait(browser, wait_time).until(EC.presence_of_element_located((By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]")))
            login_user = browser.find_element(By.XPATH,'/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]')
            #login_user.send_keys(username)
            send_keys_slowly(login_user,username)
            login_pass = browser.find_element(By.XPATH,'/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/input[1]')
            #login_pass.send_keys(password)
            send_keys_slowly(login_pass,password)
            login_btn = browser.find_element(By.CLASS_NAME,'v-btn__content')
            login_btn.click()
            
            try:
                WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='v-snack__wrapper v-sheet theme--dark error']")))
                SendNotification('Temporary Error, Please Try Again Later')
                init_stop()
                break
            except:
                pass
            
            while "/booking/index" not in browser.current_url:
                captcha_code()
                time.sleep(1)
                
            AUTH,COOKIE,JSESSIONID=AUTH_Decrypt()
            
            CourseType = CHECK_AUTO_MANUAL(AUTH,COOKIE,JSESSIONID)
            print(AUTH + "\n" + COOKIE + "\n" + JSESSIONID)
            
            if CourseType == "3A":
                CourseType = "3A"
            else:
                CourseType = "3C"
            refresh = True
            count = 0
            fail_counts = 0
            while refresh:
                try:
                    
                    if count % 10 == 0:
                        tests = POST_REQ(AUTH,COOKIE,JSESSIONID,"https://booking.bbdc.sg/bbdc-back-service/api/booking/test/listPracticalTestSlotReleased",{
                            "courseType": "3C",
                            "vehicleType": "Road",
                            "viewOnly": True
                        })

                        check_test(tests)
                    
                    
                    slots= POST_REQ(AUTH,COOKIE,JSESSIONID,"https://booking.bbdc.sg/bbdc-back-service/api/booking/c3practical/listC3PracticalSlotReleased",{
                    "courseType": CourseType,
                    "insInstructorId": "",
                    "stageSubDesc": "Practical Lesson",
                    "subVehicleType": None,
                    "subStageSubNo": None
                    })
                    if slots['success'] != True:
                        fail_counts+=1
                        print("this is fail count: ",fail_counts)
                        if fail_counts >=1:
                            init_stop()
                            SendNotification(slots['message'])
                    print('slots retrieved')
                    # print("before json loads ",type(slots))
 
                    print("after json loads ",type(slots))
                    single_wanted_booking = check(slots)
                except Exception as e:
                    print('error in slots retrieval')
                    print(e)
                    single_wanted_booking = None
                count += 1
                print('executing count:',count)
                if single_wanted_booking:
                    print('single wanted booking found')
                    slotId = single_wanted_booking['slotId']
                    slotIdEnc = single_wanted_booking['slotIdEnc']
                    bookingProgressEnc = single_wanted_booking['bookingProgressEnc']
                    captcha_call = POST_REQ(AUTH,COOKIE,JSESSIONID,"https://booking.bbdc.sg/bbdc-back-service/api/booking/manage/getCaptchaImage",{})
                    #captcha_call = captcha_call.json()
                    captcha_token = captcha_call['data']['captchaToken']
                    verifyCodeId = captcha_call['data']['verifyCodeId']
                    captcha_word = jwt.decode(captcha_token, options={"verify_signature": False})['VER']
                    print('captcha retrieved now booking call')
                    booking_call = POST_REQ(AUTH,COOKIE,JSESSIONID,"https://booking.bbdc.sg/bbdc-back-service/api/booking/c3practical/callBookC3PracticalSlot",
                                        {
                    "courseType": CourseType,
                    "slotIdList": [
                    slotId
                    ],
                    "encryptSlotList": [
                    {
                    "slotIdEnc": slotIdEnc,
                    "bookingProgressEnc": bookingProgressEnc
                    }
                    ],
                    "verifyCodeId": verifyCodeId,
                    "verifyCodeValue": captcha_word,
                    "captchaToken": captcha_token,
                    "insInstructorId": "",
                    "subVehicleType": None,
                    })
                    date = single_wanted_booking['slotRefDate']
                    print('date:',date)
                    start_time = single_wanted_booking['startTime']
                    print('start_time:',start_time)
                    end_time = single_wanted_booking['endTime']
                    print('end_time:',end_time)
                    # booking_call = booking_call.json()
                    if booking_call["data"]['bookedPracticalSlotList'][-1]['success'] == True:
                        print('Booking Successful')
                        SendNotification('Booking Successful for joel.py')
                        SendNotification(str(booking_call))
                        SendNotification(str(date))
                        SendNotification(start_time)
                        SendNotification(end_time)
                        SendNotification(booking_call["data"]['bookedPracticalSlotList'][-1]['message'])
                        time.sleep(5)
                    else:
                        print('Booking Failed')
                        SendNotification('Booking Failed')
                        SendNotification(str(booking_call))
                        SendNotification(str(date))
                        SendNotification(start_time)
                        SendNotification(end_time)
                        SendNotification(booking_call["data"]['bookedPracticalSlotList'][-1]['message'])
                        time.sleep(5)
                else:
                    # sleep for 100 seconds to allow the server to process the request
                    time.sleep(randint(30,40))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        error = str(exc_type) + "\n" + str(fname) + "\n" + str(exc_tb.tb_lineno) + "\n" + str(e)
        # requests.post(f"https://api.callmebot.com/text.php?user=@JoelPP&text={urllib.parse.quote_plus(str(error))}")
        browser.quit()

