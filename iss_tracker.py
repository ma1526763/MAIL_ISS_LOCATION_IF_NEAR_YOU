import requests
import os
from datetime import datetime
import time
from smtplib import SMTP

MY_LONG, MY_LAT = float(os.environ['LON']), float(os.environ["LAT"])
ISS_URL_ENDPOINT = "http://api.open-notify.org/iss-now.json"
SUNSET_URL_ENDPOINT = "https://api.sunrise-sunset.org/json"
ISS_LONG, ISS_LAT = 0, 0
sunset_time = []
current_hour = 0
current_minute = 0
CHECK_AFTER_SECONDS = 60
SENDER_MAIL = os.environ.get('SENDER_MAIL')
PASSWORD = os.environ.get('PASSWORD')
RECEIVER_MAIl = os.environ['RECEIVER_MAIL']
message = ""

# send mail if iss is overhead
def send_mail(visibility):
    with SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=SENDER_MAIL, password=PASSWORD)
        connection.sendmail(from_addr=SENDER_MAIL, to_addrs=RECEIVER_MAIl, msg=f"Subject:{visibility}\n\n{message}")

# get ISS location
def iss_location_func():
    global ISS_LONG, ISS_LAT
    try:
        response = requests.get(ISS_URL_ENDPOINT)
    except requests.exceptions.ConnectionError:
        print("Please check your internet connection")
        return False
    response.raise_for_status()
    data = response.json()["iss_position"]
    ISS_LONG, ISS_LAT = float(data["longitude"]), float(data["latitude"])
    return True

# get sunset time
def sunset_time_func():
    global sunset_time
    parameters = {
        "lat": MY_LAT,
        "lon": MY_LONG,
    }
    sunset_time = requests.get(url=SUNSET_URL_ENDPOINT, params=parameters).json()["results"]['sunset'].split()[0].split(":")

# check if iss_is_overhead
def iss_overhead():
    global current_hour, current_minute, message
    current_hour = datetime.now().hour % 12
    current_minute = datetime.now().minute
    # After sunset
    if current_hour > int(sunset_time[0]) and current_minute > int(sunset_time[1]) and (ISS_LONG - 5) <= MY_LONG <= (
            ISS_LONG + 5) and (ISS_LAT - 5) <= MY_LAT <= (MY_LAT + 5):
        message = f"Look up it's Night Time!\nISS CURRENT LOCATION: LAT: {ISS_LAT} , LON: {ISS_LONG}\n"
        send_mail("NIGHT TIME")
    # day time
    elif (ISS_LONG - 5) <= MY_LONG <= (ISS_LONG + 5) and (ISS_LAT - 5) <= MY_LAT <= (MY_LAT + 5):
        message = f"ISS is overhead.\nISS CURRENT LOCATION: LAT: {ISS_LAT} , LON: {ISS_LONG}\n"
        send_mail("DAY TIME")
    else:
        print("Not overhead")

def start():
    if not iss_location_func():
        return
    sunset_time_func()
    while True:
        print(f"ISS CURRENT LOCATION: LAT: {ISS_LAT} , LON: {ISS_LONG}", end=" ---- ")
        iss_overhead()
        time.sleep(CHECK_AFTER_SECONDS)
        if not iss_location_func():
            return

start()