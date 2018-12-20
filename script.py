import os
import requests
import json
from datetime import datetime
import sqlite3
import yampy

from dotenv import load_dotenv, find_dotenv
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import db_utils
from time import sleep

load_dotenv(find_dotenv())

no_city_found_email =  os.environ.get('NO_CITY_FOUND_EMAIL') #= dotenv.get('NO_CITY_FOUND_EMAIL')
from_email = os.environ.get('SENDER_EMAIL')
office_location_id = os.environ.get('OFFICE_LOCATION_ID')

ids = []

yammer = yampy.Yammer(access_token=os.environ.get('YAMMER_TOKEN'))


def birthdays_locations(per_page, current_page):
    url = 'https://rimon.namely.com/api/v1/profiles.json?filter[user_status]=active&per_page=' + str(per_page) + '&page=' + str(current_page)

    token = os.environ.get('TOKEN')

    payload = "{}"
    headers = {'authorization': 'Bearer ' + token}

    response = requests.request("GET", url, data=payload, headers=headers)

    json_data = json.loads(response.text)
    total_records = json_data['meta']['total_count']

    print "Total records: " + str(total_records) + "\n"
    print "Current Page: " + str(current_page)

    addresses = filter(lambda x: x['type'] == 'Office Location', json_data['linked']['groups'])
    ids = [x['id'] for x in addresses]

    def filter_birthday(profile):
        today = datetime.today()
        if profile['dob']:
            birthday_obj = datetime.strptime(profile['dob'], '%Y-%m-%d').replace(year = today.year)
            if birthday_obj.month == 1 and today.month == 12:
                birthday_obj = birthday_obj.replace(year = today.year+1)
            days_left = (birthday_obj - today).days + 1


            #Post to Yammer
            if days_left == 0:
              yammer_post = "Today is " + profile['full_name'] + "'s birthday. Happy birthday, " + profile['full_name'] + "!"
              yammer.messages.create(yammer_post, topics=["Birthday"])
              sleep(5)

            if days_left == 14:
                locations = filter(lambda x: x['id'] in ids, profile['links']['groups'])
                profile['city'] = 'Not Available' if len(locations) == 0 else locations[0]['name'] 
                return True
        return False

    profiles = filter(filter_birthday, json_data['profiles'])

    return (profiles, (total_records > (per_page*current_page)))


per_page = 50
current_page = 1

api_call = birthdays_locations(per_page, current_page)

birthday_profiles = api_call[0]
run_again = api_call[1]


while run_again:
    current_page += 1
    api_call = birthdays_locations(per_page, current_page)
    birthday_profiles.extend(api_call[0])
    run_again = api_call[1]

print "Profiles: "

conn = sqlite3.connect('gifter.db')
c = conn.cursor()

def send_msg(body, to):

    msg_body = "<p>Hey there,</p><p><b>Hey! Here are birthdays coming up in 14 days</b></p>";

    msg_body += body

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to
    msg['Subject'] = "Birthday Reminders - " + datetime.today().strftime('%Y-%m-%d')
    msg.attach(MIMEText(msg_body, 'html'))

    text = msg.as_string()

    server = smtplib.SMTP('smtp.office365.com', 587)
    server.starttls()
    server.login(os.environ.get('SMTP_USERNAME'), os.environ.get('SMTP_PASSWORD'))
    response = server.sendmail(from_email, to, text)
    print response, " - Sent email to ", to
    server.quit()



gifter_email_dict = dict()


for person in birthday_profiles:
    query = "SELECT * FROM gifters_locations WHERE city = '" + person['city'] + "';"
    w = c.execute(query)
    gifter = w.fetchone()
    gifter_email = gifter[0] if gifter else no_city_found_email

    if gifter_email in gifter_email_dict:
        gifter_email_dict[gifter_email].append(person)
    else:
        gifter_email_dict[gifter_email] = [person]
  

for gifter in gifter_email_dict:
    if gifter_email_dict[gifter] != None:
        is_sent = None
        for celebrant_info in  gifter_email_dict[gifter]:
            print gifter, celebrant_info['email']
            is_sent = False
            msg_body = "<p><b>" + celebrant_info['full_name'] + "</b> - " + celebrant_info['dob'] + ". Location : " + celebrant_info['city'] + "</p>"
            if celebrant_info['dietary_restrictions'] != None:
                msg_body += "<p><b>Dietary Restrictions:</b> " + celebrant_info['dietary_restrictions'] + "</b></p><br>"
            if celebrant_info['email'] == gifter:
                send_msg(msg_body, 'yaacov@rimonlaw.com')
                is_sent = True
        msg_body += "<p>Please write Michael and Yaacov with (a) a suggested gift, and (b) suggested wording for a card. Thank you.</p>"
        if not is_sent:
            send_msg(msg_body, gifter)

#No city found in db_utils mail to be sent to yaacov

















