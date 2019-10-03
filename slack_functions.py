# -*- coding: utf-8 -*-

#Import required libraries
import pandas as pd
from slacker import Slacker
from datetime import datetime
import json
import time
import os

#Ensure the authentication token works
def doTestAuth(slack):
    testAuth = slack.auth.test().body
    teamName = testAuth['team']
    currentUser = testAuth['user']
    print("Successfully authenticated for team {0} and user {1} ".format(teamName, currentUser))
    return testAuth
  
#Fetch all users for the channel and return a map userId -> userName
def getUserMap(slack):
    #get all users in the slack organization
    users = slack.users.list().body['members']
    userIdNameMap = {}
    for user in users:
        userIdNameMap[user['id']] = user['name']
    print("found {0} users ".format(len(users)))
    return userIdNameMap

def getHistory(pageableObject, channelId, pageSize = 100):
    messages = []
    lastTimestamp = None

    while(True):
        response = pageableObject.history(
            channel = channelId,
            latest  = lastTimestamp,
            oldest  = 0,
            count   = pageSize
        ).body

        messages.extend(response['messages'])

        if (response['has_more'] == True):
            lastTimestamp = messages[-1]['ts'] # -1 means last element in a list
        else:
            break
    return messages

#Create folder if not exist
def mkdir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

#Fetch and write history for all public channels
def getChannels(slack, class_name):
    channels = slack.channels.list().body['channels']
    print("\nfound channels: ")
    for channel in channels:
        print(channel['name'])

    parentDir = "".join(["output/", class_name, "/",
                         datetime.now().strftime('%Y-%m-%d'),"/channels"])
    mkdir(parentDir)
    for channel in channels:
        print("getting history for channel {0}".format(channel['name']))
        fileName = "{parent}/{file}.json".format(parent = parentDir,
                                                 file = channel['name'])
        messages = getHistory(slack.channels, channel['id'])
        channelInfo = slack.channels.info(channel['id']).body['channel']
        with open(fileName, 'w') as outFile:
            print("writing {0} records to {1}".format(len(messages), fileName))
            json.dump({'channel_info': channelInfo, 'messages': messages }, 
                        outFile, indent=4)
    return(parentDir)

#Send assignment links as a private message on Slack
def send_links(slack, user_map, name_link):
    reverse = dict((v,k) for k,v in user_map.items())
    keys = list(reverse.keys())
    
    combined = {}
    for key in keys:
        if key in name_link:
            combined[reverse[key]] = name_link[key]

    values = list(combined.keys())
    for value in values:
        if value in combined:
            slack.chat.post_message(value, combined[value], username = '@xkrieg',
                                    as_user = True)
            time.sleep(1)

    print("All links send to owners via direct message.")

#Send reports as private message on Slack
def upload_reports(slack, user_map, directory, list_of_files):
    
    keys = list(user_map.keys())
    values = list(user_map.values())
    if directory.endswith('/channels'):
        directory = directory.replace('/channels','/reports')
        title_text = 'Weekly English Fluency Assessment'
    else:
        title_text = 'Writing Assignment Feedback'
    
    for file in list_of_files:
        user_name = file.split("_")[0]
        slack.files.upload("/".join([directory,file]),
                           channels=[keys[values.index(user_name)]],
                           title=title_text)
                       
    print("Successfully uploaded reports.")
    
def add_slack_topic(slack, class_name, userIdNameMap, channel_name):
    
    #Get list of students and emails
    student_dict = pd.read_csv("".join(["resources/",class_name,"_grades.csv"]))
    student_dict = list(student_dict['user'])
    members = [key  for (key, value) in userIdNameMap.items() if value in student_dict]
    
    #Locate question
    topic_list = pd.read_csv('resources/topics.csv')
    question = topic_list.loc[topic_list['name'] == channel_name]['question']
    
    #Create channel
    slack.channels.create(channel_name)
    
    #Find channel id
    channels = slack.channels.list().body['channels']
    channel_id = [channel['id'] for channel in channels if channel['name'] == channel_name][0]
    
    #Invite members
    for member in members:
        try:
            slack.channels.invite(channel = channel_id, user = member)
        except Exception:
            print(member, "is already in the channel")
    
    #Set purpose and post question
    slack.channels.set_purpose(channel = channel_id, purpose = question)
    slack.chat.post_message(channel = channel_name, text = question, username='@xkrieg',
                            as_user = True)
    print("Added topic:", name)
    
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
