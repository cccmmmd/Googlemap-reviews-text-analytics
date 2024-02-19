import sys
import configparser
import web_clinic

# Azure Text Analytics
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient

from flask import Flask, request, abort, render_template
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)

#Config Parser
config = configparser.ConfigParser()
config.read('config.ini')

# Azure Text Analytics
credential = AzureKeyCredential(config["AzureLanguage"]["API_KEY"])


app = Flask(__name__)

channel_access_token = config['Line']['CHANNEL_ACCESS_TOKEN']
channel_secret = config['Line']['CHANNEL_SECRET']
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

handler = WebhookHandler(channel_secret)

configuration = Configuration(
    access_token=channel_access_token
)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/submit", methods=['POST'])
def submit():
    positive = 0
    negative = 0
    neutral = 0
    finalresult =  []
    if request.method == 'POST':
        id = request.form['url'].split('!1s')[1].split('!8m2!')[0]
    print(id)
   
    web_clinic.reset()

    result = web_clinic.get_20_reviews(id)
    for res in result:
        finalresult.append(azure_sentiment(res, 'web'))
    # finalresult = [{'review': '莊醫師看診細心也很有耐心(😊 + 1)\n一般醫生只會開抗生素和藥膏給我但是莊醫師有幫我把膿血擠出(😊 + 1)\n', 'total': 2}, 
    #           {'review': '每一次來看黃醫生都覺得黃醫生真的很有醫術很溫暖(😊 + 1)\n只是看個普通的痘痘也會很感同身受(😶 + 0)\n雖然會等很久(😶 + 0)\n但我仍然還是會願意等待😊謝謝黃醫生(😊 + 1)\n', 'total': 2}, 
    #           {'review': '以前都去看黃禎憲醫師(😶 + 0)\n這次沒掛到號(😶 + 0)\n改來這邊(😶 + 0)\n推薦廖醫師很專業👍(😊 + 1)\n看診的人也很多(😶 + 0)\n', 'total': 1}, 
    #           {'review': '藥劑師態度有夠差(😠 - 1)\n不了解才詢問(😶 + 0)\n了解就不會問了又不是自討苦吃(😠 - 1)\n莫名奇妙(😊 + 1)\n', 'total': -1}, 
    #           {'review': '來兩次都覺得護士好像才是醫生醫生說沒兩句就講話請問妳是醫生嗎病人要聽誰說話呢☺️(😊 + 1)\n', 'total': 1}, 
    #           {'review': '診所內的廁所竟然連洗手的清潔劑都不提供(😶 + 0)\n過了一年還是不提供(😶 + 0)\n😂🤣😂🤣(😊 + 1)\n', 'total': 1}, 
    #           {'review': '推薦顏醫師看了幾次痘痘(😊 + 1)\n吃了兩個月A酸也依治療計畫做過幾次果酸跟染料雷射(😶 + 0)\n痘痘跟痘疤都改善很多顏醫師也都很有耐心提供保養方法跟注意事項(😊 + 1)\n有些真是受益良多也因此多注意了使用的保養品跟飲食(😊 + 1)\n痘痘真的就比較不會一直冒(😶 + 0)\n顏醫師推推(😶 + 0)\n推薦顏醫師看了幾次痘痘(😊 + 1)\n吃了兩個月A酸也依治療計畫做過幾次果酸跟染料雷射(😶 + 0)\n痘痘跟痘疤都改善很多顏醫師也都很有耐心提供保養方法跟注意事項(😊 + 1)\n有些真是受益良多(😊 + 1)\n', 'total': 6}, 
    #           {'review': '建議可以先預約掛號(😶 + 0)\n環境乾淨整潔、醫師有耐心解決問題👍🏻(😊 + 1)\n', 'total': 1}, 
    #           {'review': '護士人很好(😊 + 1)\n', 'total': 1}, {'review': '每個醫生都很有耐心(😶 + 0)\n護士也不錯(😊 + 1)\n', 'total': 1}, 
    #           {'review': '醫生人很好(😊 + 1)\n會詳細解釋原因和注意事項(😶 + 0)\n不需要的治療也不會要你做(😶 + 0)\n另外記得戴口罩去（現場買一個5元）(😶 + 0)\n不要為難櫃檯美麗的姐姐(😊 + 1)\n', 'total': 2}, 
    #           {'review': '再這邊看醫生至少好幾年了(😶 + 0)\n第一次遇到那麼不愉快的經驗(😠 - 1)\n我真心建議不推薦莊醫生(😠 - 1)\n', 'total': -2}, 
    #           {'review': '平常來看診的人都很多(😶 + 0)\n可以線上預約(😶 + 0)\n平日早上不用等太久(😶 + 0)\n第一次看診是莊博閎醫生看的(😶 + 0)\n在講解他的看法與用藥都很仔細、有耐心(😊 + 1)\n', 'total': 1}]
    for res in finalresult:
        if res['total'] > 0:
            positive += 1
        elif res['total'] < 0:
            negative += 1
        else:
            neutral += 1
    # return render_template('reviews_test.html', reviews = finalresult)

    return render_template('reviews.html', reviews = finalresult, positive = positive, negative = negative, neutral = neutral)


@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    
    sentiment_result = azure_sentiment(event.message.text, 'line')
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f"{sentiment_result['review']}【總分：{sentiment_result['total']}】")],
                # messages=[TextMessage(text=event.message.text)]
            )
        )

def azure_sentiment(user_input, type):
    text_analytics_client = TextAnalyticsClient(
        endpoint=config["AzureLanguage"]["END_POINT"], credential=credential
    )
    delimiters = ["，","。"," ", "\n", ",",".","!","...","⋯","！","?","？","~","～",'|']
    if type == 'line':
        string = user_input
    else:
        string = user_input['review']
    for delimiter in delimiters:
        string = string.replace(delimiter, ' ')
 
    documents = string.split()
    #print(documents[:10])
    
    response = text_analytics_client.analyze_sentiment(
        documents[:10], show_opinion_mining=True, language="zh-hant"
    )
    # print(response)


    docs = [doc for doc in response if not doc.is_error]
    point = 0
    result = ""
    result_list = {}
    for idx, doc in enumerate(docs):
        sentiment = ''
        if(docs[idx].sentiment == 'positive'):
            sentiment = '\U0001F60A , + 1'
            point += 1
        elif(docs[idx].sentiment == 'negative'):
            sentiment = '\U0001F620 , - 1'
            point -= 1
        else:
            sentiment = '\U0001F636 , + 0'
        result += (
            f"{docs[idx].sentences[0].text}({sentiment})\n"
        )  
    result_list['review'] = result
    result_list['total'] = point
    # result += '總分：'+str(point)

    return result_list

if __name__ == "__main__":
    app.run()

