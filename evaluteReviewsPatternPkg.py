#import filterData
import json
import csv
import codecs
import nltk
import nltk.corpus
import pattern.en as Pattern
from collections import defaultdict
from nltk.metrics import *
import numpy
import sys

#To resolve the ascii encoding error
reload(sys)
sys.setdefaultencoding('utf-8')
def decode_json(line):
    try:
        return json.loads(line)
    except:
       return None

class Eval:
    correlation_vector1 = []
    correlation_vector2 = []

    #Inlcude POS tags as given in two papers

    positiveChunkPOS_tag = "positive: {<JJ> <NN>|<JJ> <NNS>|<RB> <JJ>|<RBR> <JJ>}"#|<RB> <JJ>|<RB> <VBG>|<RB> <VBN>|<RB> <VBG>|<RBR> <JJ>}"
    negativeChunkPOS_tag = "negative: {<JJ> <NN>|<JJ> <NNS>|<RB> <JJ>|<RBR> <JJ>}"#<RB> <JJ>|<RB> <VBG>|<RB> <VBN>|<RB> <VBG>|<RBR> <JJ>}"

    def initializeCorrelationVectors(self):
        self.correlation_vector1 = []
        self.correlation_vector2 = []


    # Take all the reviews and get the all the chunks as per a regex
    def getChunks(self,review_text, star, positive_regex, negative_regex, review_id, dictionary_accuracy, resultsWriter):
        #try:
        count_pos = 0;count_neg = 0;total_count = 0
        #####
        # Following variables to add data to result csv
        results_csv_row = {}
        results_positive_phrases = []
        results_negative_phrases = []
        results_csv_row["Reviews"] = review_text
        results_csv_row["Stars"] = star

        #####
        review_phrases = []
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
                if polarity_score[0] >=(0.2) and polarity_score[1]>=0.5:
                    results_positive_phrases.append(noun_phrase+"||")
                    positive_score += Pattern.sentiment(noun_phrase)[0]
                    total_count += 1
                    print "Positives:", noun_phrase, ": " ,positive_score

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
                if polarity_score[0] <=(-0.2) and polarity_score[1]>=0.5:
                    results_negative_phrases.append(noun_phrase+"||")
                    negative_score += Pattern.sentiment(noun_phrase)[0]

                    total_count += 1
                    print "Negatives:", noun_phrase, ": " ,negative_score
                    detectedNegative = True;

        if detectedPositive or detectedNegative:


            sentence_score = (positive_score+negative_score)/2
            if sentence_score > 0:
                results_csv_row["Positive_Phrases"] = results_positive_phrases
                results_csv_row["Negative_Phrases"] = []
                results_csv_row["Positive_Polarity"] = sentence_score
                results_csv_row["Negative_Polarity"] = "NA"

            else:
                results_csv_row["Positive_Phrases"] = []
                results_csv_row["Negative_Phrases"] = results_negative_phrases
                results_csv_row["Negative_Polarity"] = sentence_score
                results_csv_row["Positive_Polarity"] = "NA"

            resultsWriter.writerow(results_csv_row)
            self.correlation_vector1.append(sentence_score)
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
        csvfile = codecs.open(fileName.strip(".json")+"_Results.csv", 'w', 'utf-8')
        fieldnames = ["Reviews", "Stars", "Positive_Phrases", "Positive_Polarity", "Negative_Phrases", "Negative_Polarity"]
        resultsWriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

        charlotteHospitalReviews = []
        with open(fileName) as f:
            for line in f:
                charlotteHospitalReviews.append(decode_json(line))

        charlotteHospitalReviews = charlotteHospitalReviews[0]

        #Iterate over each review and get chunks
        id =0
        for each_review in charlotteHospitalReviews:

            id+=1
            self.getChunks(each_review['text'],each_review['stars'], self.positiveChunkPOS_tag, self.negativeChunkPOS_tag,id,dictionary_accuracy, resultsWriter )
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

    def generateCorrelationGraph(self,outputCSVFile):
        csvfile = codecs.open(outputCSVFile.strip(".json")+"_Plot.csv", 'w', 'utf-8')
        fieldnames = ["Stars", "Polarity Values"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(len(self.correlation_vector1)):
            csv_row = {}
            csv_row["Stars"] = self.correlation_vector2[i]
            csv_row["Polarity Values"] = self.correlation_vector1[i]
            writer.writerow(csv_row)

outputFile = "Phoenix_careCentre_reviews.csv"
fileName = "Phoenix_hospital_reviews.json"

e = Eval()
e.initializeCorrelationVectors()
resultDictionary = e.parseReviews(fileName)
e.evaluation(resultDictionary)
predicted_set, labeled_set = e.pre_process(resultDictionary)
print("Actual Accuracy: ",accuracy(labeled_set,predicted_set))
print(ConfusionMatrix(labeled_set,predicted_set))
#e.generateCorrelationGraph(fileName)