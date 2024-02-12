import requests
from bs4 import BeautifulSoup

def get_reviews_data():
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }

    response = requests.get("https://www.google.com/async/reviewDialog?hl=zh-TW&async=feature_id:0x3442abc9159d64e9:0xc7a5f9f2ed41b74a,next_page_token:,sort_by:newestFirst,start_index:,associated_topic:,_fmt:pc", headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')
    
    user = []
    
    token = soup.select_one('.gws-localreviews__general-reviews-block')['data-next-page-token']


    for el in soup.select('.gws-localreviews__google-review'):
        node = el.select_one('.f5axBf > span')
        if node is not None:
            tempreview = node.text.strip()
        else:
            tempreview = ''
        user.append(tempreview)


    for user_data in user:
        print(user_data)
    return user

get_reviews_data()