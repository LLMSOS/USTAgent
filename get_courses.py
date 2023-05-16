import requests
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import os
from pathlib import Path

ALL_COURSES = ['ACCT','AESF','AIAA','AMAT','BIBU','BIEN','BSBE','BTEC','CBME','CENG','CHEM','CHMS','CIEM','CIVL','CMAA','COMP','CORE','CPEG','CSIC','CSIT','DASC','DBAP','DSAA','DSCT','ECON','EEMT','EESM','ELEC','EMBA','EMIA','ENEG','ENGG','ENTR','ENVR','ENVS','EOAS','EVNG','EVSM','FINA','FTEC','GBUS','GFIN','GNED','HLTH','HMMA','HUMA','IBTM','IDPO','IEDA','IIMP','IMBA','INTR','IOTA','IPEN','ISDN','ISOM','JEVE','LABU','LANG','LIFS','MAED','MAFS','MARK','MASS','MATH','MECH','MESF','MFIT','MGCS','MGMT','MICS','MILE','MIMT','MSBD','MSDM','MTLE','NANO','OCES','PDEV','PHYS','PPOL','RMBI','ROAS','SBMT','SCIE','SEEN','SHSS','SMMG','SOSC','SUST','TEMG','UGOD','UROP','WBBA']


def get_soup(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    return None

def extract_course_data(soup):
    course_data = pd.DataFrame()
    course_section = pd.DataFrame()

    for course in soup.find_all(class_='course'):
        
        course_title = course.find('h2').text
        
        # Find all the <tr> tags in the HTML script
        trs = course.find(class_='courseattr').find(class_='popupdetail').find_all('tr')

        # Initialize empty dictionaries to store the extracted information
        course_info = {}
        course_info['course code'] = course_title.split(' -')[0]
        course_info['course title'] = course_title
        # Loop through each <tr> tag and extract the information
        for tr in trs:
            th = tr.find('th')
            td = tr.find('td')

            if th and td:
                course_info[th.text] = td.text

        # Print the extracted information
        #print(course_info)
        
        
        # Extract the 'sections' table
        table = course.find('table', class_='sections')
        
        headers = []

        for th in table.find('tr').find_all('th'):
            headers.append(th.text.strip())

        rows = []

        for row in table.find_all('tr')[1:]:
            row_data = []

            for td in row.find_all('td'):
                row_data.append(td.text.strip())

            if rows and len(row_data) < len(headers):
        #        for index, data in enumerate(row_data):
        #            rows[-1][index] += f" {data}"            
                for index, element in enumerate(row_data, start=1):
                    rows[-1][index] += ' ' + element

            else:
                rows.append(row_data)

        df = pd.DataFrame(rows, columns=headers)
        df.insert(loc=0, column='course code', value=course_title.split(' -')[0])
        
        course_section = pd.concat([course_section, df], axis=0, ignore_index=True, sort=False)
        course_section = course_section.where(pd.notnull(course_section), None)

        # Add the sections to the course_info dictionary
        # course_info['sections'] = df

        # course_data[course_title.split(' -')[0]] = course_info
        
        new_row = pd.DataFrame([course_info])
        #print(new_row)
        #course_data.append(new_row, ignore_index=True)
        course_data = pd.concat([course_data, new_row], axis=0, ignore_index=True, sort=False)
        course_data = course_data.where(pd.notnull(course_data), None)

    return course_data, course_section




# Use this function to get courses information and sections
def crawl_website(course_codes=ALL_COURSES, upper_url='https://w5.ab.ust.hk/wcq/cgi-bin/2230/subject/'):
    courses_info = pd.DataFrame()
    courses_section = pd.DataFrame()
    for course_code in course_codes:
        # 2230 for 2022-2023 Spring, and 2240 for 2022-2023 Summer
        url = upper_url + course_code
        soup = get_soup(url)
        if soup:
            course_info, course_section = extract_course_data(soup)
            courses_section = pd.concat([courses_section, course_section], axis=0, ignore_index=True, sort=False)
            courses_section = courses_section.where(pd.notnull(courses_section), None)
            courses_info = pd.concat([courses_info, course_info], axis=0, ignore_index=True, sort=False)
            courses_info = courses_info.where(pd.notnull(courses_info), None)

    return courses_info, courses_section

# Sample usage:
# courses_info, courses_section = crawl_website(course_codes)