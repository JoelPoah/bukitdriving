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

log_file_path = 'ryan.log'

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

# Example User-Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
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
def check_test(slots):
    
    wanted_days = {
        1:{"weekday":[11,12,18,19,25,26],"weekend":[0]},
        2:{"weekday":[1,2,8,9,10,11,12,13,14,15,16,22,23],"weekend":[0]},
    }
    try:
        date_now = datetime.now()
        slot_data = slots['data']['releasedSlotListGroupByDay']
        
        for key, value in slot_data.items():
            for index, slot_row in enumerate(value):
                date = slot_row['slotRefDate']
                # Convert date to a proper date format
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                start_time = slot_row['startTime']
                start_time = datetime.strptime(start_time, '%H:%M')
                # Filter only the wanted days for the specified month
                if date.month in wanted_days and date.day in wanted_days[date.month]['weekday'] and start_time.hour >=6:
                    return slot_row
                elif date.month in wanted_days and date.day in wanted_days[date.month]['weekend'] and start_time.hour >=6:
                    return slot_row
          
    except Exception as e:
        print('error in check_test()')
        print(e)    
    return None

def check(slots):
    print('executing check()')

    # Define the desired days for each month
    # 9:{"weekday":[2,3,4,5,6,9,10,11,12,13,16,17,18,19,20,23,24,25,26,27,30],"weekend":[1,7,8,14,15,21,22,28,29]},
    
    wanted_days = {
        11:{"weekday":[0],"weekend":[0]},
        12:{"weekday":[0],"weekend":[]},
        1:{"weekday":[4,5,11,12,18,19,25,26],"weekend":[0]}
    }

    try:
        date_now = datetime.now()
        slot_data = slots['data']['releasedSlotListGroupByDay']
        
        for key, value in slot_data.items():
            for index, slot_row in enumerate(value):
                date = slot_row['slotRefDate']
                # Convert date to a proper date format
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                start_time = slot_row['startTime']
                start_time = datetime.strptime(start_time, '%H:%M')
                # Filter only the wanted days for the specified month
                if date.month in wanted_days and date.day in wanted_days[date.month]['weekday'] and start_time.hour >=6:
                    return slot_row
                elif date.month in wanted_days and date.day in wanted_days[date.month]['weekend'] and start_time.hour >=6:
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
            username="105F26022004"
            password="020975"
            WebDriverWait(browser, wait_time).until(EC.presence_of_element_located((By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]")))
            login_user = browser.find_element(By.XPATH,'/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]')
            login_user.send_keys(username)
            # send_keys_slowly(login_user,username)
            login_pass = browser.find_element(By.XPATH,'/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/input[1]')
            login_pass.send_keys(password)
            # send_keys_slowly(login_pass,password)
            login_btn = browser.find_element(By.CLASS_NAME,'v-btn__content')
            login_btn.click()
            
            try:
                WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='v-snack__wrapper v-sheet theme--dark error']")))
                SendNotification('Temporary Error, Please Try Again Later')
                init_stop()
                break
            except:
                pass
            
            while "/booking/index" not in browser.current_url:
                captcha_code()
                time.sleep(5)
                
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
                    
                    test_slots = POST_REQ(AUTH,COOKIE,JSESSIONID,"https://booking.bbdc.sg/bbdc-back-service/api/booking/test/listPracticalTestSlotReleased",{
                    "courseType": CourseType,
                    "vehicleType": "Road",
                    "viewonly":True
                    })
                    
                    testslot = check_test(test_slots)
                    if testslot:
                        print('test slot found')
                        print(testslot)
                        SendNotification('Test Slot Found')
                        SendNotification(str(testslot))
                        break
                    
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
                            SendNotification(slots.message)
                    print('slots retrieved')
 
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
                        SendNotification('Booking Successful for Ryan')
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
                    time.sleep(randint(35,45))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        error = str(exc_type) + "\n" + str(fname) + "\n" + str(exc_tb.tb_lineno) + "\n" + str(e)
        # requests.post(f"https://api.callmebot.com/text.php?user=@JoelPP&text={urllib.parse.quote_plus(str(error))}")
        browser.quit()

