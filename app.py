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
    totalpoint = 0
    if request.method == 'POST':
        id = request.form['url'].split('!1s')[1].split('!8m2!')[0]
     # for res in result:
    #    finalresult.append(azure_sentiment(res, 'web'))


    finalresult = web_clinic.get_20_reviews(id)

    # for res in finalresult:
    #     totalpoint += res['total'] 
    return render_template('reviews_test.html', reviews = finalresult)

    # return render_template('reviews_test.html', reviews = finalresult, total = totalpoint)


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

