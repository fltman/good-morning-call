#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import caldav
from datetime import datetime, timedelta
import pytz
from openai import OpenAI
from elevenlabs import voices, generate, save, set_api_key
#import datetime

set_api_key("YOUR ELEVEN LABS KEY")

client = OpenAI()

def create_wakeup_call(name, weather, news, calendar):
	if name == "jeeves":
		voice_id = "AZCDoG2FZUmOoztPBLBq"
		
		messages=[
			{
				"role": "user",
				"content": "I want you to act and talk like an extremely stereotypical British butler. Yes, sir. Splendid day sir wouldn't you say. No cricket today sir so I'll spare you the sport. Todays top news seems to be about xxxxxx  but no other news worth mentioning from the colonies sir. \n\nAh the weather sir a splendid grey day with gusty wind sir. We have a slight chill today with temperatures below zero sir so I'll turn on the heat in the car for you sir so that it is all ready when you are sir. Yes sir, let me honk the horn for you as well just to let the neighbours know that it's time to rise and shine. Yes sir... Always reply in english"
			}
		]
	elif name == "gollum":
		voice_id = "5zxpMZTtqU2XdryRbAkg"
	
		messages= [
			{
				"role": "user",
				"content": "You are Gollum, creepy character from Lord of the Rings. Always reply in english."
			}
		]
	elif name == "jules":
		voice_id = "QFqn4T7kE81UlNiJqoqL"
	
		messages= [
			{
				"role": "user",
				"content": "You are Jules Winnfield, gangster and thug from pulp fiction. Always reply in english"
			}
		]
	elif name == "david":
		voice_id = "oEGHrESEGCGeNFDUy9Ef"
	
		messages= [
			{
				"role": "user",
				"content": "Let's roleplay and pretend that you are david attenborough observing and describing The data below. You put a lot of focus on attraction between humans in a funny way For example:  the male has put on a white shirt, quite possibly to attract the female in red next to him. Always reply in english"
			}
		]
	elif name == "nicole":
		voice_id = "piTKgcLEGmPE4e6mEKli"
	
		messages= [
			{
				"role": "user",
				"content": "You are Nicole a relaxed and caring person with a relaxing, soothing voice. Always reply in english."
			}
		]
	
	now = datetime.now()
	
	# Extract date, weekday, and time
	current_date = now.date()
	weekday = now.strftime("%A")  # This gives the full weekday name
	current_time = now.time()
	
	# Combine into a single variable (as a string for example)
	date_weekday_time = f"Date: {current_date}, Weekday: {weekday}, Time: {current_time}"
	
	messages.append(
		{
			"role": "user",
			"content": f"Stay in character and wake Anders up based on this:\n\n\
Date and time:{date_weekday_time}\n\n\
Todays weather:{weather}\n\n\
Todays Calendar:```{calendar}```\n\n\
Todays News:```{news}```	\n\n\
Only reply with the wake up call."
		}
	)
	
	response = client.chat.completions.create(
		model="gpt-4-1106-preview",
		messages=messages,
		temperature=1,
		top_p=1,
		frequency_penalty=0,
		presence_penalty=0
	)
	
	render_audio(f"{name}.mp3", response.choices[0].message.content, voice_id)
	print (response.choices[0].message.content)
	return response.choices[0].message.content
	
def summarize_news(content):
	response = client.chat.completions.create(
		model="gpt-4-1106-preview",
		messages=[
			{
				"role": "user",
				"content": f"The content below is from extracting text from a webpage. Summarize the top news for me: \n\n{content}"
			}
		],
		temperature=1,
		max_tokens=256,
		top_p=1,
		frequency_penalty=0,
		presence_penalty=0
	)
	
	return response.choices[0].message.content

def render_audio(filepath, text, voice_id):
	audio = generate(text=text, voice=voice_id,
		model='eleven_multilingual_v2')
	save(audio, filepath)

def fetch_webpage_text(url):
	try:
		response = requests.get(url)
		response.raise_for_status()  # This will raise an exception for HTTP errors
		
		# Parse the content with BeautifulSoup
		soup = BeautifulSoup(response.content, 'html.parser')
		return soup.get_text(separator='\n', strip=True)
	except requests.RequestException as e:
		return str(e)

def get_weather(location):
	base_url = f"http://wttr.in/{location}"
	params = {
		'format': '4'  # Simplified format for weather information
	}
	
	try:
		response = requests.get(base_url, params=params)
		response.raise_for_status()  # Raises an exception for HTTP errors
		
		return response.text.strip()
	except requests.RequestException as e:
		return str(e)

def get_todays_icloud_events(username, app_specific_password):
	# iCloud CalDAV URL
	url = 'https://caldav.icloud.com/'
	
	# Connect to the CalDAV server
	client = caldav.DAVClient(url, username=username, password=app_specific_password)
	principal = client.principal()
	calendars = principal.calendars()
	summary = ""
	if calendars:
		# Assuming you want to check the first calendar
		calendar = calendars[0]
		
		# Define the time range for today
		now = datetime.now(pytz.utc)
		start = datetime(now.year, now.month, now.day, tzinfo=pytz.utc)
		end = start + timedelta(days=1)
		
		# Fetch events for today
		events = calendar.date_search(start, end)
		
		for event in events:
			#print(event.instance.vevent.summary.value, event.instance.vevent.dtstart.value)
			summary = f"{summary}\n{event.instance.vevent.summary.value}, {event.instance.vevent.dtstart.value}"
		return summary
	
	else:
		print("No calendars found.")
		return []

#print (calendar)
url = "http://dn.se"
location = "Kalmar"
news = summarize_news(fetch_webpage_text(url))
weather = get_weather(location)
calendar = get_todays_icloud_events('email@icloud.com', 'your_app_specific_password')	# Login to https://appleid.apple.com/ to get your app specific password

#create_wakeup_call("jeeves", weather, news, calendar)
#create_wakeup_call("gollum", weather, news, calendar)
#create_wakeup_call("david", weather, news, calendar)
#create_wakeup_call("jules", weather, news, calendar)
#create_wakeup_call("hans", weather, news, calendar)
create_wakeup_call("nicole", weather, news, calendar)
