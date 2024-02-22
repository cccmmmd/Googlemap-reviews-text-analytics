import requests
from bs4 import BeautifulSoup

token = ''
# id = '0x3442a83fd0338d9d:0x8eaca58f28b364f6'
cid = ''
data_words = []
page = 0
name = ''

def reset():
    global page, cid, data_words,name,token
    cid = ''
    data_words = []
    page = 0
    name = ''
    token = ''

def get_20_reviews(id):
    global page, token, cid, data_words
    cid = id
   
    if token == '':
        if page < 1:
            get_reviews_data(tkn='')
            page += 1
            get_20_reviews(id)
    else:
        if page < 2:
            get_reviews_data(tkn=token)
            page += 1
            get_20_reviews(id)
    
    # print(data_words)   
            
    return data_words

def fetch_name():
    return name
 
    
def get_reviews_data(tkn):
    global token, cid, name
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    response = requests.get(f"https://www.google.com/async/reviewDialog?hl=zh-TW&async=feature_id:{cid},next_page_token:{tkn},sort_by:newestFirst,start_index:,associated_topic:,_fmt:pc", headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')
    token = soup.select_one('.gws-localreviews__general-reviews-block')['data-next-page-token']
    name = soup.select_one('.Lhccdd > div:first-of-type ').text

    for el in soup.select('.gws-localreviews__google-review'):
        preview = el.find("span", {"class":"review-full-text"})
        node = el.find("span", {"jscontroller":"MZnM8e"})
        tempreview = ''
        # node = el.select_one('.Jtu6Td > span')
        
        if node.text != '':
            if preview is None:
                tempreview = node.text
            else:
                tempreview = preview.text
            data_words.append({
                'review': tempreview,
                'time': el.select_one('.dehysf').text.strip(),
                })

    #return data_words

