from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import WebScrapeJobs

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['company_database']
collection_comp = db['companies-info']
collection_ML_job = db['ML_Jobs']

curr_job_count = 0
company_name = ""

@app.route('/', methods=['GET'])
def index():
    global curr_job_count
    curr_job_count = 0
    return render_template('form_css.html')






@app.route('/submit', methods=['POST'])
def submit():
    global curr_job_count
    global company_name
    # Get the company name and location from the form submission
    company_name = request.form.get('company_name')
    location = request.form.get('location')

    print(company_name,location)


    # Store company name and Location in the database
    company_data = {
                'Company_name': company_name,
                'Location': location
            }
    collection_comp.insert_one(company_data)


    #########################################################################################

    #   Passing company_name and location to WebScrapeJobs.py

    WebScrapeJobs.setInput(company_name,location)
    count = WebScrapeJobs.parseJobsInLocation()
    if count != 0:
        WebScrapeJobs.NLP_pipeLine()
        ML_jobs = WebScrapeJobs.store_ML_jobs()
        print(ML_jobs)
        for job in ML_jobs:
            # Create a document to be inserted
            Job_data = {
                'Company_name': company_name,
                'Location': location,
                'Job_Role': job[0],
                'Apply_Link': job[1]
            }

            # Insert the document into the collection
            collection_ML_job.insert_one(Job_data)

            curr_job_count += 1
        
        print(curr_job_count)
        print('Company information stored successfully.')
        return redirect(url_for('result'))
    else:
        return f'{company_name} INFORMATION DOES NOT EXIST'
    #########################################################################################
    
    
    


@app.route('/result')
def result():
    global curr_job_count

    # Retrieve all companies looking for ML developers
    
    Openings = collection_ML_job.find().sort('_id',-1).limit(curr_job_count)
    # if len(Openings)==0:
    #     return 'Currently No ML Jobs opening at {company_name}'
    print(Openings)

    curr_job_count = 0

    return render_template('result_css.html', Openings = Openings,company_name=company_name.upper())

if __name__ == '__main__':
    app.run()
