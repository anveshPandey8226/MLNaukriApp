import bs4
import pandas
from selenium import webdriver
import time
import random
from nltk import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from nltk import pos_tag
import pickle
import string

with open('vocab_3.pkl', 'rb') as file:
    vocab = pickle.load(file)

company_name = ""
location = ""
stop_words = []
df = ""

def setInput(company,location_name):
    global company_name
    global location
    company_name = company
    location = location_name

def parseJobsInLocation():

    ### Open URL
    global company_name
    global location
    global df
    url = f"https://www.naukri.com/{company_name}-jobs-in-{location}"
    driver = webdriver.Chrome(executable_path='C:/program files/chromedriver.exe')


    ### parse Links from pages
    Link=[]
    for i in range(1,3):
        site = url + "-" + str(i)
        url = ""
        for i in site:
            if i == " ":
                url = url + "-"
            else:
                url = url + i
        print(url)
        driver.get(url)
        timeDelay = random.randrange(10,20)
        time.sleep(timeDelay) 
        soup=bs4.BeautifulSoup(driver.page_source, 'lxml')#returns html of the page
        for i in soup.findAll(attrs={'class':"jobTuple"}):
            for j in i.findAll(attrs={'class':"title ellipsis"}):
                Link.append(j.get('href')) #stores all the link of the job postings
        

    ### parse each link to store job description,skills and role of that company
    description=[]
    role=[]
    skills=[]
    links = []

    for lin in range(len(Link)):
        driver.get(Link[lin])
        time.sleep(1)
        soup=bs4.BeautifulSoup(driver.page_source, 'lxml') 
           
        if soup.find(attrs={'class':"jd-header-comp-name"}) != None and company_name.lower() in soup.find(attrs={'class':"jd-header-comp-name"}).text.lower():
            print("------Company name-------  ",company_name,soup.find(attrs={'class':"jd-header-comp-name"}).text.lower(),end="  ")
            print(company_name.lower() in soup.find(attrs={'class':"jd-header-comp-name"}).text.lower())
            print("company matched")
            description.append(soup.find(attrs={'class':"job-desc"}).text)
            for i in soup.find(attrs={'class':"other-details"}).findAll(attrs={'class':"details"}):
                role.append(i.text)
                break
            
            sk=[]
            for i in soup.find(attrs={'class':"key-skill"}).findAll('a'):
                sk.append(i.text)
            skills.append(sk)
            links.append(Link[lin])
    
    driver.close()

    # Storing the results in data frame
    df = pandas.DataFrame()
    df['role']=role
    df['description']=description
    df['skills']=skills
    df['Job Link']=links

    return df.shape[0]
    




def remove_stopwords(x):
    st = []
    for i in x:
        if i in stop_words:
            continue
        else:
            st.append(i)
    return st

def lemmatize(x):
    lem_words =  []
    for ele in x:
        lem_words.append(lemmatizer.lemmatize(ele))
    return lem_words


def select_NN(x):
    task_keywords = []
    for i in x:
        if i[1] == "NN":
            task_keywords.append(i[0])
        else:
            continue
    return task_keywords


def remove_punctuation(text):
    for punc in list(string.punctuation):
        if punc in text:
            text = text.replace(punc, ' ')
    return text.strip()



def NLP_pipeLine():
    # lower Casing 
    df.description = df.description.apply(lambda x: x.lower())
    # removing unwanted substrings from role
    df['role'] = df['role'].str[6:-1]
    print("Role : ",df["role"].loc[0])
    # punctuation removal
    df["description"] = df["description"].apply(remove_punctuation)
    # Tokenization
    tokenizer = RegexpTokenizer(r"\w+") # Remove puntations
    df['tokenized_sents'] = df.apply(lambda row: tokenizer.tokenize(row['description']), axis=1)
    # Stopward removal
    stop_words = set(stopwords.words("english"))
    stop_words = [x for x in stop_words]
    df['No_Stopwords'] = df['tokenized_sents'].apply(remove_stopwords)
    # Lemmatization
    df["Lemmatized"] = df["No_Stopwords"].apply(lemmatize)
    # pos tagging
    df["POS_Lemmataized"] = df["Lemmatized"].apply(pos_tag)
    # Selecting nouns since all the skills will be noum which help us to classify the job as ML
    df['KeyWords'] = df['POS_Lemmataized'].apply(select_NN)
    df.to_excel('All_Jobs_Records.xlsx')




# Classifying jobs as ML
def check_ML_Job(x):
    temp_role = x[0].lower().split()
    
     
    # checking job title
    for word in temp_role:
        if "machine learning" == word or "ml" == word:
            return "Yes"
        
    # Checking Description  
    temp_desc = x[-1]
    for v in vocab:
        if v in temp_desc:
            # print("---------",temp_desc,"---------")
            return "Yes"
    return "No"
    
    
def unique_links(jobs):
    unique_list = []
    for x in jobs:
        if x[3] not in unique_list:
            unique_list.append(x[3])
    print("Unique list : ",unique_list)
    return unique_list


def store_ML_jobs():
    result = []
    df["ML Job"] = df.apply(check_ML_Job,axis=1)
    record_xls = df[df["ML Job"] == "Yes"]
    record_xls.to_excel('ML_Jobs_Records.xlsx')
    ML_JOBS = df[df["ML Job"] == "Yes"].values.tolist()
    uniq_links = unique_links(ML_JOBS)
    for job in ML_JOBS:
        if job[3] in uniq_links:
            result.append([job[0],job[3]])
            uniq_links.remove(job[3])

    print("store ML Jobs : ",result)
    return result
    
