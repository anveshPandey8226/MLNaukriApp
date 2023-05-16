from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['company_database']
collection_comp = db['companies-info']
collection_ML_job = db['ML_Jobs']



Openings = collection_ML_job.find().sort('_id',-1).limit(0)
for open in Openings:
    print(open['Company_name'])