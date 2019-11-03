#Import libraries
import pandas as pd

def count_transitions(text):
    transition_list = pd.read_csv("resources/transition_words.csv")
    transition_list = transition_list['word'].tolist()
    
    trans_count = 0
    trans_diversity = 0
    for word in transition_list:
        trans_count += text.lower().count(word)
        if text.lower().count(word) > 1:
            trans_diversity += 1
    
    return(trans_count, trans_diversity)
    
if __name__ == "__main__":
    
    #Load essay
    essay_file = "output/hyogenACE_2019/superpower_essay/superpower_essay.csv"
    essays = pd.read_csv(essay_file)
    essays = essays.loc[essays['revision'] == "pre"]["essay_content"]
    essay = essays[0]
    print(count_transitions(essay))
