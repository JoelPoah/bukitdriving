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
import datetime
import re
from seleniumwire.utils import decode as sw_decode
import jwt
import sys ,os

browser = webdriver.Chrome()
stealth(browser,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

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
                dates = browser.find_elements(By.XPATH, "//div[@class='v-calendar-weekly__day v-present' or @class='v-calendar-weekly__day v-future']")
                wanted_dates = [14,15,16,17]
                for each_date in dates:
                    if running:
                        if "/login" in browser.current_url:
                            running = False
                            running2 = False
                            running3 = True
                        try:
                            child_item = each_date
                            print(child_item.text)
                            parent_of_div = child_item.find_elements(By.TAG_NAME,"div")
                            child_child_item = parent_of_div[0].find_elements(By.TAG_NAME,"span")
                            print(child_child_item[0].get_attribute('class').split())
                            
                            if 'disabled-text' not in (child_child_item[0].get_attribute('class').split()) and child_item.text in wanted_dates:
                                print("Found slot")
                                child_item.click()
                                grey_screen = WebDriverWait(browser, wait_time).until(EC.invisibility_of_element_located((By.XPATH,"//div[@class='v-overlay__scrim']")))
                                #change this
                                sessionList = browser.find_elements(By.CLASS_NAME,"sessionList")
                                slot = sessionList[1].find_element(By.CLASS_NAME,"sessionContent-web")
                                all_slot = slot.find_elements(By.CLASS_NAME,"sessionCard")
                                for each_slot in all_slot:
                                    # Get the current time
                                    now = datetime.datetime.now()

                                    # Convert the string containing "HH:MM" to a datetime object with the same date as the current time
                                    regex_check = re.search("\d{2}:\d{2}\ ",each_slot.text)
                                    time_str = (regex_check.group()).strip()
                                    time_obj = datetime.datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=int(child_item.text))

                                    # Calculate the difference between the two datetime objects
                                    time_diff = time_obj - now

                                    # Extract the number of hours from the difference
                                    hours_diff = int(time_diff.total_seconds() / 3600)
                                    print(hours_diff)
                                    if hours_diff >= 1 and time_str != "07:30":
                                        each_slot.click()
                                
                                submit_button = WebDriverWait(browser, wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='col-right col col-4']//button[@type='button']")))
                                submit_button.click()
                                confirm = WebDriverWait(browser, 1000).until(EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='CONFIRM']")))
                                confirm.click()
                                captcha_code()
                                now = datetime.datetime.now()
                                date_of_book_slot = each_date.text + "/" + str(now.month)
                                class_booked = urllib.parse.quote_plus(date_of_book_slot + "\n" +all_slot[0].text)
                                ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
                                fkingwork = True
                                while fkingwork:
                                    if "/login" in browser.current_url:
                                        running = False
                                        running2 = False
                                        running3 = True
                                        fkingwork = False
                                    try:
                                        successornot=WebDriverWait(browser, 1000,ignored_exceptions=ignored_exceptions).until(EC.presence_of_element_located((By.XPATH,"//div[@class='item-bottom']//p[@class='text_success' or @class='text_fail']")))
                                        print(successornot.get_attribute("class"))
                                        print(successornot.text)
                                        if "text_success" in successornot.get_attribute("class"):
                                            requests.post(f"https://api.callmebot.com/text.php?user=@JoelPP&text={class_booked}")
                                            fkingwork = False

                                    except:
                                        pass
                                new_booking = WebDriverWait(browser, 100).until(EC.presence_of_element_located((By.XPATH, "//span[normalize-space()='CLOSE']")))
                                new_booking.click()
                                running = False
                            else:
                                nohave = "No slot available donkey"
                                requests.post(f"https://api.callmebot.com/text.php?user=@JoelPP&text={nohave}")
                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            print(exc_type, fname, exc_tb.tb_lineno)
                            error = str(exc_type) + "\n" + str(fname) + "\n" + str(exc_tb.tb_lineno) + "\n" + str(e)
                            requests.post(f"https://api.callmebot.com/text.php?user=@JoelPP&text={urllib.parse.quote_plus(str(error))}")
                time.sleep(randint(30,60))
                browser.refresh()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        error = str(exc_type) + "\n" + str(fname) + "\n" + str(exc_tb.tb_lineno) + "\n" + str(e)
        requests.post(f"https://api.callmebot.com/text.php?user=@JoelPP&text={urllib.parse.quote_plus(str(error))}")
        browser.refresh()
