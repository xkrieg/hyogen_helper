import nltk
import math
import re

def getWordCount(text):
	wordList = re.findall(r'\w+', text)
	return len(wordList)

def getSentenceCount(text):
	sentList = nltk.sent_tokenize(text)
	return len(sentList)

def getParaCount(text):
	#Split the text into paragraphs
	paraList = text.splitlines()
	#Remove blank lines from the list of paragraphs
	paraList[:] = [element for element in paraList if element != ""]
	return len(paraList)

def getStdDevSentenceLength(text, mean):

	sentList = nltk.sent_tokenize(text)
	nr=0.0
	for sent in sentList:
		nr = nr + (getWordCount(sent) - mean)**2
	
	return math.sqrt(nr/len(sentList))

def sentence_length(text):
	#split the essay into sentences
	sentList = nltk.sent_tokenize(text)
	
	short_sent = 0
	long_sent = 0
	sumSentLength = 0
	for sent in sentList:
	    sumSentLength = sumSentLength + getWordCount(sent)
	    if getWordCount(sent) < 17:
	        short_sent =+ 1
	    if getWordCount(sent) > 35:
	        long_sent =+ 1

	ave_sent_length = float(sumSentLength)/len(sentList)
	sd_sent_length  = getStdDevSentenceLength(text, ave_sent_length)
	percent_short = short_sent / len(sentList)
	percent_long  = long_sent / len(sentList)

	return(ave_sent_length, sd_sent_length, percent_short, percent_long)
