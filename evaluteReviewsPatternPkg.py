#import filterData
import json
import nltk
import nltk.corpus
import pattern.en as Pattern
from collections import defaultdict
from nltk.metrics import *
import numpy


def decode_json(line):
    try:
        return json.loads(line)
    except:
       return None

class Eval:
    correlation_vector1 = []
    correlation_vector2 = []
    #Inlcude POS tags as given in two papers

    #{<JJ> <NN>|<JJ> <NNS>||<RB> <JJ>|<RB> <VBG>|<RB> <VBN>|<RB> <VBG>|<RBR> <JJ>|<VBG><NN>|<VBG><NNS>|<VB><NN>|<VB><NNS>|<VBD><NN>|<VBD><NNS>}
    #{<JJ> <NN>|<JJ> <NNS>||<RB> <JJ>|<RB> <VBG>|<RB> <VBN>|<RB> <VBG>|<RBR> <JJ>|<VBG><NN>|<VBG><NNS>|<VB><NN>|<VB><NNS>|<VBD><NN>|<VBD><NNS>}
    positiveChunkPOS_tag = "positive: {<JJ> <NN>|<JJ> <NNS>|<RB> <JJ>|<RB> <VBG>|<RB> <VBN>|<RB> <VBG>|<RBR> <JJ>}"
    negativeChunkPOS_tag = "negative: {<JJ> <NN>|<JJ> <NNS>|<RB> <JJ>|<RB> <VBG>|<RB> <VBN>|<RB> <VBG>|<RBR> <JJ>}"

    def initializeCorrelationVectors(self):
        self.correlation_vector1 = []
        self.correlation_vector2 = []


    # Take all the reviews and get the all the chunks as per a regex
    def getChunks(self,review_text, star, positive_regex, negative_regex, review_id, dictionary_accuracy):
        #try:
        count_pos = 0;count_neg = 0;total_count = 0
        positive_score = 0.0
        negative_score = 0.0
        detectedPositive = False;
        detectedNegative = False;
        positiveParser = nltk.RegexpParser(positive_regex)
        negativeParser = nltk.RegexpParser(negative_regex)
        tokenized_reviews = nltk.word_tokenize(review_text)
        POStagged_reviews = nltk.pos_tag(tokenized_reviews)
        chunk_reviews = positiveParser.parse(POStagged_reviews)
        subtrees = chunk_reviews.subtrees()
        positive_score = 0.0
        negative_score = 0.0

        for each_subtree in subtrees:
            if each_subtree.label() == "positive":

                noun_phrase = ""
                (terms, tags) = zip(*each_subtree)
                for i in range(0,len(terms)):
                    noun_phrase = noun_phrase +" " + terms[i]
                polarity_score = Pattern.sentiment(noun_phrase.strip())
                if polarity_score[0] >=(0.1):
                    positive_score += Pattern.sentiment(noun_phrase)[0]
                    total_count += 1
                    #print "Positives:", noun_phrase, ": " ,positive_score
                    detectedPositive = True
        chunk_reviews = negativeParser.parse(POStagged_reviews)
        subtrees = chunk_reviews.subtrees()
        for subtree in subtrees:

            if subtree.label() == 'negative':

                noun_phrase = ""
                (terms, tags) = zip(*subtree)
                for i in range(0,len(terms)):
                    noun_phrase = noun_phrase + " " + terms[i]
                polarity_score = Pattern.sentiment(noun_phrase.strip())
                if polarity_score[0] <=(-0.1):
                    negative_score += Pattern.sentiment(noun_phrase)[0]
                    total_count += 1
                    #print "Negatives:", noun_phrase, ": " ,negative_score
                    detectedNegative = True;

        if detectedPositive or detectedNegative:
            self.correlation_vector1.append((positive_score+negative_score)/2)
            self.correlation_vector2.append(star)
            dictionary_accuracy[review_id] = ((positive_score+negative_score)/2,star)
        #print ("*") * 50

    def evaluation(self,dictionary_accuracy):
        labelCount = 0.0
        totalCount = 0.0
        #print dictionary_accuracy
        for each_key in dictionary_accuracy.keys():
            if dictionary_accuracy[each_key][1] >= 3.0:
                labelCount+=1
            totalCount +=1
        print "Baseline ", labelCount/totalCount
        labelCount = 0.0
        totalCount = 0.0
        for each_item_key in dictionary_accuracy.keys():

            if dictionary_accuracy[each_item_key][0] >= 0:
                labelCount +=1

            totalCount+=1

        print labelCount
        print totalCount
        print "Current Accuracy (Positive Predictive Value) ", labelCount/totalCount

    #except Exception as e:pass


    #Get reviews
    def parseReviews(self,fileName):
        dictionary_accuracy = defaultdict(float)
        charlotteHospitalReviews = []
        with open(fileName) as f:
            for line in f:
                charlotteHospitalReviews.append(decode_json(line))

        charlotteHospitalReviews = charlotteHospitalReviews[0]

        #Iterate over each review and get chunks
        id =0
        for each_review in charlotteHospitalReviews:

            id+=1
            self.getChunks(each_review['text'],each_review['stars'], self.positiveChunkPOS_tag, self.negativeChunkPOS_tag,id,dictionary_accuracy )
        print "Correlation constant: ", numpy.corrcoef(self.correlation_vector1,self.correlation_vector2)
        return dictionary_accuracy

    def pre_process(self,dictionary_accuracy):
        labeled = []
        predicted = []
        for each_key in dictionary_accuracy.keys():
            if dictionary_accuracy[each_key][0] > 0:
                predicted.append("Good")
            else:
                predicted.append("Bad")

            if(dictionary_accuracy[each_key][1]) >= 3.0:
                labeled.append("Good")
            else:
                labeled.append("Bad")

        return predicted,labeled





e = Eval()
e.initializeCorrelationVectors()
fileName = "Pittsburgh_careCentre_reviews.json"
resultDictionary = e.parseReviews(fileName)
e.evaluation(resultDictionary)
predicted_set, labeled_set = e.pre_process(resultDictionary)
print("Actual Accuracy: ",accuracy(labeled_set,predicted_set))
print(ConfusionMatrix(labeled_set,predicted_set))