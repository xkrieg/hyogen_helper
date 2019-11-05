# -*- coding: utf-8 -*-

#Import required libraries
from subprocess import call
import os

from functions.slack_functions import mkdir

#Activate Rscript
def send_report_request(filename):
    command = "".join(["/usr/local/bin/Rscript ", "--vanilla ",
                       "report_builder.R ", filename])
    call(command, shell=True, stdin=None, stdout=None, stderr=None,
         close_fds=True, bufsize=0)
    
    #Gather list of pdfs
    directory = "".join([filename.replace('/channels',''), "/reports"])
    mkdir(directory)
    list_of_reports = [pdfs for pdfs in os.listdir(directory) if pdfs.endswith('.pdf')]
    
    return(list_of_reports)

#Written reports
def test_result_request(class_name, project_name, pre_post):
    command = "".join(["/usr/local/bin/Rscript ", "--vanilla ",
                       "test_result_builder.R ", class_name, " ", project_name])
    call(command, shell=True, stdin=None, stdout=None, stderr=None,
         close_fds=True, bufsize=0)
    
    #Gather list of pdfs
    directory = "".join(['output/',class_name,"/",project_name,"/",pre_post,"_reports"])
    mkdir(directory)
    list_of_reports = [pdfs for pdfs in os.listdir(directory) if pdfs.endswith('final_report.pdf')]
    
    return(list_of_reports)
