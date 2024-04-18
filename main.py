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
    "https://api.callmebot.com/text.php?user=@JoelPP&text=",
    # "https://api.callmebot.com/text.php?user=@Jessieraven&text=",
    # "https://api.telegram.org/bot6786500283:AAEI6WNk1ZGB7uLtugUbLR_iKYbxwoLM2EE/sendMessage?chat_id=-4188476384&text="
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
                    start_time_minus_2hours = start_time - timedelta(hours=2)
                    print('start time converted')

                    # added catch
                    if date.month in [4]:
                        SendNotification('Found a slot in September for Joel')
                        try:
                            msg+="OMG BOOKING FOUND but not booked yet please wait for confirmation booking!\n"
                            print('Date: ',date ,"Start: ", start_time_str, "End: ", end_time, "Total Fee: ", total_fee , "UserFixGrpNo: ", userFixGrpNo)
                            msg += f"Date: {date} Start: {start_time_str} End: {end_time} Total Fee: {total_fee} UserFixGrpNo: {userFixGrpNo}\n"
                            SendNotification(str(msg))
                        except:
                            SendNotification('There was a possible booking found but error in sending & formatting')


                    try:

                        # if it is the desired month and also 2 hours before the slot
                        if date.month in [4] and date_now<=(start_time_minus_2hours):
                            print('the index of the length of session that begins to be suitable is: ',index)
                            SendNotification('Returning True and initializing the booking process')

                            return True,index
                        else:
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
                    time.sleep(randint(1,3))
                else:
                    verify_button = browser.find_element(By.XPATH,"//span[text()=' CONFIRM ']")
                verify_button.click()
                del browser.requests
                return
    except:
        pass        
    

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
                        hehe = False
                    print("im here")
                    Book_slots = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//body//div[@id='app']//div[@class='row']//div[@class='row']//div[1]//div[1]//button[1]//span[1]")))
                    Book_slots.click()
                    No_Fix_Instructor= WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='radiogroup']//div[1]//div[1]//div[1]")))
                    No_Fix_Instructor.click()
                    Next = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='NEXT']")))
                    Next.click()
                    try:
                        WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH,"//div[@class='v-snack__wrapper v-sheet theme--dark error']")))
                        time.sleep(randint(15,60))
                    except:
                        hehe = False
                    

            

            # test
            # Test = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[normalize-space()='Test']")))
            # grey_screen = WebDriverWait(browser, wait_time).until(EC.invisibility_of_element_located((By.XPATH,"//div[@class='v-overlay__scrim']")))
            # Test.click()
            # grey_screen = WebDriverWait(browser, wait_time).until(EC.invisibility_of_element_located((By.XPATH,"//div[@class='v-overlay__scrim']")))
            # Book_slots = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='v-window-item v-window-item--active']//span[@class='v-btn__content'][normalize-space()='Book Slot']")))
            # Book_slots.click()
            # Continue = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Continue']")))
            # Continue.click()
            # Accept_terms = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='v-card__actions']//div[@class='v-input--selection-controls__ripple']")))
            # Accept_terms.click()
            # Confirm = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='v-card__actions']//span[@class='v-btn__content'][normalize-space()='Confirm']")))
            # Confirm.click()
            # grey_screen = WebDriverWait(browser, wait_time).until(EC.invisibility_of_element_located((By.XPATH,"//div[@class='v-overlay__scrim']")))
            
            # TPDS
            # WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, "//div[9]//div[1]//button[1]//span[1]")))
            # TPDS_button = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[9]//div[1]//button[1]//span[1]")))
            # TPDS_button.click()
            # WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='Continue']")))
            # Continue = WebDriverWait(browser, 20).until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Continue']")))
            # time.sleep(1)
            #Continue.click()
            running = True
            while running:
                if "/login" in browser.current_url:
                    running = False
                    running2 = False
                    running3 = True
                    running4 = True
                grey_screen = WebDriverWait(browser, wait_time).until(EC.invisibility_of_element_located((By.XPATH,"//div[@class='v-overlay__scrim']")))
                WebDriverWait(browser, wait_time).until(EC.presence_of_element_located((By.XPATH, "//div[@class='v-calendar-weekly__day v-present' or @class='v-calendar-weekly__day v-future']//*")))

                # DateReleasedSpan = WebDriverWait(browser, wait_time).until(EC.presence_of_all_elements_located((By.XPATH, "//body//div[@id='app']//div[@class='v-main__wrap']//div[@class='chooseSlot']//div[@class='dateList dateList-web d-none d-md-flex']")))


                span1 = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//body//div[@id='app']//div[@class='v-main__wrap']//div[@class='chooseSlot']//div[@class='dateList dateList-web d-none d-md-flex']//button[1]")))
                span1.click()

                # Sends next few closest slots
                # processed_available_slots = process_json_available_slots()
                print(f'clicked the 1st button')
                grey_screen = WebDriverWait(browser, wait_time).until(EC.invisibility_of_element_located((By.XPATH,"//div[@class='v-overlay__scrim']")))
                WebDriverWait(browser, wait_time).until(EC.presence_of_element_located((By.XPATH, "//div[@class='v-calendar-weekly__day v-present' or @class='v-calendar-weekly__day v-future']//*")))
                suitable_month,suitable_index = process_json_available_slots()


                    

                '''
                In theory you do not need to click the 2nd and 3rd button as we only want the closest slots now 
                '''
                        
                ''' 
                I want the Bot to auto book the slot with notification if processed_available_slots is true means it detected a month that we wanted therefore we activate the booking process

                for trial purposes we can set the month to include september which is the earliest date for booking currently
                '''

                print('suitable_month bool value: ', suitable_month)

                if suitable_month == True:


                    print('inside the booking process')

                    dates = browser.find_elements(By.XPATH, "//div[@class='v-calendar-weekly__day v-present' or @class='v-calendar-weekly__day v-future']")
                    wanted_dates = [18,19,21,22,23,25,26,28,29,30] ## this is for april

                    for each_date in dates:
                        try:
                            child_item = each_date
                            parent_of_div = child_item.find_elements(By.TAG_NAME,"div")
                            child_child_item = parent_of_div[0].find_elements(By.TAG_NAME,"span")

                            if 'disabled-text' not in (child_child_item[0].get_attribute('class').split()) and int(child_item.text) in wanted_dates :
                                print("Found slot")
                                child_item.click() ## This becomes a function later to execute the booking process

                                grey_screen = WebDriverWait(browser, wait_time).until(EC.invisibility_of_element_located((By.XPATH,"//div[@class='v-overlay__scrim']")))

                                # chooseSlotsAvailable = WebDriverWait(browser, wait_time).until(EC.presence_of_element_located((By.CLASS_NAME,"col-mid col col-4")))
                                # chooseSlots = browser.find_elements(By.CLASS_NAME,"col-mid col col-4")

                                # will Xpath instead
                                chooseSlotsAvailable = WebDriverWait(browser, wait_time).until(EC.presence_of_element_located((By.XPATH, "//div[@class='col-mid col col-4']")))
                                chooseSlots = browser.find_elements(By.XPATH,"//div[@class='col-mid col col-4']")

                                print('found chooseSlots !')

                                chooseSlotsContentSession = chooseSlots[0].find_elements(By.XPATH,"//div[@class='sessionContent sessionContent-web d-none d-md-flex']")
                                print('found chooseSlotsContentSession !')
                                all_slots = browser.find_elements(By.XPATH,"//div[@class='col-mid col col-4']//div[@class='sessionContent sessionContent-web d-none d-md-flex']//div[@class='sessionCard']")

                                print('all slots found !')
                                print('dtype of all_slots', type(all_slots))

                                print('length of all_slots', len(all_slots))
                                grey_screen = WebDriverWait(browser, wait_time).until(EC.invisibility_of_element_located((By.XPATH,"//div[@class='v-overlay__scrim']")))

                                try:
                                    for index,value in enumerate(all_slots):
                                        if index >= suitable_index :
                                            value.click()
                                    print('clicked all possible slots')
                                    
                                except:
                                    print('error in clicking all slots')
                                    pass

                                # delay 3 second
                                time.sleep(3)

                                # find the summary right and click the submit button
                                submit_button = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='col-right col col-4']//button[@type='button']")))
                                submit_button.click()
                                confirm = WebDriverWait(browser, 1000).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='v-dialog v-dialog--active']//div[@class='v-card__actions justify-end']//span[normalize-space()='CONFIRM']")))
                                confirm.click()
                                
                                captcha_code()
                                # since we only want the first date's all slots we can break the loop
                                # break removed because it screwed up the loop 

                                time.sleep(3)

                                msg = "These Slots have been booked!"
                                for i in all_slots:
                                    msg += i.text
                                    msg += "\n"
                                SendNotification(msg)
                            else:
                                continue
                                # print("No slot available")
                        except Exception as e:
                            print('error in booking function: ',e)
                            pass


                else:
                    print('Not a desired month for booking shutting down the bot')
                    # SendNotification('No available slots')
                    # time.sleep(randint(30,60))
                    # browser.refresh()
                time.sleep(randint(10,15))
                browser.refresh()
                # exit code
                # running = False
                # browser.quit()
                # browser.close()
                # del browser
                
                '''
                Browser refreshes and running continues
                '''
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        error = str(exc_type) + "\n" + str(fname) + "\n" + str(exc_tb.tb_lineno) + "\n" + str(e)
        # requests.post(f"https://api.callmebot.com/text.php?user=@JoelPP&text={urllib.parse.quote_plus(str(error))}")
        browser.refresh()

