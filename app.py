import sys
import configparser
import web_clinic
import json

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
    web_clinic.reset()
    finalresult =  []
    if request.method == 'POST':
        id = request.form['url'].split('!1s')[1].split('!8m2!')[0]

    # result = web_clinic.get_20_reviews(id)
    name = web_clinic.fetch_name()


    # a = azure_sentiment(result[1], 'web')
    # a['time'] = result[1]['time']        
    # finalresult.append(a)

    #for res in result:
    #    a = azure_sentiment(res, 'web')
    #    a['time'] = res['time']        
    #    finalresult.append(a)
    
    finalresult = [{'review': '不懂為什麼說林醫生不好，今早看過覺得態度很友善也會寒暄，看診速度快，整體診所環境舒適，看診後藥師也會解說藥物，經驗還不錯(😊 , + 1)\n', 'total': 1, 'key_phrases': ['林醫生', '態度', '看診', '速度', '整體診所環境', '藥師', '藥物', '經驗'], 'time': '1 個月前'}, {'review': '醫生很好，但是晚班兩位櫃台態度極差，已經有預約，要我們晚點到，完五分鐘到就不給掛號，小孩發高燒人不舒服，還堅持不給掛號，千拜託萬拜託好不容易才給掛號，號碼還故意往後，好像是她們施恩典似的，態度極差對待我們，小孩從小到大都在這家看，第一次遇到這樣護士，大大影響對這家診所印象(😠 , - 1)\n', 'total': -1, 'key_phrases': ['醫生', '晚班兩位櫃台態度', '預約', '小孩', '高燒人', '號碼', '恩典', '第一次', '護士', '診所'], 'time': '1 個月前'}, {'review': '給錯看診號碼，被強迫往後延。(😠 , - 1)\n往後延一次後，又說不是我，兩度給錯看診號碼？(😠 , - 1)\n說剛剛有叫號但我沒聽到？(😠 , - 1)\n我明明就坐在室內，什麼都沒聽到，盯著號碼燈直接跳過我的號碼，然後被迫再往後延一次？(😠 , - 1)\n真的莫名其妙，想看診的人要三思，你的號碼會被莫名的被往後延。(😠 , - 1)\n', 'total': -5, 'key_phrases': ['診號碼', '看', '叫號', '室內', '號碼燈', '人'], 'time': '1 個月前'}, {'review': '昨天初次到診所看診，櫃檯人員跟醫生都非常親切也很有耐心。(😊 , + 1)\n我跟醫生說我看過很多家吃了不少藥都沒有改善。(😠 , - 1)\n隨時都乾咳都覺得喉嚨有血有異物感、痰都咳不出來、瘋狂鼻塞也鼻水倒流、睡前跟起床後都鼻水狂流、狂打噴嚏🤧 對於一個換季就會過敏的人真的很難受！(😠 , - 1)\n回家服藥後真的全部的症狀都有改善，最令人困擾的睡覺鼻塞跟乾咳竟然都消失了！！！(😠 , - 1)\n終於有一個非常好的睡覺品質！(😊 , + 1)\n真的非常感謝建佑診所的細心耐心看診，以及（真的）對症下藥！(😊 , + 1)\n很值得給予五星好評！！(😊 , + 1)\n♡♡♡蔡醫師萬歲！！(😊 , + 1)\n', 'total': 2, 'key_phrases': ['昨天', '診所', '櫃檯人員', '醫生', '耐心', '很多家', '了不少藥', '改善', '乾咳', '喉嚨', '血', '異物感', '瘋狂鼻塞', '鼻水', '起床', '噴嚏', '一個', '季', '症狀', '睡覺鼻塞', '睡覺品質', '五星好評', '蔡醫師'], 'time': '2 個月前'}, {'review': '看診專業、態度親切陳醫師跟蔡醫師都非常用心推！(😊 , + 1)\n', 'total': 1, 'key_phrases': ['態度', '陳醫師', '蔡醫師'], 'time': '2 個月前'}, {'review': '溫柔的蔡醫生拯救了我將近5天的眩暈，原本以為沒救了，真的痛苦到很想死，但是今天吃完蔡醫師的藥我就好一半了，交給專業的就對了  (😊 , + 1)\n', 'total': 1, 'key_phrases': ['蔡醫生', '眩暈', '今天', '蔡醫師'], 'time': '2 個月前'}, {'review': '沒帶口罩，口罩一個賣10元，口罩沒包裝，又不開收據，護士服務態度差！(😠 , - 1)\n', 'total': -1, 'key_phrases': ['口罩', '包裝', '收據', '護士服務態度差'], 'time': '2 個月前'}, {'review': '看診照順序走嘛過號的人卡在我老婆號碼前面卡很久我在外面等過號妳的事情關我什麼事情？(😠 , - 1)\n醫生卻好像在給我跟病人聊天一個看診至少15分起跳是把脈還是看生辰八字？(😶 , + 0)\n換我老婆時  說了一句發燒  測快篩讓她在等兩個號很瞎欸    過號的人可以卡在裡面那麼久我卻一等再等  不是不願意等麻煩有點邏輯的看診好嗎？(😠 , - 1)\n從90幾號等到1百一十多號照正常程序走  我不會怎樣但這點讓我覺得到底是看診的診所還是來聊天的喝茶地方？(😶 , + 0)\n', 'total': -2, 'key_phrases': ['人', '老婆號碼', '事情', '醫生', '15分', '生辰八字', '一句', '燒', '兩個號', '裡面', '麻煩', '邏輯', '1百一十多號照正常程序', '診所', '茶地方'], 'time': '2 個月前'}, {'review': '蔡醫師超強的！！！(😶 , + 0)\n我心中耳鼻喉科的第一名，而且在眩暈症的領域也是專精。(😶 , + 0)\n超愛問蔡醫師問題的，根本是小百科！！(😊 , + 1)\n😍😍😍(😊 , + 1)\n', 'total': 2, 'key_phrases': ['蔡醫師', '第一名', '領域', '小百科'], 'time': '2 個月前'}, {'review': '蔡醫師超專業(😊 , + 1)\n', 'total': 1, 'key_phrases': ['蔡醫師超專業'], 'time': '3 個月前'}, {'review': '一家人看病的指定診所，陳醫生超認真又熱心，蔡醫生也是，這家診所很推薦！(😊 , + 1)\n', 'total': 1, 'key_phrases': ['一家人', '指定診所', '陳醫生', '蔡醫生'], 'time': '3 個月前'}, {'review': '醫生們問診細心專業，親切又有耐心，最重要是能對症下藥，讓身體不舒服容易玻璃心的病人心情愉悅，病先好一半❤️(😊 , + 1)\n', 'total': 1, 'key_phrases': ['醫生們', '耐心', '藥', '身體', '玻璃心', '病人心情'], 'time': '3 個月前'}, {'review': '醫生問診用心，等待時間也不會太久！(😊 , + 1)\n已經在這裡看好幾年了(😶 , + 0)\n', 'total': 1, 'key_phrases': ['醫生', '時間'], 'time': '3 個月前'}, {'review': '蔡宏彥醫師人很好 有問必答 ！(😊 , + 1)\n', 'total': 1, 'key_phrases': ['蔡宏彥醫師人'], 'time': '4 個月前'}, {'review': '陳醫師本人保養超好皮膚美麗到發亮，很專業也不推銷產品，淨膚雷射後兩天就沒有很明顯痕跡，皮膚也變白變亮，超怕痛的我都覺得下次還會再嘗試！(😊 , + 1)\n推薦！(😊 , + 1)\n👍(😊 , + 1)\n', 'total': 3, 'key_phrases': ['陳醫師本人', '皮膚', '產品', '淨膚雷射', '明顯痕跡', '下次'], 'time': '5 個月前'}, {'review': '朋友介紹打淨膚雷射，蔡醫師溫柔美麗專業，術後照顧說明清楚，打完恢復良好，膚色有均勻一些，良好的經驗❤️(😊 , + 1)\n', 'total': 1, 'key_phrases': ['朋友', '淨膚雷射', '蔡醫師', '術後', '膚色', '良好', '經驗'], 'time': '5 個月前'}, {'review': '哇⋯⋯蔡醫生超慈祥的，很有耐心的安撫病患！(😊 , + 1)\n真是這附近可遇不可求的好醫生😭(😠 , - 1)\n', 'total': 0, 'key_phrases': ['蔡醫生', '耐心', '病患', '好醫生'], 'time': '8 個月前'}, {'review': '護士很愛找同事聊天，當天某護士正在專心輸入看診資料，另一護士一直干擾要聊天，打預防針也草草結束，結果出來看到又在滑手機！(😊 , + 1)\n', 'total': 1, 'key_phrases': ['護士', '同事', '診資料', '預防針', '結果', '手機'], 'time': '9 個月前'}]
    # print(finalresult)
  
    unique_time = []
    classify = []
    keywords = {}
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
        elif res['total'] < 0:
            review['negative'] += 1
        else:
            review['neutral'] += 1

        for i in res['key_phrases']:
            if i not in keywords:
                keywords[i] = 1
            else:
                keywords[i] += 1
        # keywords = {i:res['key_phrases'].count(i) for i in res['key_phrases']}
    print(keywords)


    classify = json.dumps(classify)
    # print(classify)

    # return render_template('reviews_test.html', reviews = result, name = name)

    return render_template('reviews.html', finalresult = finalresult, review = review, name = name, classify = classify)


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

