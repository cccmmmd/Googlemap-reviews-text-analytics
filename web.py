import requests
from bs4 import BeautifulSoup

token = ''
data = []
data2 = []
page = 1

def get_20_reviews():
    global page, token
    while page < 3:
        if token == '':
            get_reviews_data(tkn='')
        else:
            get_reviews_data(tkn=token)
        page += 1
    return data
def remove_common(a, b):
    a, b = list(set(a).difference(b)), list(set(b).difference(a))
 
    
def get_reviews_data(tkn):
    global token
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    response = requests.get(f"https://www.google.com/async/reviewDialog?hl=zh-TW&async=feature_id:0x3442abc9159d64e9:0xc7a5f9f2ed41b74a,next_page_token:{tkn},sort_by:newestFirst,start_index:,associated_topic:,_fmt:pc", headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')
    
    token = soup.select_one('.gws-localreviews__general-reviews-block')['data-next-page-token']


    for el in soup.select('.gws-localreviews__google-review'):
        node = el.select_one('.f5axBf > span')
        if node is not None:
           tempreview = node.get_text(separator=' ').split()
        else:
           tempreview = None
        data.append(tempreview)

        node2 = el.select_one('.k8MTF')
        if node2 is not None:
           tempreview2 = node2.get_text(separator=' ').split()
        else:
           tempreview2 = None
        data2.append(tempreview2)

    
    #print(data)
    #print(data2)

    for d1 in data:
        for d2 in data2:
            #for ds2 in d2:
            print(d1, d2)
            
  
    for user_data in data:
        print(user_data)

    for user_data in data2:
       print(user_data)
    
    return data

get_20_reviews()