#!/bin/bash
#PATH=/opt/someApp/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

import os
import requests
import json
from datetime import datetime
import sqlite3

from dotenv import load_dotenv, find_dotenv
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import db_utils

load_dotenv(find_dotenv())

no_city_found_email =  os.environ.get('NO_CITY_FOUND_EMAIL') #= dotenv.get('NO_CITY_FOUND_EMAIL')
from_email = os.environ.get('SENDER_EMAIL')


def birthdays_locations(per_page, current_page, locations_dict = dict()):
	url = 'https://rimon.namely.com/api/v1/profiles.json?filter[status]=active&per_page=' + str(per_page) + '&page=' + str(current_page)

	token = os.environ.get('TOKEN')

	payload = "{}"
	headers = {'authorization': 'Bearer ' + token}

	response = requests.request("GET", url, data=payload, headers=headers)

	json_data = json.loads(response.text)
	total_records = json_data['meta']['count']

	print "Total records: " + str(total_records) + "\n"
	print "Current Page: " + str(current_page)
	count = 1
	for row in json_data['profiles']:
		location = "Not Available" if row['home']['city'] == None else row['home']['city']
		today = datetime.today()
		if row['dob']:
			birthday_obj = datetime.strptime(row['dob'], '%Y-%m-%d').replace(year = today.year)
			days_left = (birthday_obj - today).days
			
			if days_left == 14:
				person = {'fullname': str(row['first_name']) + " " + str(row['last_name']), 'birthday': str(birthday_obj), 'city': location}
				if location in locations_dict:
					locations_dict[location].append(person)
				else:
					locations_dict[location] = [person]

		else:
			print ""

		count = count + 1
	return (locations_dict, (total_records > (per_page*current_page)))

per_page = 50
current_page = 1

api_call = birthdays_locations(per_page, current_page, dict())	

locations = api_call[0]
run_again = api_call[1]

while run_again:
	current_page += 1
	api_call = birthdays_locations(per_page, current_page, locations)
	locations = api_call[0]
	run_again = api_call[1]




conn = sqlite3.connect('gifter.db')
c = conn.cursor()


gifter_email_dict = dict()

for location in locations:
	celebrants = locations[location]
	query = "SELECT * FROM gifters_locations WHERE city = '" + location + "';"
	w = c.execute(query)
	gifter = w.fetchone()

	if gifter != None:
		gifter_email = gifter[0]
	else:
		gifter_email = no_city_found_email

	if gifter_email in gifter_email_dict:
		for celebrant in celebrants:
			gifter_email_dict[gifter_email].append(celebrant)
	else:
		gifter_email_dict[gifter_email] = celebrants


for gifter in gifter_email_dict:
	msg_body = "<p>Hey there,</p><p><b>Hey! Here are birthdays coming up in 14 days</b></p>"
	for celebrant_info in gifter_email_dict[gifter]:
		msg_body += "<p><b>" + celebrant_info['fullname'] + "</b> - " + celebrant_info['birthday'] + ". Location : " + celebrant_info['city'] + "</p><br><p>Please write Michael and Yaacov with (a) a suggested gift, and (b) suggested wording for a card. Thank you.</p>"

	msg = MIMEMultipart()
	msg['From'] = from_email
	msg['To'] = gifter
	msg['Subject'] = "Birthday Reminders- " + datetime.today().strftime('%Y-%m-%d')
	msg.attach(MIMEText(msg_body, 'html'))

	text = msg.as_string()

	server = smtplib.SMTP('smtp.office365.com', 587)
	server.starttls()
	server.login(os.environ.get('SMTP_USERNAME'), os.environ.get('SMTP_PASSWORD'))
	response = server.sendmail(from_email, gifter, text)
	print response, " - Sent email to ", gifter
	server.quit()

