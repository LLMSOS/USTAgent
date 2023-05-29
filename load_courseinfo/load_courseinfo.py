import pandas as pd
import pickle
import os
from pathlib import Path

course_codes = ['ACCT','AESF','AIAA','AMAT','BIBU','BIEN','BSBE','BTEC','CBME','CENG','CHEM','CHMS','CIEM','CIVL','CMAA','COMP','CORE','CPEG','CSIC','CSIT','DASC','DBAP','DSAA','DSCT','ECON','EEMT','EESM','ELEC','EMBA','EMIA','ENEG','ENGG','ENTR','ENVR','ENVS','EOAS','EVNG','EVSM','FINA','FTEC','GBUS','GFIN','GNED','HLTH','HMMA','HUMA','IBTM','IDPO','IEDA','IIMP','IMBA','INTR','IOTA','IPEN','ISDN','ISOM','JEVE','LABU','LANG','LIFS','MAED','MAFS','MARK','MASS','MATH','MECH','MESF','MFIT','MGCS','MGMT','MICS','MILE','MIMT','MSBD','MSDM','MTLE','NANO','OCES','PDEV','PHYS','PPOL','RMBI','ROAS','SBMT','SCIE','SEEN','SHSS','SMMG','SOSC','SUST','TEMG','UGOD','UROP','WBBA']


def load_courseinfo(course_codes):
    course_data = {}
    for course_code in course_codes:
        pickle_in = open(os.path.join(Path.cwd(), 'Courseinfo', course_code+'.pickle'), 'rb')
        course_data[course_code] = pickle.load(pickle_in)
        print(course_code + " information loaded")
    return course_data


if __name__ == '__main__':
    course_data = load_courseinfo(course_codes)
