import pandas as pd
import pickle
import os
from pathlib import Path
import re
from platform import platform
from tools_utils import prompts

class LoadGivenCourses:
    """ Load given courses information from the pickle file.

        Inputs should be a string with course codes, separated by commas.
    
        Support the following course format:
        "COMP 2011", "COMP2011", "comp 2011", "comp2011"
    """
    def __init__(self, 
                all_courses_file_path='load_courseinfo\Courseinfo\AllCourses.pickle') -> None:
        self.all_courses_file_path = os.path.join(Path.cwd(), all_courses_file_path)
        if 'mac' in platform():
            self.all_courses_file_path = self.all_courses_file_path.replace('\\', '/')
        # print(self.all_courses_file_path)
        # print('/Users/liuhanmo/Library/CloudStorage/OneDrive-HKUSTConnect/USTAgent/USTAgent/load_courseinfo/Courseinfo/AllCourses.pickle')
        assert os.path.exists(self.all_courses_file_path), "AllCourses.pickle file not found."
        print("LoadGivenCourses Tool has been set up."
              "Using file information from " + self.all_courses_file_path + ".")

    def split_course_code(self, text):
        # Use regular expressions to split the input string into English and number parts
        match = re.match(r"([A-Za-z ]+)(\d+)", text)
        if match:
            # Remove any spaces from the English part and convert it to uppercase
            english_part = match.group(1).replace(" ", "").upper()
            number_part = match.group(2)
            return english_part, number_part
        else:
            # If there's no match, return None for both parts
            return None, None

    
    def find_course(self, input):
        # Load course information by input, example input: "COMP 2011", "COMP2011", "comp 2011", "comp2011".
        subject, number = self.split_course_code(input)
        course_code = subject + " " + number
        pickle_in = open(self.all_courses_file_path, 'rb')
        #course_data[course_code] = pickle.load(pickle_in)
        course_data = pickle.load(pickle_in)
        return course_data[subject][course_code]

    @prompts(name="Load Course Information", 
             description="useful when you have a course code and want to know more about it."
                         "like: find information about COMP2011,"
                         "or find information about 'comp 2011, elec 1100, math 1013'."
                         "The input to this tool should be a string of course codes, separated by commas.")
    def forward(self, inputs):
        assert isinstance(inputs, str), "The input to this tool should be a string of course codes, separated by commas."
        inputs = inputs.split(',')
        course_info = {}
        for input in inputs:
            course_info[input] = self.find_course(input)

        return course_info
        
