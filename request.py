import httpx
import json

def POST_REQ(auth, cookie, jsessionid, url, data={}):
    headers = {
        'User-Agent': 'Postman',
        'Authorization': auth,
        'Cookie': cookie,
        'Jsessionid': jsessionid
    }

    print('These are the headers:', headers)

    try:
        response = httpx.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        print('Response from POST request:', response.status_code, response.text)
        return response
    except httpx.RequestError as e:
        print(f"An error occurred: {e}")
        return None

AUTH = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJCQkRDIiwiTlJJQyI6IlQwMTI4MzM3QSIsImV4cCI6MTcxNzQyNDEzMH0.MGjHtbnIGEQPOQUEv2loZvEjtQMka6uXn6sJUHSNAVY"
COOKIE = "bbdc-token=Bearer%20eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJCQkRDIiwiTlJJQyI6IlQwMTI4MzM3QSIsImV4cCI6MTcxNzQyNDEzMH0.MGjHtbnIGEQPOQUEv2loZvEjtQMka6uXn6sJUHSNAVY"
JSESSIONID = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJBQ0NfSUQiOiIxMDU5NTk5IiwiVFJBX0xPR0lOIjoiMzM3QTE4MDkyMDAxIiwiaXNzIjoiQkJEQyIsIk5SSUMiOiJUMDEyODMzN0EiLCJleHAiOjEzMDU2NjM1NjU1MX0.jKDEqitbNItO4FYTPX0178taiyHUL6dYnNFzb_3GOkM"

res = POST_REQ(AUTH, COOKIE, JSESSIONID, "https://booking.bbdc.sg/bbdc-back-service/api/booking/c3practical/checkC3UserGroup")

print('Response from POST request:', res)

