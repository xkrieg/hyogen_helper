# -*- coding: utf-8 -*-

#Import required libraries
import pandas as pd
import subprocess
import os
import re

def read_pdfs(path, pre_post = "pre"):
    
    #Open repository
    directory_path = "".join([path[:path.index("_".join([pre_post,"reports"]))], path.split("/")[2], ".csv"])
    repository = pd.read_csv(directory_path)

    files = []
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in [f for f in filenames if f.endswith("".join([pre_post, "_report.pdf"]))]:
            files.append(os.path.join(dirpath, filename))

    for file in files:
        
        args = ["pdftotext", '-enc', 'UTF-8', file, '-']
        res = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = res.stdout.decode('utf-8')
        final_grade = [int(s) for s in output.split() if s.isdigit()][-1]
        
        if final_grade >= 90:
            letter = "S"
        elif final_grade < 90 and final_grade >= 80:
            letter = "A"
        elif final_grade < 80 and final_grade >= 70:
            letter = "B"
        elif final_grade < 70 and final_grade >= 60:
            letter = "C"
        else:
            letter = "F"
        
        percentages = re.findall(r'\d+%', output)
        percentages = [int(i.strip('%')) for i in percentages]
        percentages[2] = 100 - int(percentages[2])
        
        if 'Passive Voice Sentences: ' in output:
            passive = output[output.index('Passive Voice Sentences: ') + 25:
                             output.index('Passive Voice Sentences: ') + 27]
            passive = 100 - int(passive.strip('.'))
        else:
            passive = 100
        
        percentages = percentages[0:3] + [passive] + [percentages[i] for i in [6, 16]] + [final_grade] + [letter]
    
        #Get name
        name = file.split("/")[-1]
        name = name[:name.index("_".join(["", pre_post, "report.pdf"]))]

        for i, row in repository.iterrows():
            if repository.loc[i, "name"] == name and repository.loc[i, "revision"] == pre_post:
                repository.loc[i, "word_choice"] = percentages[0]
                repository.loc[i, "transitional_phrases"] = percentages[1]
                repository.loc[i, "sentence_length"] = percentages[2]
                repository.loc[i, "passive_voice"] = percentages[3]
                repository.loc[i, "simple_starts"] = percentages[4]
                repository.loc[i, "vocabulary"] = percentages[5]
                repository.loc[i, "grade"] = percentages[6]
                repository.loc[i, "letter"] = percentages[7]
                    
        #Save csv file
        repository = repository.fillna(0)
        repository.to_csv(directory_path, index = False)
        
    print("Repository updated.")

if __name__ == "__main__":
    
    #Get folder name
    #output/hyogenB_2019/comparative_essay/pre_reports
    path = input('Where are the reports stored? ')
    read_pdfs(path)
    
