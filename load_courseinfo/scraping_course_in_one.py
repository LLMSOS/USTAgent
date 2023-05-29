import requests
from bs4 import BeautifulSoup
import pandas as pd
import pickle
import os
from pathlib import Path

course_codes = ['ACCT', 'AESF', 'AIAA', 'AMAT', 'BIBU', 'BIEN', 'BSBE', 'BTEC', 'CBME', 'CENG', 'CHEM', 'CHMS',
                    'CIEM', 'CIVL', 'CMAA', 'COMP', 'CORE', 'CPEG', 'CSIC', 'CSIT', 'DASC', 'DBAP', 'DSAA', 'DSCT',
                    'ECON', 'EEMT', 'EESM', 'ELEC', 'EMBA', 'EMIA', 'ENEG', 'ENGG', 'ENTR', 'ENVR', 'ENVS', 'EOAS',
                    'EVNG', 'EVSM', 'FINA', 'FTEC', 'GBUS', 'GFIN', 'GNED', 'HLTH', 'HMMA', 'HUMA', 'IBTM', 'IDPO',
                    'IEDA', 'IIMP', 'IMBA', 'INTR', 'IOTA', 'IPEN', 'ISDN', 'ISOM', 'JEVE', 'LABU', 'LANG', 'LIFS',
                    'MAED', 'MAFS', 'MARK', 'MASS', 'MATH', 'MECH', 'MESF', 'MFIT', 'MGCS', 'MGMT', 'MICS', 'MILE',
                    'MIMT', 'MSBD', 'MSDM', 'MTLE', 'NANO', 'OCES', 'PDEV', 'PHYS', 'PPOL', 'RMBI', 'ROAS', 'SBMT',
                    'SCIE', 'SEEN', 'SHSS', 'SMMG', 'SOSC', 'SUST', 'TEMG', 'UGOD', 'UROP', 'WBBA']

def get_soup(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    return None


def extract_course_data(soup):
    course_data = {}

    for course in soup.find_all(class_='course'):

        course_title = course.find('h2').text

        # Find all the <tr> tags in the HTML script
        trs = course.find(class_='courseattr').find(class_='popupdetail').find_all('tr')

        # Initialize empty dictionaries to store the extracted information
        course_info = {}
        course_info['course title'] = course_title
        # Loop through each <tr> tag and extract the information
        for tr in trs:
            th = tr.find('th')
            td = tr.find('td')

            if th and td:
                course_info[th.text] = td.text

        # Print the extracted information
        # print(course_info)

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
        # print(df)

        # Add the sections to the course_info dictionary
        course_info['sections'] = df

        course_data[course_title.split(' -')[0]] = course_info

    return course_data


def crawl_website(course_codes):
    course_data = {}
    for course_code in course_codes:
        url = 'https://w5.ab.ust.hk/wcq/cgi-bin/2230/subject/' + course_code
        soup = get_soup(url)
        if soup:
            course_data[course_code] = extract_course_data(soup)

        else:
            print("Failed to fetch the URL")
    pickle_out = open(os.path.join(Path.cwd(), 'Courseinfo', 'AllCourses.pickle'), 'wb')
    # pickle_out = open(course_code+'.pickle', 'wb')
    pickle.dump(course_data, pickle_out)
    pickle_out.close()
    print("Reloaded all courses information and saved into AllCourses.pickle file in Courseinfo folder.")


if __name__ == '__main__':
    crawl_website(course_codes)