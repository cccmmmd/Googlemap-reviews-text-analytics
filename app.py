import sys
import configparser
import web_clinic
import json
import threading


# Azure Text Analytics
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import (
    TextAnalyticsClient,
    ExtractKeyPhrasesAction,
    AnalyzeSentimentAction
)

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
    review = {
        "positive": 0,
        "negative": 0,
        "neutral" :0
    }
    good_keywords = {}
    bad_keywords = {}
    neutral_keywords={}
    web_clinic.reset()
    finalresult = []
    finalresult1 =  []
    finalresult2 =  []
    if request.method == 'POST':
        id = request.form['url'].split('!1s')[1].split('!8m2!')[0]

    result1, result2 = web_clinic.get_20_reviews(id)
    name = web_clinic.fetch_name()

    # a = azure_sentiment(result[1], 'web')
    # a['time'] = result[1]['time']        
    # finalresult.append(a)

    def r1():
        if len(result1) > 0:
            for res in result1:
                a = azure_sentiment(res, 'web')
                a['time'] = res['time']        
                finalresult1.append(a)
    
    def r2():
        if len(result2) > 0:
            for res in result2:
                a = azure_sentiment(res, 'web')
                a['time'] = res['time']        
                finalresult2.append(a)

    r1 = threading.Thread(target=r1)
    r2 = threading.Thread(target=r2)
    
    r1.start()  
    r2.start()  

    r1.join()
    r2.join()
    finalresult = finalresult1 + finalresult2
    # print(finalresult)
  
   

    unique_time = []
    classify = []
    
    for res in finalresult:
        if res['time'] not in unique_time:
            unique_time.append(res['time'])
            new = {
                'time': res['time'],
                'good': 0,
                'bad': 0,
                'neutral': 0
                }
            if res['total'] > 0:
                new['good']+= 1
            elif res['total'] < 0:
                new['bad'] += 1
            else:
                new['neutral'] += 1
            classify.append(new)
        else:
            temp = [sub for sub in classify if sub['time'] == res['time'] ]
            
            if res['total'] > 0:
                temp[0]['good']+= 1
            elif res['total'] < 0:
                temp[0]['bad'] += 1
            else:
                temp[0]['neutral'] += 1
            
        if res['total'] > 0:
            review['positive'] += 1
            for i in res['key_phrases']:
                if i not in good_keywords:
                    good_keywords[i] = 1
                else:
                    good_keywords[i] += 1
        elif res['total'] < 0:
            review['negative'] += 1
            for i in res['key_phrases']:
                if i not in bad_keywords:
                    bad_keywords[i] = 1
                else:
                    bad_keywords[i] += 1
        else:
            review['neutral'] += 1
            for i in res['key_phrases']:
                if i not in neutral_keywords:
                    neutral_keywords[i] = 1
                else:
                    neutral_keywords[i] += 1
    
    # print(good_keywords, bad_keywords, neutral_keywords)


    classify = json.dumps(classify)
    good_keywords = json.dumps(good_keywords)
    bad_keywords = json.dumps(bad_keywords)
    neutral_keywords = json.dumps(neutral_keywords)
    # print(classify)

    # return render_template('reviews_test.html', reviews = result, name = name)

    return render_template('reviews.html', finalresult = finalresult, review = review, name = name, classify = classify, good_keywords = good_keywords, bad_keywords=bad_keywords, neutral_keywords = neutral_keywords )


@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    returnMessages = []
    sentiment_result = azure_sentiment(event.message.text, 'line')
    
    returnMessages.append(TextMessage(
                    text=f"{sentiment_result['review']}【總分：{sentiment_result['total']}】"))
    if sentiment_result['total'] > 0:
        returnMessages.append(TextMessage(text="謝謝你的肯定！我們繼續努力 \U00002764"))
    elif sentiment_result['total'] < 0:
        returnMessages.append(TextMessage(text="抱歉讓你有不愉快的觀感，我們深入了解檢討 \U0001F64F"))
    else:
        returnMessages.append(TextMessage(text="謝謝你給予評論！我們收到了！ \U0001F609"))
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=returnMessages
                # messages=[TextMessage(text=event.message.text)]
            )
        )

def azure_sentiment(user_input, type):
    text_analytics_client = TextAnalyticsClient(
        endpoint=config["AzureLanguage"]["END_POINT"], credential=credential
    )
    if type == 'line':
        string = user_input
    else:
        string = user_input['review']
    # delimiters = ["，","。"," ", "\n", ",",".","!","...","⋯","！","?","？","~","～",'|']
    # for delimiter in delimiters:
    #     string = string.replace(delimiter, ' ')
    # documents = string.split()
    #print(documents[:10])
        
    # response = text_analytics_client.analyze_sentiment(
    #     [string], show_opinion_mining=True, language="zh-hant"
    # )
        
    poller = text_analytics_client.begin_analyze_actions(
        [string],
        actions=[
            ExtractKeyPhrasesAction(),
            AnalyzeSentimentAction(),
        ],
        language="zh-Hant",
        polling_interval=1
    )
    document_results = poller.result()
   
    result_list = {}
    
    for doc, action_results in zip([string], document_results):
        sentiment = ''
        point = 0
        result_line = ""
        key_phrases = []
        for result in action_results:
            if result.kind == "KeyPhraseExtraction":
                key_phrases = result.key_phrases
            elif result.kind == "SentimentAnalysis":
                for doc in result.sentences:
                    sentiment = ''
                    if(doc.sentiment == 'positive'):
                        sentiment = '\U0001F60A , + 1'
                        point += 1
                    elif(doc.sentiment == 'negative'):
                        sentiment = '\U0001F620 , - 1'
                        point -= 1
                    else:
                        sentiment = '\U0001F636 , + 0'
                    result_line += (
                        f"{doc.text}({sentiment})\n"
                    )  
                result_list['review'] = result_line
                result_list['total'] = point
                result_list['key_phrases'] = key_phrases


    return result_list

if __name__ == "__main__":
    app.run()

