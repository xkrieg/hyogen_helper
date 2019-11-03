#Import libraries
import pandas as pd
import nltk
#from nltk.corpus import wordnet
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from textstat.textstat import textstatistics, easy_word_set, legacy_round
from textstat import flesch_kincaid_grade, text_standard, linsear_write_formula
from textstat import dale_chall_readability_score, coleman_liau_index
from textstat import automated_readability_index, smog_index, gunning_fog
from textstat import flesch_reading_ease
from itertools import groupby

#Local functions
from paper_grader.sentence_start import identify_speech

#Helper function for yule
def words(entry):
    return filter(lambda w: (len(w), 0),
                  [w.strip("0123456789!:,.?(){}[]") for w in entry.split()])

#Vocab richness calculator
def yule(entry):

    d = {}
    stemmer = PorterStemmer()
    for w in words(entry):
        w = stemmer.stem(w).lower()
        try:
            d[w] += 1
        except KeyError:
            d[w] = 1
 
    M1 = float(len(d))
    M2 = sum([len(list(g))*(freq**2) for freq, g in groupby(sorted(d.values()))])
 
    try:
        return (M1*M1)/(M2-M1)
    except ZeroDivisionError:
        return 0

#Count syllables
def syllables_count(word): 
	return textstatistics().syllable_count(word)

#Return difficult and easy words from the text 
def difficult_words(text):

    PR_list = pd.read_csv("resources/paper_rater_bad_words.csv")
    PR_list = PR_list['words'].tolist()

    #Create set
    easy_words_set = set()
    diff_words_set = set()

    #Add list of stop words
    stop_words = set(stopwords.words('english'))

    #Find all words in the text
    sentences = sent_tokenize(text)
    for sentence in sentences: 
        words = word_tokenize(sentence)

        for i, word in enumerate(words): 
            syllable_count = syllables_count(word) 
            if word not in easy_word_set and syllable_count >= 3: 
                diff_words_set.add(word.lower())
            if word in easy_word_set and word in PR_list and word not in stop_words:
                try:
                    easy_words_set.add(word.lower())
                except Exception as e:
                    pass

    return(diff_words_set, easy_words_set)

# def get_synonyms(word, POS):
#     
#     if POS == "nouns":
#         target = "".join([word, '.n.01'])
#     elif POS == "verbs":
#         target = "".join([word, '.v.01'])
#     else:
#         target = word
# 
#     synonyms = []
#     antonyms = []
#     
#     for syn in wordnet.synsets(word):
#         print(syn)
#         for l in syn.lemmas():
#             if syllables_count(l.name()) > 1:
#                 synonyms.append(l.name()) 
#             if l.antonyms(): 
#                 antonyms.append(l.antonyms()[0].name())
#                 
#     if len(synonyms) < 1:
#         synonyms = ["No suggestions"]
# 
#     return(set(synonyms))

def vocab_check(text):
    
    #Construct dictionary
    vocab_results = {'dale_chall_readability_score': dale_chall_readability_score(text),
                     'smog_index': smog_index(text), 'gunning_fog': gunning_fog(text),
                     'flesch_reading_ease': flesch_reading_ease(text),
                     'flesch_kincaid_grade': flesch_kincaid_grade(text),
                     'linsear_write_formula': linsear_write_formula(text),
                     'coleman_liau_index': coleman_liau_index(text),
                     'automated_readability_index': automated_readability_index(text),
                     'yule_vocab_richness': yule(text),
                     'total_score': text_standard(text, float_output=True)}
                     
    diff_words, easy_word_dict = difficult_words(text)
    
    return(vocab_results, diff_words, easy_word_dict)

if __name__ == '__main__':
    
    text = "We have a series of example sentences. Some of them include sentences like the one above. Inconsequentially, I am attempting to exasperate the fundamental concept of machine learning. This is an example sentence."
    print(vocab_check(text))
