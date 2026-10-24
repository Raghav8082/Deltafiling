import time
import requests


HEADERS = { "User-Agent" : "RaghavVerma vermaraghav879@gmail.com"};  
last_request = 0 ; 

def get_json(url): 
    global last_request; 
    wait = 0.12 -(time.time() -  last_request) ; 

    if wait> 0  : 
        time.sleep(wait)

    last_request = time.time()


    r = requests.get(url,  headers =  HEADERS  , timeout = 30 )
    r.raise_for_status()    
    return r.json()


def get_text(url):
    global last_request
    wait = 0.12 - (time.time() - last_request)
    if wait > 0:
        time.sleep(wait)
    last_request = time.time()

    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.text    


# if __name__ == "__main__":
#     data = get_json("https://data.sec.gov/submissions/CIK0000320193.json")
#     print(data["name"])  # should print: Apple Inc.
