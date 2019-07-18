# -*- coding: utf-8 -*-

#Import required libraries
import tkinter as tk
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
def initialize(class_name):
    slack = Slacker(class_dict[class_name])
    testAuth = doTestAuth(slack)
    userIdNameMap = getUserMap(slack)
    #print(userIdNameMap)
    return(slack, userIdNameMap)

#Fluency assignment evaluation
def fluency_check(slack, class_name, userIdNameMap):
    folder = getChannels(slack, class_name)
    standardized_files(folder, userIdNameMap)
    user_by_week(folder)
    list_of_reports = send_report_request(folder)
    upload_reports(slack, userIdNameMap, folder, list_of_reports)
    print("Done")
    
#Upload writing assignment
def upload_assignment(slack, class_name, project_name, user_map):
    service = initiate()
    name_link = create_files_from_list(service, class_name, project_name)
    send_links(slack, user_map, name_link)
    
#Download writing assignment
def download_assignment(class_name, project_name, pre_post):
    service = initiate()
    mkdir("".join(["output/",class_name,"/",project_name,"/",pre_post,"_reports"]))
    download_essays(service, class_name, project_name, pre_post)
    
#Distribute writing assignment reports
def distribute_assignment(slack, class_name, project_name, userIdNameMap, pre_post):
    directory = "".join(["output/",class_name,"/",project_name,"/",pre_post,"_reports"])
    #Read from reports
    read_pdfs(directory, pre_post)
    
    if pre_post == "post":
        test_reports = test_result_request(class_name, project_name, pre_post)
    else:
        test_reports = [pdf for pdf in os.listdir(directory) if pdf.endswith('pre_report.pdf')]

    upload_reports(slack, userIdNameMap, directory, test_reports)

if __name__ == "__main__":
    
    #Get selection resources
    class_dict = get_classes()
    project_list = get_projects()
    
    #Preset global variables
    class_name = list(class_dict.keys())[0]
    slack, userIdNameMap = initialize(class_name)
    project_name = project_list[0]
    pre_post_list = ["pre","post"]
    pre_post = "pre"
    
    #Create window
    m=tk.Tk()
    m.title('発言Helper')
    
    #Class dropdown
    tk_classvar = tk.StringVar(m)
    def change_class_dropdown(*args):
        global slack, class_name, userIdNameMap
        class_name = tk_classvar.get()
        slack, userIdNameMap = initialize(class_name)
    tk_classvar.set(class_name) #Set the default option
    class_popupMenu = tk.OptionMenu(m, tk_classvar, *class_dict)
    tk.Label(m, text="Choose a class:").grid(row = 1, column = 0, sticky='w')
    class_popupMenu.grid(row = 2, columnspan=4, column = 0, sticky='n,s,e,w')
    tk_classvar.trace('w', change_class_dropdown)
    
    #Project dropdown
    tk_projectvar = tk.StringVar(m)
    def change_project_dropdown(*args):
        global project_name
        project_name = tk_projectvar.get()
    tk_projectvar.set(project_name) #Set the default option
    project_popupMenu = tk.OptionMenu(m, tk_projectvar, *project_list)
    tk.Label(m, text="Choose a project:").grid(row = 3, column = 0, sticky='w')
    project_popupMenu.grid(row = 4, columnspan=3, column = 0, sticky='e,w')
    tk_projectvar.trace('w', change_project_dropdown)
    
    #Add new project
    def add_project(string_var):
        global project_name
        project_name = string_var.get()
        tk_projectvar.set(string_var.get())
    
    #New project text entry
    v = tk.StringVar(m, value='< new project >')
    new_project = tk.Entry(m, textvariable=v)
    new_project.grid(row = 4, columnspan=3, column = 3, sticky='n,s,e,w')
    
    #Submit new project button
    submit_button = tk.Button(m, text="Submit New Project",
                              command = lambda : add_project(v))
    submit_button.grid(row = 4, columnspan=3, column = 6, sticky='e,w')
    
    #Pre_post dropdown
    tk_prepostvar = tk.StringVar(m)
    def change_prepost_dropdown(*args):
        global pre_post
        pre_post = tk_prepostvar.get()
    tk_prepostvar.set(pre_post) #Set the default option
    prepost_popupMenu = tk.OptionMenu(m, tk_prepostvar, *pre_post_list)
    tk.Label(m, text="Choose pre/post revision:").grid(row = 5, column = 0, sticky='w')
    prepost_popupMenu.grid(row = 6, columnspan=4, column = 0, sticky='n,s,e,w')
    tk_prepostvar.trace('w', change_prepost_dropdown)
    
    ### Four Buttons ###
    fluency_button = tk.Button(m, text="Fluency Check",
            command = lambda : fluency_check(slack, class_name, userIdNameMap))
    fluency_button.grid(row = 2, columnspan=4, column = 4, sticky='n,s,e,w')
    
    upload_button = tk.Button(m, text="Upload Writing Project",
            command = lambda : upload_assignment(slack, class_name, project_name, userIdNameMap))
    upload_button.grid(row = 4, columnspan=3, column = 9, sticky='n,s,e,w')
    
    download_button = tk.Button(m, text="Download Writing Project",
            command = lambda : download_assignment(class_name, project_name, pre_post))
    download_button.grid(row = 6, columnspan=4, column = 4, sticky='n,s,e,w')
    
    distribute_button = tk.Button(m, text="Distribute Writing Reports",
            command = lambda : distribute_assignment(slack, class_name, project_name, 
                                                     userIdNameMap, pre_post))
    distribute_button.grid(row = 6, columnspan=4, column = 8, sticky='n,s,e,w')
    
    #Open Resource Folder
    def open_resources():
        check_call(['open', 'resources'])
    resources_button = tk.Button(m, text="Resources...", command = open_resources)
    resources_button.grid(row = 2, columnspan=4, column = 8, sticky='n,s,e,w')
    
    #Exit button
    exit_button = tk.Button(m, text='Exit', width=25, command=m.destroy)
    exit_button.grid(row = 7, column = 4, columnspan=4, sticky='n,s,e,w')
    m.mainloop()
