#import filterData
import json
import nltk
import nltk.corpus
import pattern.en as Pattern
from collections import defaultdict

dictionary_accuracy = defaultdict(float)
def decode_json(line):
    try:
        return json.loads(line)
    except:
       return None

# Take all the reviews and get the all the chunks as per a regex
def getChunks(review_text, star, positive_regex, negative_regex, review_id):
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
            if polarity_score[0] <=(-0.1):
                negative_score += Pattern.sentiment(noun_phrase)[0]
                total_count += 1
                print "Negatives:", noun_phrase, ": " ,negative_score
            detectedNegative = True;

    if detectedPositive or detectedNegative:
        dictionary_accuracy[review_id] = ((positive_score+negative_score)/2,star)
    print ("*") * 50


def getBaseline(review_list):
    labelCount = 0.0
    totalCount = 0.0
    for each_review in review_list:
        if each_review['stars'] >= 3.0:
            labelCount+=1.0
        totalCount+=1.0

    return labelCount/totalCount
#print getBaseline(charlotteHospitalReviews)

def evaluation():
    labelCount = 0.0
    totalCount = 0.0
    print dictionary_accuracy
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
    print "Current Accuracy ", labelCount/totalCount

    #except Exception as e:pass

#Inlcude POS tags as given in two papers
positiveChunkPOS_tag = "positive: {<JJ> <NN>|<JJ> <NNS>|<NN> <NNS>}"
negativeChunkPOS_tag = "negative: {<JJ> <NN>|<JJ> <NNS>|<NN> <NNS>}"


#Get reviews
charlotteHospitalReviews = []
with open("Charlotte_hospital_reviews.json") as f:
    for line in f:
        charlotteHospitalReviews.append(decode_json(line))

charlotteHospitalReviews = charlotteHospitalReviews[0]

#Iterate over each review and get chunks
t =0
for each_review in charlotteHospitalReviews:
    #print each_review['text']
    t+=1
    getChunks(each_review['text'],each_review['stars'], positiveChunkPOS_tag, negativeChunkPOS_tag,t )
