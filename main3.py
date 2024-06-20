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
from random import randint
import requests
import urllib.parse
from datetime import datetime, timedelta
import re
from seleniumwire.utils import decode as sw_decode
import jwt
import sys ,os

from selenium.webdriver.chrome.options import Options

people_msg = [
    "https://api.callmebot.com/text.php?user=@JoelPP&text=",
    # "https://api.callmebot.com/text.php?user=@Jessieraven&text=",
    # "https://api.telegram.org/bot6786500283:AAEI6WNk1ZGB7uLtugUbLR_iKYbxwoLM2EE/sendMessage?chat_id=-4188476384&text="
]



proxies = ["172.104.56.209:9050","188.166.239.48:3128","110.34.166.183:4153","167.71.220.29:7497","128.199.218.40:29492"]

# browser = webdriver.Chrome()

chrome_options = Options()
chrome_options.add_argument("proxy-server="+proxies[randint(0,len(proxies)-1)])
browser = webdriver.Chrome(options=chrome_options)
# Use Selenium-Stealth to make this browser instance stealthy
random_platforms = [
    "Win32",
    "Win64",
    "MacIntel",
    "Windows NT 10.0; Win64; x64",
    "Linux x86_64",
    "Linux i686"
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
        browser.minimize_window()
        browser.maximize_window()
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
                # data = data.decode("utf8")
                # data = json.loads(data)
                # Jsessionid = data['data']['jsessionid']
        else:
            pass
    return authToken,cookie,jsessionid

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
        return response
    except httpx.RequestError as e:
        print(f"An error occurred: {e}")
        return None

def check(slots):
    print('executing check()')
    month = 6
    wanted_days = [22,23,24,25,26,27,28,30]
    try:
        slot_data = slots['data']['releasedSlotListGroupByDay']
        for key,value in slot_data.items():
            for index,slot_row in enumerate(value):
                date = slot_row['slotRefDate']
                # convert date to a proper date format
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                # filter only month
                start_time = slot_row['startTime']
                start_time = datetime.strptime(start_time, '%H:%M')
                if date.month == month:
                    # filter only the wanted days
                    if date.day in wanted_days and start_time.hour >= 12:
                        print('found the slot')
                        return slot_row
    except Exception as e:
        print('error in check()')
        print(e)
    return None


wait_time = 100
browser.get('https://booking.bbdc.sg/#/login?redirect=%2Fbooking')
running3 = True
while True:
    try:
        while running3:
            username="105F26022004"
            password="020975"
            WebDriverWait(browser, wait_time).until(EC.presence_of_element_located((By.XPATH, "/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]")))
            login_user = browser.find_element(By.XPATH,'/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/input[1]')
            login_user.send_keys(username)
            login_pass = browser.find_element(By.XPATH,'/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/form[1]/div[1]/div[3]/div[1]/div[1]/div[1]/div[1]/input[1]')
            login_pass.send_keys(password)
            login_btn = browser.find_element(By.CLASS_NAME,'v-btn__content')
            login_btn.click()
            captcha_code()
            running4 = True
            running3 = False
        while running4:
            browser.maximize_window()
            sidebar = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='decrease']//button[@type='button']")))
            browser.minimize_window()
            browser.maximize_window()
            browser.minimize_window()
            browser.maximize_window()
            # needs to maximized to click later hopefully rand sleeps help to bypass the bot detection
            if "/home/index" in browser.current_url:
                try:
                    sidebar = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='decrease']//button[@type='button']")))
                    sidebar.click()
                    sidebar.click()
                except:
                    pass
                Booking_button = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Booking']")))
                Booking_button.click()
            running2 = True
            running4 = False
        while running2:
            if "/home/index" in browser.current_url:
                sidebar = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='decrease']//button[@type='button']")))
                sidebar.click()
                sidebar.click()
                Booking_button = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Booking']")))
                Booking_button.click()
            if "/login" in browser.current_url:
                running2 = False
                running3 = True
                running4 = False
            if "/chooseSlot" in browser.current_url:
                running = True
                running2 = False
            ## practical
            grey_screen = WebDriverWait(browser, wait_time).until(EC.invisibility_of_element_located((By.XPATH,"//div[@class='v-overlay__scrim']")))
            Booking_Dropdown = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/nav/div[1]/div[3]/div[2]/div/div[1]')))
            Booking_Dropdown.click()
            Practical = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Practical']")))
            grey_screen = WebDriverWait(browser, wait_time).until(EC.invisibility_of_element_located((By.XPATH,"//div[@class='v-overlay__scrim']")))
            Practical.click()
            grey_screen = WebDriverWait(browser, wait_time).until(EC.invisibility_of_element_located((By.XPATH,"//div[@class='v-overlay__scrim']")))
            hehe = True
            while hehe:
                if "/login" in browser.current_url:
                    running2 = False
                    running3 = True
                    running4 = True
                    hehe = False
                if "/booking/chooseSlot" in browser.current_url:
                    hehe = False
                else:
                    if "/home/index" in browser.current_url:
                        try:
                            sidebar = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='decrease']//button[@type='button']")))
                            sidebar.click()
                            sidebar.click()
                        except:
                            pass
                        Booking_button = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Booking']")))
                        Booking_button.click()
                    Book_slots = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//body//div[@id='app']//div[@class='row']//div[@class='row']//div[1]//div[1]//button[1]//span[1]")))
                    Book_slots.click()
                    No_Fix_Instructor= WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='radiogroup']//div[1]//div[1]//div[1]")))
                    No_Fix_Instructor.click()
                    Next = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='NEXT']")))
                    Next.click()
                    #try:
                    #    WebDriverWait(browser, 35).until(EC.presence_of_all_elements_located((By.XPATH,"//div[@class='v-snack__wrapper v-sheet theme--dark error']")))
                    #except:
                    #    hehe = False
                    AUTH,COOKIE,JSESSIONID=AUTH_Decrypt()

                    print(AUTH + "\n" + COOKIE + "\n" + JSESSIONID)


                    refresh = True
                    count = 0
                    while refresh:

                        try:
                            slots= POST_REQ(AUTH,COOKIE,JSESSIONID,"https://booking.bbdc.sg/bbdc-back-service/api/booking/c3practical/listC3PracticalSlotReleased",{
                            "courseType": "3C",
                            "insInstructorId": "",
                            "stageSubDesc": "Practical Lesson",
                            "subVehicleType": None,
                            "subStageSubNo": None
                            })

                            print('slots retrieved')

                            # print("before json loads ",type(slots))

                        
                            slots = slots.json()    

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

                            captcha_call = captcha_call.json()
                            captcha_token = captcha_call['data']['captchaToken']
                            verifyCodeId = captcha_call['data']['verifyCodeId']
                            captcha_word = jwt.decode(captcha_token, options={"verify_signature": False})['VER']

                            print('captcha retrieved now booking call')
                            booking_call = POST_REQ(AUTH,COOKIE,JSESSIONID,"https://booking.bbdc.sg/bbdc-back-service/api/booking/c3practical/callBookC3PracticalSlot",
                                                {
                            "courseType": "3C",
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


                            booking_call = booking_call.json()



                            if booking_call["data"]['bookedPracticalSlotList'][-1]['success'] == True:
                                print('Booking Successful')
                                SendNotification('Booking Successful')
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
                            time.sleep(randint(20,30))

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        error = str(exc_type) + "\n" + str(fname) + "\n" + str(exc_tb.tb_lineno) + "\n" + str(e)
        # requests.post(f"https://api.callmebot.com/text.php?user=@JoelPP&text={urllib.parse.quote_plus(str(error))}")
        browser.refresh()

