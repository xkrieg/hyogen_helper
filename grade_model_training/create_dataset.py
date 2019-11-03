#Import libraries
import pandas as pd
import progressbar
import os

#Local functions
from paper_grader.vocabulary import *
from paper_grader.sentence_start import *
from paper_grader.spelling import *
from paper_grader.grammar import *
from paper_grader.statistics import *
from paper_grader.passive_voice import Tagger
from paper_grader.transitional_phrases import count_transitions

#Detect passive voice
def passive_master(essay):
    t = Tagger()
    pass_dict = {"passive":0, "total":0, "passive_sent": list()}
    for token in nltk.sent_tokenize(essay):
        try:
            if t.is_passive(token):
                pass_dict["passive"] += 1
                pass_dict["passive_sent"].append(token)
            pass_dict["total"] += 1
        except Exception as e:
            pass
    pass_dict["percent_active"] = 1-pass_dict["passive"]/pass_dict["total"]
    return(pass_dict)

#Extract information from essays
def check_essay(essay):
    output = [getParaCount(essay), getSentenceCount(essay), getWordCount(essay)]
    
    #Problem spaces
    problem_spaces, essay = check_spaces(essay)
    output.append(problem_spaces)
    
    #Spelling (number of errors)
    num_misspelt, misspelt_suggestions = spellCheck(essay)
    output.append(num_misspelt)
    
    #Grammar (number of errors)
    num_grammar_problems, grammar_suggestions = grammar_check(essay)
    output.append(num_grammar_problems)

    #Vocabulary (*vocab_results*, number diff words, number easy words)
    vocab_results, diff_words, easy_word_dict = vocab_check(essay)
    output = output + list(vocab_results.values())
    
    #Sentence Start (4 diversity statistics)
    ratio_dict, problem_sentences = sentence_start(essay)
    output = output + list(ratio_dict.values())
    
    #Passive Voice (*percent passive*)
    pass_dict = passive_master(essay)
    output.append(pass_dict['percent_active'])
    
    #Sentence Length (average, sd, *percent_short sentences*, percent long sentences)
    ave_sent_length, sd_sent_length, percent_short, percent_long = sentence_length(essay)
    output = output + [ave_sent_length, sd_sent_length, percent_short, percent_long]
    
    #Transitional Phrases (number, number different kinds)
    trans_count, trans_diversity = count_transitions(essay)
    output= output + [trans_count, trans_diversity]

    return(output)

#Generate list of essays
possible_suffix = ['superpower_essay.csv','100_birthday_essay.csv','analysis_essay.csv',
                   'argumentative_essay.csv','comparative_essay','process_essay.csv',
                   'descriptive_essay.csv','narrative_essay.csv','summary_essay.csv']

list_of_essay_files = []
for suffix in possible_suffix:
    for root, dirs, files in os.walk("output"):
        for file in files:
            if file.endswith(suffix):
                list_of_essay_files.append("/".join([root,file]))

#Load essays
paper_rater = pd.read_csv(list_of_essay_files[0])
for essay_file in list_of_essay_files[1:]:
    essays = pd.read_csv(essay_file)
    paper_rater = paper_rater.append(essays)
paper_rater.reset_index()

#Score essays with new system
df = list()
pbar = progressbar.ProgressBar(paper_rater.shape[0])
pbar.start()
for index, row in paper_rater.iterrows():
    pbar.update(index)
    essay = row['essay_content']
    df.append([row['grade'], row['revision']] + check_essay(essay))
    
#Create masterfile
df = pd.DataFrame.from_records(df)
df.columns=['grade', 'prepost', 'paragraph_count', 'sentence_count',
            'word_count', 'num_problem_spaces', 'num_misspelt',
            'num_grammar_problems', 'dale_chall_readability_score',
            'smog_index', 'flesch_reading_ease', 'flesch_kincaid_grade',
            'linsear_write_formula', 'coleman_liau_index',
            'automated_readability_index', 'yule_vocab_richness',
            'total_score', 'nouns', 'pronouns', 'verbs', 'adjectives',
            'adverbs', 'conjunctions', 'particles', 'pronouns', 
            'prepositions', 'others', 'simpson', 'fisher', 'brillouin', 
            'berger_parker', 'percent_active', 'ave_sent_length', 
            'sd_sent_length', 'percent_short', 'percent_long',
            'trans_count', 'trans_diversity']
df.to_csv("deep_learn_data.csv", index = False)
print(df)
