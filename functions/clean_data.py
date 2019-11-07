# -*- coding: utf-8 -*-

#Import required libraries
import pandas as pd
from pandas.io.json import json_normalize
from datetime import datetime
from spellchecker import SpellChecker
import language_check
import csv
import json
import re
import os

#Get class info
def get_classes():
    class_list = pd.read_csv('resources/class_list.csv')
    class_dict = dict(zip(class_list['class'], class_list['key']))
    return(class_dict)
    
#Get class info
def get_projects():
    with open('resources/projects.csv', 'r+') as f:
        reader = csv.reader(f)
        project_list = list(reader)
        project_list = [item for sublist in project_list for item in sublist]
    return(project_list)
    
##Get topic info
def get_topics():
    topic_list = pd.read_csv('resources/topics.csv')
    topic_names = list(topic_list['name'])
    return(topic_list, topic_names)

#Returns of all json files in directory
def get_files(directory):
    json_files = [jsonf for jsonf in os.listdir(directory) if jsonf.endswith('.json')]
    return(json_files)

#Find longest word in message
def find_longest(list_of_strings):
    if len(list_of_strings) > 0:
        longest = len(max(list_of_strings, key=len))
    else:
        longest = 0
    return(longest)
    
#Find average length of words in message
def find_average(list_of_strings):
    if len(list_of_strings) > 0:
        average = sum(map(len, list_of_strings)) / len(list_of_strings)
    else:
        average = 0
    return(average)
    
#Find spelling errors
def spell_check(spell, list_of_strings):
    if len(list_of_strings) > 0:
        n_misspelled = len(spell.unknown(list_of_strings))
    else:
        n_misspelled = 0
    return(n_misspelled)

#Find grammar errors
def grammar_check(grammar, sentence_list):
    count = 0
    if len(sentence_list) > 0:
        for sentence in sentence_list:
            count = count + len(grammar.check(sentence))
    return(count)

#Create standard columns & wordcount across all channels
def standardized_files(directory, user_map):
    file_list = get_files(directory)
    for i, file in enumerate(file_list):
        with open("/".join([directory,file])) as f:
            data = json.load(f)
        try:
            data = json_normalize(data["messages"])
        
            #Select required columns
            df = data.loc[:, ['user', 'ts', 'text']]
            df = df.dropna()
        
        except KeyError:
            df = pd.DataFrame(columns=['user', 'ts', 'text'])
        
        #Check grammar before reformatting sntences
        grammar = language_check.LanguageTool('en-US')
        df['grammar_check'] = [grammar_check(grammar,i.split(".")) for i in df['text']]
        
        #Format text
        df['text'] = [re.sub(r'^https?:\/\/.*[\r\n]*', '', s,flags=re.MULTILINE) for s in df['text']]
        df['text'] = [re.sub(r'[^\w\s]','',s) for s in df['text']]
        
        #Get wordcount, longest word, spelling, and average word length
        df['word_count'] = [len(i.split()) for i in df['text']]
        df['longest_word'] = [find_longest(i.split()) for i in df['text']]
        df['ave_word_len'] = [find_average(i.split()) for i in df['text']]
        spell = SpellChecker()
        df['spell_check'] = [spell_check(spell,i.split()) for i in df['text']]
        
        #Format date
        df['date'] = [datetime.fromtimestamp(int(round(float(i),0)),tz = None).strftime('%Y-%m-%d') for i in df['ts']]
        df = df.drop(['ts'], axis = 1)
        
        #Add channel name
        df['channel'] = [file[:-len(".json")]] * len(df['date'])
        
        #Remap usernames
        try:
            df['user'] = df.replace({"user": user_map})
        except ValueError:
            pass
        
        #Reorganize columns
        df = df.loc[:, ['user','date','channel','word_count','ave_word_len',
                        'longest_word','spell_check','grammar_check','text']]
    
        #Add to main dataframe
        if i == 0:
            main_df = df
        else:
            main_df = main_df.append(df)
    
    #Save and Return
    main_df.to_csv("/".join([directory[:-len("/channels")],"total_wordcount.csv"]),index=False)
    print("Total Word Count File Saved.")
    
    return(main_df)

#Aggregate user data for each week
def user_by_week(directory):
    #Load file
    df = pd.read_csv("/".join([directory[:-len("/channels")],"total_wordcount.csv"]))

    #Weekly values
    df['date'] = pd.to_datetime(df['date'])
    cutoff = max(df['date']) - pd.to_timedelta(7, unit='d')
    temp_df = df.loc[df['date'] >= cutoff]
    agg_df = temp_df.groupby(['user'])['ave_word_len','spell_check','grammar_check'].mean().reset_index()
    agg_df['word_count'] = temp_df.groupby(['user'])['word_count'].sum().reset_index()['word_count']
    agg_df['longest_word'] = temp_df.groupby(['user'])['longest_word'].max().reset_index()['longest_word']
    agg_df['date'] = [datetime.now().strftime('%Y-%m-%d')] * len(agg_df.index)

    #Total wordcount
    total_words = df.groupby(['user'])['word_count'].sum().reset_index()
    total_words.columns = ['user', 'total_words']

    agg_df = pd.merge(agg_df, total_words, how='inner', on = 'user')
    #Reorganize columns
    agg_df = agg_df.loc[:, ['user','date','word_count','ave_word_len','longest_word',
                            'spell_check','grammar_check','total_words']]

    agg_df.to_csv("/".join([directory[:-len("/channels")],"weekly_wordcount.csv"]),index=False)
    print("Weekly Word Count File Saved.")
