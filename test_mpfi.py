# -*- coding: utf-8 -*-

#Import required libraries
import tkinter as tk
import pandas as pd
from slacker import Slacker
from datetime import datetime
from subprocess import check_call
import os

#Import local functions
from slack_functions import doTestAuth, getUserMap, mkdir, send_links
from slack_functions import getChannels, upload_reports
from clean_data import standardized_files, user_by_week, get_classes, get_projects
from generate_reports import send_report_request, test_result_request
from google_functions import initiate, create_files_from_list, download_essays
from pdf_reader import read_pdfs

#Get token and test authorization
def initialize():
    slack = Slacker('xoxp-156433728469-157043125975-586792693168-15113f5462084e42a5116c1d214e231d')
    testAuth = doTestAuth(slack)
    userIdNameMap = getUserMap(slack)
    return(slack, userIdNameMap)
    
def send_mpfi(slack, class_name, userIdNameMap):
    
    message = 'Hello! Please complete the MPFI sometime during class today. I really appreciate your help in making this class even better! http://www.mpfi.xanderkrieg.com'
    
    #Get list of students and emails
    student_dict = pd.read_csv("".join(["resources/",class_name,"_grades.csv"]))
    student_dict = student_dict.loc[student_dict['mpfi'] == 1]
    student_dict = list(student_dict['user'])
    members = [key  for (key, value) in userIdNameMap.items() if value in student_dict]
    
    #Distribute to members
    for member in members:
        try:
            slack.chat.post_message(channel = member, text = message, username='@xkrieg',
                                    as_user = True)
        except Exception as e:
            print(e)

    print("Sent MPFI to", len(members), "participants via direct message.")
    
if __name__ == "__main__":

    #Initialize
    slack, userIdNameMap = initialize()
    send_mpfi(slack, 'emosta_2019', userIdNameMap)
