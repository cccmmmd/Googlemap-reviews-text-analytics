import requests
from bs4 import BeautifulSoup

token = ''
id = '0x3442a83fd0338d9d:0x8eaca58f28b364f6'
data_words = []
page = 0


def get_20_reviews():
    global page, token
    if token == '':
        get_reviews_data(tkn='')
        page += 1
    else:
        if page < 2:
            get_reviews_data(tkn=token)
            page += 1
    
    print(data_words)   
            
    return data_words

 
    
def get_reviews_data(tkn):
    global token, id
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    response = requests.get(f"https://www.google.com/async/reviewDialog?hl=zh-TW&async=feature_id:{id},next_page_token:{tkn},sort_by:newestFirst,start_index:,associated_topic:,_fmt:pc", headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')
    
    token = soup.select_one('.gws-localreviews__general-reviews-block')['data-next-page-token']


    for el in soup.select('.gws-localreviews__google-review'):
        node = el.find("span", {"jscontroller":"MZnM8e"})
        # node = el.select_one('.Jtu6Td > span')
        if node.text != '':
            tempreview = node.text
            # data_words.append(tempreview)
            data_words.append({'review': tempreview})

    #return data_words

get_20_reviews()