from time import sleep
import requests
from statics import *
import re
import json
import os

cve_endpoint = "https://services.nvd.nist.gov/rest/json/cves/1.0"
cpe_endpoint = "https://services.nvd.nist.gov/rest/json/cpes/1.0"
k = apikey

def seek(libraries_dict, fname):

    if os.path.isfile(fname):
        print(f"Persistence file found: {fname}!")
        with open(fname,"r") as f:
            data = f.read()
            modules_cves_dict = json.loads(data)
            return modules_cves_dict

    cpes=[]

    if isinstance(libraries_dict, dict):
        keywords = libraries_dict.keys()
    elif isinstance(libraries_dict, list):
        keywords = libraries_dict

    counter = 0
    print("\nPhase 1: Gathering CPEs from NVD API")

    for kw in keywords:

        kw = kw.lower()
        kw2 = kw

        if "-" in kw:
            kw2 = kw.replace("-","_")
        
        elif "_" in kw:
            kw2 = kw.replace("_","-")

        counter +=1
        progress = round((counter*100)/len(libraries_dict),2)
        print(f'Completed: {progress}%', end='\r')
        r = requests.get(f'{cpe_endpoint}?keyword={kw}&resultsPerPage=300')
        print(f'search: {kw}')
        if r.status_code !=200:
            if r.status_code == 503:
                print("NVD API is down :(")
                exit(0)
            banned = True

            while banned:
                print("Banned from NVD Api, waiting...")
                sleep(10)
                r = requests.get(f'{cpe_endpoint}?keyword={kw}&resultsPerPage=300')
                if r.status_code !=200:
                    banned=True
                elif r.status_code == 200:
                    r = requests.get(f'{cpe_endpoint}?keyword={kw}&resultsPerPage=300')
                    try:
                        if (r.status_code == 200):
                            if r.json()["error"] == 'Invalid apiKey':
                                print("Invalid API Key")
                                sleep(5)
                                banned = True
                    except:
                        banned=False
    
        if(len(r.json()["result"]["cpes"])) > 0:
            for i in r.json()["result"]["cpes"]:
                if re.search(rf':({kw}|{kw2}):', i["cpe23Uri"]):
                    cpes.append(i["cpe23Uri"])

    modules_cves_dict = {}
    
    counter = 0    
    print("\nPhase 2: Gathering CVEs from NVD API")

    for cpe in cpes:
        counter +=1
        progress = round((counter*100)/len(cpes),2)
        print(f'Completed: {progress}%', end='\r')
        cves=[]

        r =  requests.get(f'{cve_endpoint}?cpeMatchString={cpe}&resultsPerPage=200')

        if(len(r.json()["result"]["CVE_Items"])) > 0:
            cve_items = r.json()["result"]["CVE_Items"]
            
            for cve_item in cve_items:
                cves.append(cve_item["cve"]["CVE_data_meta"]["ID"])
            
        modules_cves_dict[cpe]=cves
        
        with open(fname,"w") as f:
            f.write(json.dumps(modules_cves_dict))

    if len(modules_cves_dict) > 0:
        print("Not empty") # FAIL 
    else:
        print("Emtpy") # PASS
    return modules_cves_dict
#------endofSeek



'''

def oldSelect(modules_cves_dict, libraries_file):

    choice_dict = {}
    c = 0
    

    if isinstance(libraries_file, dict):
        kws = libraries_file.keys()

    else:
        kws = libraries_file


    for i in modules_cves_dict:
        if len(modules_cves_dict[i]) != 0:
            
            for x in kws: 
                x = x.lower()
                x2 = x

                if "-" in x:
                    x2 = x.replace("-","_")
                
                elif "_" in x:
                    x2 = x.replace("_","-")

                if isinstance(libraries_file, dict):
                    if x in i:
                        print(f'[{c}] {i} {x}:{libraries_file[x]}')
                        choice_dict[str(c)]=i
                        c +=1
                    
                    elif x2 in i:
                        print(f'[{c}] {i} {x2}:{libraries_file[x]}')
                        choice_dict[str(c)]=i
                        c +=1    

                if isinstance(libraries_file, list):
                    if x in i:
                        print(f'[{c}] {i} {x}')
                        choice_dict[str(c)]=i
                        c +=1
                    
                    elif x2 in i:
                        print(f'[{c}] {i} {x2}')
                        choice_dict[str(c)]=i
                        c +=1    
    
    while True:
        print("[x] back to menu")

        choice = input("select module or option: ")

        if choice=="x":
            break
        else:
            try:
                cpe = choice_dict[choice]
                cves = modules_cves_dict[cpe]
                print(cpe)
                for x in cves:
                    print(x)
            except:
                print("Select a valid module!")
        
        
        

'''