import json
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
    # "https://api.callmebot.com/text.php?user=@JoelPP&text=",
    "https://api.callmebot.com/text.php?user=@Jessieraven&text=",
    "https://api.telegram.org/bot6786500283:AAEI6WNk1ZGB7uLtugUbLR_iKYbxwoLM2EE/sendMessage?chat_id=-4188476384&text="
]





browser = webdriver.Chrome()
# browser = webdriver.Chrome(options=chrome_options)
stealth(browser,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

def RetrieveKeyData(data):
        data = json.loads(data)
        slot_data = data['data']['releasedSlotListGroupByDay']

        print('slot data retrieved')

        date_now = datetime.now()
        # for testing purposes hardcode the date_now to a specific datetime 
        # date_now = datetime.strptime('16/09/2024 07:00','%d/%m/%Y %H:%M')
        print('date now: ',date_now)

        if slot_data or slot_data != None or slot_data != [] or slot_data != {} or slot_data != "null" or slot_data != "undefined" or slot_data != "":

            print('success if dict type', type(slot_data))

            # take out all the keys ,values['startTime,'endTime']

            msg=""

            for key, value in slot_data.items():
                # print(key, value)
                for index,slot_row in enumerate(value):
                    date = slot_row['slotRefDate']
                    start_time = slot_row['startTime']
                    userFixGrpNo = slot_row['userFixGrpNo']
                    print('userFixGrpNo: ',userFixGrpNo)
                    start_time_str = start_time
                    print('start time retrieved')


                    end_time = slot_row['endTime']
                    total_fee = slot_row['totalFee']


                    # convert date to a proper date format
                    date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

                    print('before start_time is stripped to datetime' , start_time)

                    start_time = datetime.strptime(start_time,'%H:%M')

                    print('after start_time is stripped to datetime' , start_time)
                    start_time = start_time.replace(year=date.year, month=date.month, day=date.day,hour=start_time.hour,minute=start_time.minute)

                    print('after start_time is stripped to datetime with replacement' , start_time)
                    start_time_minus_1hours = start_time - timedelta(hours=1)
                    print('start time converted')

                    # added catch
                    try:
                        # if it is the desired month and also 2 hours before the slot
                        #if date.month in [5] and date_now<=(start_time_minus_2hours):
                        #   '''
                        #  removed 2 hour wait time need instant response
                        #  '''
                        if date.month in [6] :
                           print('the index of the length of session that begins to be suitable is: ',index)
                           msg = "Found slot proceed to book ! Date: \n" + str(date)+ "Start Time: " + str(start_time) + "End Time: " + str(end_time) + "Current time: " + str(date_now) + "Group: " + str(userFixGrpNo) +  "." 
                           SendNotification(msg)
                           return True,index
                        else:
                            msg = "slot did not meet hour criteria " + str(date)

                            continue
                    except:
                        SendNotification('Returned False meaning slot did not meet a 2 hour criteria & desired month')

                return False,0


                # SendNotification(str(msg)) 
                ''' 
                For Auto Booking its not necessary to notify available slots but auto take the slot and book it
                '''
        else:
            return False,0



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

def process_json_available_slots():
    try:

        booking_ready = WebDriverWait(browser, 100).until(EC.presence_of_element_located((By.XPATH, "//div[@class='container container--fluid']")))
        print('booking ready')
        for request in reversed(browser.requests):
            print('yes reverse works')
            if "c3practical/listC3PracticalSlotReleased" in request.url:
                print('inside the network traffic')
                data = sw_decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                data = data.decode("utf8")
                print('if is str is working',type(data))
                Wanted_Month,IndexOfSlots = RetrieveKeyData(data)

                return Wanted_Month,IndexOfSlots
            else:
                pass
    except:
            print('error in process_json_available_slots() or RetrieveKeyData()')
            # SendNotification('ERROR process_json_available_slots()')
            return False,0
            
def filter_wanted_slots(slot_data):
    # take the keys of all the slot_data 
    dates_available = slot_data.keys()
    # convert to a string 
    dates_available = [str(date) for date in dates_available]
    return dates_available

    

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
    # Execute JavaScript to retrieve all localStorage data
    local_storage = browser.execute_script("return window.localStorage.getItem('vuex');")

    # Convert the localStorage string to a dictionary
    local_storage = json.loads(local_storage)

    authToken = local_storage['user']['authToken']
    # remove the % from the token
    authToken = authToken.replace('%',' ')


    # authorization = local_storage['user']['authToken']
    # print('authorization retrieved',authorization)


    # WELL TECHNICALLY COOKIE IS JUST bbdc-token=${authToken}

    # cookie = 'bbdc-token='+authToken

    # Retrieve cookie
    cookies = browser.get_cookies()
    cookie = next((cookie['value'] for cookie in cookies if cookie['name'] == 'bbdc-token'), None)

    for request in reversed(browser.requests):
        if "account/getUserProfile" in request.url:
                jsessionid = request.headers['jsessionid']
                # data = data.decode("utf8")
                # data = json.loads(data)
                # Jsessionid = data['data']['jsessionid']
        else:
            pass
    return authToken,cookie,jsessionid

def POST_REQ(auth, cookie, jsessionid, url, data):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth,
        'Cookie': cookie,
        'Jsessionid': jsessionid
    }

    print('this is the headers',headers)
    response = requests.post(url, headers=headers,data=data)
    print('response from post request',response)

# Example usage:
# auth = "Bearer your_token"
# cookie = "your_cookie"
# jsessionid = "your_jsessionid"
# url = "https://example.com/api"
# data = {"key": "value"}
# response = POST_REQ(auth, cookie, jsessionid, url, data)




wait_time = 100
browser.get('https://booking.bbdc.sg/#/login?redirect=%2Fbooking')
running3 = True
while True:
    try:
        while running3:
            username="337a18092001"
            password="112220"
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
                    print("im here")
                    Book_slots = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//body//div[@id='app']//div[@class='row']//div[@class='row']//div[1]//div[1]//button[1]//span[1]")))
                    Book_slots.click()
                    No_Fix_Instructor= WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='radiogroup']//div[1]//div[1]//div[1]")))
                    No_Fix_Instructor.click()
                    Next = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='NEXT']")))
                    Next.click()
                    AUTH,COOKIE,JSESSIONID=AUTH_Decrypt()

                    print("returned data")
                    print(AUTH,"\n",COOKIE,"\n",JSESSIONID)
                    # res = POST_REQ(AUTH,COOKIE,JSESSIONID,"https://booking.bbdc.sg/bbdc-back-service/api/booking/c3practical/listC3PracticalTrainings",{"courseType": "3C", "pageNo": 1, "pageSize": 10, "courseSubType": "Practical"})


                    # sleep for 20 seconds to allow the server to process the request
                    time.sleep(100)

                    try:
                        WebDriverWait(browser, 35).until(EC.presence_of_all_elements_located((By.XPATH,"//div[@class='v-snack__wrapper v-sheet theme--dark error']")))

                    except:
                        hehe = False
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        error = str(exc_type) + "\n" + str(fname) + "\n" + str(exc_tb.tb_lineno) + "\n" + str(e)
        # requests.post(f"https://api.callmebot.com/text.php?user=@JoelPP&text={urllib.parse.quote_plus(str(error))}")
        browser.refresh()

