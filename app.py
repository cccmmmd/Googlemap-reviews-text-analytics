import sys
import configparser
import web_clinic

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
    finalresult =  []
    if request.method == 'POST':
        id = request.form['url'].split('!1s')[1].split('!8m2!')[0]
    # print(id)
   
    web_clinic.reset()

    result = web_clinic.get_20_reviews(id)
    name = web_clinic.fetch_name()

    # azure_sentiment(result[14], 'web')

    for res in result:
        finalresult.append(azure_sentiment(res, 'web'))
    print(finalresult)
    

    # for res in result:

    for res in finalresult:
        if res['total'] > 0:
            review['positive'] += 1
        elif res['total'] < 0:
            review['negative'] += 1
        else:
            review['neutral'] += 1
    
    # return render_template('reviews_test.html', reviews = result, name = name)

    return render_template('reviews.html', finalresult = finalresult, review = review, name = name)


@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    returnMessages = []
    sentiment_result = azure_sentiment(event.message.text, 'line')
    
    returnMessages.append(TextMessage(
                    text=f"{sentiment_result['review']}【總分：{sentiment_result['total']}】"))
    if sentiment_result['total'] > 0:
        returnMessages.append(TextMessage(text="是開心評論喔！\U00002764"))
    elif sentiment_result['total'] < 0:
        returnMessages.append(TextMessage(text="是不爽的評論喔！ \U0001F525"))
    else:
        returnMessages.append(TextMessage(text="是中立的評論！ \U0001F375"))
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

