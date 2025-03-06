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

def GET( url, headers={}, data={}):
    
    headers = {
        'Origin':'https://booking.bbdc.sg',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    }
    try:
        response = httpx.get(url,headers=headers,  timeout=30)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        print('Response from GET request:', response.status_code, response.text)
        slots = response.json()
        return slots
    except httpx.RequestError as e:
        print(f"An error occurred: {e}")
        return None
    
get_res = GET("https://booking.bbdc.sg/#/login?redirect=homeindex")
print(get_res)