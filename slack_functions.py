# -*- coding: utf-8 -*-

#Import required libraries
from slacker import Slacker
from datetime import datetime
import json
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
