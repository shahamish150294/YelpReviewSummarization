import tarfile
import json
#Code to read the tar file
#t = tarfile.open('yelp_dataset_challenge_academic_dataset.tar', 'r')
#business_json = []
#Unzip the tar files

#Code to read json data by line
def decode_json(line):
    try:
        return json.loads(line)
    except:
        return None

def filterData(city):
        yelp_data_business = []
        with open("yelp_academic_dataset_business.json") as f:
                for line in f:
                        yelp_data_business.append(decode_json(line))

        hospital_count  = 0
        careCentres_count  = 0
        business_hospitals = []
        business_careCentres = []
        careCentres = ['Assisted Living Facilities', 'Counseling & Mental Health', 'Habilitative Services','Home Health Care', 'Medical Centers', 'Rehabilitation Center',
                                'Weight Loss Centers', 'Child Care & Day Care', 'Urgent Care', 'Skin Care']

        #Check whether data for business:Health & Medical is present, if present look for group hospital data and group other centers
        for each_business in yelp_data_business:
                if ('Health & Medical' in each_business['categories'] and city in each_business['city']):
                        if ( 'Hospitals' in each_business['categories']):
                                business_hospitals.append(each_business)
                                hospital_count +=1
                        else:
                                for eachCentre in careCentres:
                                        if ( eachCentre in each_business['categories']):
                                                business_careCentres.append(each_business)
                                                careCentres_count +=1


        yelp_data_review = []
        hospital_review_count  = 0
        careCentres_review_count  = 0
        business_review_hospitals = []
        business_review_careCentres = []

        with open("yelp_academic_dataset_review.json") as f:
                for line in f:
                        each_review_json = decode_json(line)
                        for each_hospital in business_hospitals:
                                if (each_review_json['business_id'] == each_hospital['business_id']):
                                        business_review_hospitals.append(each_review_json)
                                        hospital_review_count +=1

                        for each_careCentre in business_careCentres:
                                if (each_review_json['business_id'] == each_careCentre['business_id']):
                                        business_review_careCentres.append(each_review_json)
                                        careCentres_review_count +=1



        # To store the reviews in json
        fileName = city+'_hospital_reviews.json'
        with open(fileName,'w') as outputfile:
            json.dump(business_review_hospitals,outputfile	)

        fileName = city+'_careCentre_reviews.json'
        with open(fileName,'w') as outputfile:
            json.dump(business_review_careCentres,outputfile)

#filterData("Pittsburgh")
filterData("Charlotte")
