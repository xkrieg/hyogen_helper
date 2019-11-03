#Import libraries
import pandas as pd
from nltk.tokenize import sent_tokenize
from pylanguagetool import api
import re

def get_paragraph(text):
	
	#Split the text into paragraphs
	paraList = text.splitlines()
	
	#Remove blank lines from the list of paragraphs
	paraList[:] = [element for element in paraList if element != ""]
	return paraList

def remove_header(text):
    
    #Remove and rejoin essay without first three paragraphs
    text = "\n".join(get_paragraph(text)[3:])
    return(text)

def check_spaces(text):
    
    #Count space problems
    problem_spaces = 0
    for i, a in enumerate(text[0:-1]):
        if a == "." or a == "," or a == ":" or a == "!" or a == "?":
            if (text[i+1].isspace()) == False: 
                problem_spaces += 1
    
    #Fix them
    text = re.sub(r'(?<=[.,])(?=[^\s])', r' ', text)
    
    #Remove non-English characters
    text = text.encode('ascii', errors='ignore').decode('utf-8')
    
    return(problem_spaces, text)

def api_request(text):
    response = api.check(text, "https://languagetool.org/api/v2/", "en-US")
    assert "software" in response
    try:
        match = response["matches"][0]
    except(IndexError):
        match = "This sentence does not seem to contain any grammatical errors."
    return(match)
    
def grammar_check(text):
    sentences = sent_tokenize(text)
    grammar_errors = {}
    for i, sentence in enumerate(sentences):
        match = api_request(sentence)
        if match != "This sentence does not seem to contain any grammatical errors.":
            temp_dict = {}
            temp_dict['sentence'] = match['context']['text']
            temp_dict['correction'] = match['message']
            grammar_errors[i] = temp_dict
    return(len(grammar_errors), grammar_errors)
    
if __name__ == '__main__':
    #Load essay
    essay_file = "output/hyogenACE_2019/superpower_essay/superpower_essay.csv"
    essays = pd.read_csv(essay_file)
    essays = essays.loc[essays['revision'] == "pre"]["essay_content"]
    
    text = essays[15]
    text = remove_header(text)
    spacing_errors, text = check_spaces(text)
    print("Spacing Errors:", spacing_errors)
    print(grammar_check(text))
