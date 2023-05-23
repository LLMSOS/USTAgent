import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime, timedelta

def get_soup(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    return None


# Sample input: ("2023-05-16", 30)
def get_dates(start_date, period):

    input_date = datetime.strptime(start_date, '%Y-%m-%d')

    # List to store the output dates
    output_dates = [start_date]

    # Generate the dates for the next n days
    for i in range(period):
        next_date = input_date + timedelta(days=i+1)
        output_dates.append(next_date.strftime('%Y-%m-%d'))

    return output_dates

def get_events(url):
    
    events_data = pd.DataFrame()
    
    soup = get_soup(url)
    events = soup.find_all(class_='views-row')

    for event in events:
        title = event.h2.text.strip()
        link = "https://calendar.hkust.edu.hk" + event.find('a', href=True)['href']
        categories = ', '.join([category.text.strip() for category in event.find_all(class_='category')])
        organizer = event.find(class_='venue').text.strip()
        location = event.find_all(class_='venue')[1].text.strip()
        date = event.find(class_='date').text.strip()

        info = {
            'Title': [title],
            'Link': [link],
            'Categories': [categories],
            'Organizer': [organizer],
            'Location': [location],
            'Date': [date]
        }

        details = event_details(link)
        event_data = info | details
        df = pd.DataFrame(event_data)
        
        events_data = pd.concat([events_data, df], axis=0, ignore_index=True, sort=False)
        events_data = events_data.where(pd.notnull(events_data), None)
        
    return events_data


def event_details(url):

    soup = get_soup(url)

    # Extract the JSON-LD script
    json_script = soup.find('script', {'type': 'application/ld+json'}).string

    # Parse the JSON-LD script
    data = json.loads(json_script)

    # Extract the relevant information using key-value pairs
    event = data['@graph'][0]
    
    url = event.get('url')
    description = event.get('description')
    start_date = event.get('startDate')
    end_date = event.get('endDate')
    location_name = event['location'].get('name')
    location_country = event['location']['address'].get('addressCountry')
    performer_name = event['performer'].get('name')
    performer_url = event['performer'].get('url')
    
    
    data = {
    'URL': [url],
    'Description': [description],
    'Start Date': [start_date],
    'End Date': [end_date],
    'Location Name': [location_name],
    'Location Country': [location_country],
    'Performer Name': [performer_name],
    'Performer URL': [performer_url]
    }

    # Convert the dictionary into a pandas dataframe
    # df = pd.DataFrame(data)

    return data




# Use this function to get events, from the start date and within a period of time
def get_events_by_dates(start_date, period):
    dates = get_dates(start_date, period)
    events = pd.DataFrame()
    for date in dates:
        url = 'https://calendar.hkust.edu.hk/?date=' + date
        event = get_events(url)
        events = pd.concat([events, event], axis=0, ignore_index=True, sort=False).drop_duplicates(subset=['Title'])
    return events


# Sample usage:
# events = get_events_by_dates('2021-05-16', 30)