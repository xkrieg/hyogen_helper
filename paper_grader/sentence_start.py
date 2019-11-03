# -*- coding: utf-8 -*-

#Import librarys
import numpy as np
import nltk
from skbio.diversity.alpha import simpson_e, fisher_alpha, brillouin_d, berger_parker_d

#Identify parts of speech
def identify_speech(sentence):
    
    #Construct dictionary
    POS_dictionary = {"CD":"nouns", "EX":"pronouns", "NN":"nouns", "NNS":"nouns", 
                      "NNP":"nouns", "NNPS":"nouns", "POS":"nouns", "PDT":"pronouns",
                      "PRP":"pronouns", "PRP$":"pronouns", "WP$":"pronouns",
                      "WP": "pronouns", "JJ":"adjectives", "JJR":"adjectives",
                      "JJS":"adjectives", "RB":"adverbs", "RBR":"adverbs",
                      "RBS":"adverbs", "VB":"verbs", "VBD":"verbs", "VBG":"verbs",
                      "VBN":"verbs", "VBP":"verbs", "VBZ":"verbs", "WRB":"adverbs",
                      "CC":"conjunctions", "RP":"particles", "DT":"pronouns",
                      "WDT":"particles", "FW":"others", "UH":"others", "LS":"others",
                      "MD":"others", "IN":"prepositions", "TO":"prepositions"}
    
    #Extract parts of speech                  
    tokens = nltk.word_tokenize(sentence)
    tags = list(dict(nltk.pos_tag(tokens)).values())
    
    for i, tag in enumerate(tags):
        if tag in POS_dictionary:
            tags[i] = POS_dictionary[tag]
        else:
            tags[i] = "others"
    return(tags)

#Define function
def sentence_start(text):

    #Count variables
    ratio_dict = {"nouns":0, "pronouns":0, "verbs":0, "adjectives":0, "adverbs":0,
                  "conjunctions":0, "particles":0, "pronouns":0, "prepositions":0,
                  "others":0,"simpson":0, "fisher":0, "brillouin":0, "berger_parker":0}

    #Tokenize into sentences
    sentences = nltk.tokenize.sent_tokenize(text)
    problem_sentences = []
    
    #Loop through sentences
    for sentence in sentences:
        tags = identify_speech(sentence)
        ratio_dict[tags[0]] = ratio_dict[tags[0]] + 1
        
        if tags[0] == "nouns" or tags[0] == "pronouns":
            problem_sentences.append(sentence)
    
    #Calculate diversity
    simpson = simpson_e(list(ratio_dict.values())[0:7])
    fisher = fisher_alpha(list(ratio_dict.values())[0:7])
    brillouin = brillouin_d(list(ratio_dict.values())[0:7])
    berger_parker = berger_parker_d(list(ratio_dict.values())[0:7])
    
    #Convert to percentage
    #ratio_dict = {k: "".join([str(round(v / len(sentences),4)*100),"%"]) for k, v in ratio_dict.items()}
    
    #Update diversity metric
    ratio_dict['simpson'] = simpson
    ratio_dict['fisher'] = fisher
    ratio_dict['brillouin'] = brillouin
    ratio_dict['berger_parker'] = berger_parker
    
    return(ratio_dict, problem_sentences)
    
if __name__ == '__main__':
    
    text = "We have a series of example sentences. Some of them include sentences like the one above. Inconsequentially, I am attempting to exasperate the fundamental concept of machine learning. This is an example sentence."
    ratio_dict, problem_sentences = sentence_start(text)
    print(ratio_dict)
    print(problem_sentences)
