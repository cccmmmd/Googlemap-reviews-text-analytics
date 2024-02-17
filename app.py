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
    finalresult = []
    result = web_clinic.get_20_reviews()
    #for res in result:
    #    finalresult.append(azure_sentiment(res))
    
    return render_template('reviews.html', reviews = result)
    #return render_template('reviews.html', reviews = finalresult)

@app.route("/reviews", methods=['POST'])
def reviews():
    result = web_clinic.get_20_reviews()
    return render_template('reviews.html', reviews = result)


@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    
    sentiment_result = azure_sentiment(event.message.text)
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=sentiment_result)],
                # messages=[TextMessage(text=event.message.text)]
            )
        )

def azure_sentiment(user_input):
    text_analytics_client = TextAnalyticsClient(
        endpoint=config["AzureLanguage"]["END_POINT"], credential=credential
    )
    delimiters = ["，","。"," ", "\n", ",",".","!","...","⋯","！","?","？","~","～",'|']
    string = user_input
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
    for idx, doc in enumerate(docs):
        sentiment = ''
        if(docs[idx].sentiment == 'positive'):
            sentiment = '\U0001F60A \U00002796 \U000020E3'
            point += 1
        elif(docs[idx].sentiment == 'negative'):
            sentiment = '\U0001F620 \U00002795 \U000020E3'
            point -= 1
        else:
            sentiment = '\U0001F636'
        result += (
            f"{docs[idx].sentences[0].text}({sentiment})\n"
        )   
    result += '總分：'+str(point)

    return result

if __name__ == "__main__":
    app.run()

