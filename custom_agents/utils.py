import pandas as pd


def parse_date_time(str):
    '''
    Return the date and time from the given string.
    E.g., 'MoWe 2:00PM - 3:15PM' -> ['Monday 2:00PM - 3:15PM', 'Wednesday 2:00PM - 3:15PM']
    str: str, string to parse
    
    return: list, list of date and time
    '''
    std_weekdays = {'Mo': 'Monday', 'Tu': 'Tuesday', 'We': 'Wednesday', 'Th': 'Thursday', 'Fr': 'Friday', 'Sa': 'Saturday'}

    found_time = []
    prev_loc = 0
    components = str.split()
    for i, cpt in enumerate(components):
        if '-' in cpt:
            time_str = ' '.join(components[i-1:i+2]) 
            
            weekdays = components[prev_loc:i]
            for key in std_weekdays.keys():
                for weekday in weekdays:
                    if key in weekday:
                        found_time.append(' '.join([std_weekdays[key], time_str]))
            prev_loc = i+1

    if len(found_time) == 0:
        return None
    else:
        return found_time


def get_course_dataframes(section_path, info_path):
    '''
    Return the dataframes for course section and course info
    path: str, path to the data folder
    return: df_course_section, df_course_info
    '''
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    # pd.set_option('max_colwidth', 100)

    course_section_path = section_path
    df_course_section = pd.read_csv(course_section_path)

    course_info_path = info_path
    df_course_info = pd.read_csv(course_info_path)

    # df1 = pd.read_csv('data/courses_section.csv').iloc[:, 1:]
    # df2 = pd.read_csv('data/courses_info.csv').iloc[:, 1:]

    df_course_section['Date & Time'] = df_course_section['Date & Time'].apply(parse_date_time)
    df_course_section['Section Name'] = df_course_section['Section'].apply(lambda x: x.split()[0])
    df_course_section['Section ID Code'] = df_course_section['Section'].apply(lambda x: x.split()[1]).apply(lambda x: x[1:-1])
    df_course_section.drop('Section', axis=1, inplace=True)

    return df_course_section, df_course_info


def get_event_dataframes(path):
    '''
    Return the dataframes for event section information and event description
    path: str, path to the data folder
    return: df_event_section, df_event_info
    '''
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    # pd.set_option('max_colwidth', 100)

    event_path = path
    df = pd.read_csv(event_path)

    df["Performer Name"] = df["Performer Name"].replace("The Hong Kong University of Science and Technology", "HKUST")
    # df.drop('Description', axis=1, inplace=True)
    df.drop("URL", axis=1, inplace=True)
    df.drop("Performer URL", axis=1, inplace=True)
    df.drop("Date", axis=1, inplace=True)
    df.drop("Location Name", axis=1, inplace=True)
    df = df.fillna('')

    df_event_section = df.drop('Description', axis=1)
    df_event_info = df[['Title', 'Description']]

    return df_event_section, df_event_info