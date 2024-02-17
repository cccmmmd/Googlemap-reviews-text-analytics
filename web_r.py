import requests
from bs4 import BeautifulSoup

token = ''
#id = '0x3442a8198dabb32d:0xd722c6ab25f13d86'
id = '0x3442abc9159d64e9:0xc7a5f9f2ed41b74a'
data_words = []
data_points = []
data_points_show = []
data_show = []
page = 0

def webdisplay():
    for i1,d1 in enumerate(data_words):
        if d1 is not None and data_points[i1] is not None:
            data_show.append(' '.join(list(set(data_words[i1]).difference(set(data_points[i1])))))
        else:
            data_show.append(None)
    for user_data2 in data_points_show:
        print(user_data2)   

def get_20_reviews():
    global page, token
    if token == '':
        get_reviews_data(tkn='')
        page += 1
    else:
        if page < 2:
            get_reviews_data(tkn=token)
            page += 1
        else:
            for i1,d1 in enumerate(data_words):
                for i2,d2 in enumerate(data_points):
                    if d1 is not None and d2 is not None:
                        data_words[i1] = [x for x in d1 if x]
                        data_points[i2] = [x for x in d2 if x]
    
      
            
    return data_show

 
    
def get_reviews_data(tkn):
    global token, id
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    response = requests.get(f"https://www.google.com/async/reviewDialog?hl=zh-TW&async=feature_id:{id},next_page_token:{tkn},sort_by:newestFirst,start_index:,associated_topic:,_fmt:pc", headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')
    
    token = soup.select_one('.gws-localreviews__general-reviews-block')['data-next-page-token']


    for el in soup.select('.gws-localreviews__google-review'):
        node = el.select_one('.f5axBf > span')
        if node is not None:
           tempreview = [x.strip('\xa0\xa0|\xa0\xa0') for x in node.get_text(' ').split()]
        else:
           tempreview = None
        
        data_words.append(tempreview)

        node2 = el.select_one('.k8MTF')
        if node2 is not None:
           tempreview2 = [x.strip('\xa0\xa0|\xa0\xa0') for x in node2.get_text(' ').split()]
           tempreview3 = node2.get_text().split('\xa0\xa0|\xa0\xa0')
        else:
           tempreview2 = None
           tempreview3 = None
        data_points.append(tempreview2)
        data_points_show.append(tempreview3)

    
  
    # for user_data1 in data_words:
    #     print(user_data1)

    
    webdisplay() 
    # return data_words

get_20_reviews()