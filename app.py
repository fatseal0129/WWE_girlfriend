from ibm_watson import AssistantV2, NaturalLanguageUnderstandingV1, ApiException, LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, ClassificationsOptions, EntitiesOptions, SentimentOptions, KeywordsOptions, RelationsOptions,SemanticRolesOptions,ConceptsOptions,EmotionOptions
import json
import requests
import random
from flask import Flask, redirect, request, render_template, jsonify

app = Flask(__name__)

#for watson
authenticator_watson = IAMAuthenticator('QCLxh6rThZNpXNMnL3fHUX_dtruelzQw64edrS0ul57r')
assistant = AssistantV2(
    version='2021-11-27',
    authenticator=authenticator_watson
)
assistant.set_service_url('https://api.us-south.assistant.watson.cloud.ibm.com/instances/021d4c98-d8ee-4bb9-a118-bb27c74ad3aa')

#for NLU的Authenticator
authenticator_NLU = IAMAuthenticator('a08zu4Rj1LwgTr6QIux_M5pz3fMCvhyQCuSUkiZvBvLr')
natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2022-04-07',
    authenticator=authenticator_NLU
)
natural_language_understanding.set_service_url('https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/c80740d9-2c7e-4549-8384-fd77bfabc985')
        
#for translate
authenticator_translate = IAMAuthenticator('7dy5K0vohQLnWcNEE32TWTD_zmJ_M1jbB25THtKqy3Lx')
language_translator = LanguageTranslatorV3(
    version='2018-05-01',
    authenticator=authenticator_translate
)        

language_translator.set_service_url('https://api.au-syd.language-translator.watson.cloud.ibm.com/instances/2a3b0652-010d-4379-aafa-c48c02eb63c1')

session = dict()
All_Food = ['牛肉麵','拉麵','泡麵','烏龍麵','涼麵','意麵','義大利麵','蕃茄麵','鍋燒意麵','炒麵','丼飯'
            ,'控肉飯','海南雞飯','肉燥飯','飯包','飯糰','滷肉飯','咖哩飯','炒飯','魯肉飯','燒肉飯','雞肉飯','兩餐'
            ,'韓式料理','關東煮','鐵板燒','肯德基','21世紀風味館','漢堡王','麥當勞','炸雞','subway','摩斯漢堡','牛排','燒烤',
            '烤肉','火鍋','涮涮鍋','鴛鴦鍋','麻辣鍋','壽喜燒','鼎泰豐','湯包','早安城之美','麥味登','早午餐','美而美',
            '拿波里','達美樂','pizza','必勝客','後餐鹹酥雞','後餐臭豆腐','後餐','章魚燒','豬血糕','臭豆腐','宵夜','京都',
            '日式定食','三餐自助餐','甘味廚房','一品快餐','丼飯屋','一餐自助餐','高麗元','教餐','雞同鴨講','藝素佳','八方雲集',
            '突厥','南機場夜市','士林夜市','公館夜市','師大夜市','景美夜市','楠雅夜市','寧夏夜市','樂華夜市','饒河夜市',
            '壽司','迴轉壽司','健康餐','7-11','便利商店','萊爾富','全家','ok mart']

wantfood = ['1']

def CreateSession():
    session = assistant.create_session(
    assistant_id='67ec82fc-1dcc-4821-8034-103862368d56'
        ).get_result()
    return session


@app.route('/')
def welcome():
    del wantfood[0]
    session = CreateSession()
    wantfood.append(random.choice(All_Food))
    print("Now she wants is : " + wantfood[0])
    response = assistant.message(
        assistant_id='67ec82fc-1dcc-4821-8034-103862368d56',
        session_id = session.get('session_id'),
    input={
        'message_type': 'text',
        'text': "start",
        'options': {
            'return_context': True
            }
        }
        ).get_result()
    result = response.get('output').get('generic')
    return render_template('index.html', response = result[0].get('text'))


@app.route('/qwer', methods = ['POST'])
def responsela():
    #使用者輸入
    input = request.form['res']
    session = CreateSession()
    print(input)
    response = assistant.message(
        assistant_id='67ec82fc-1dcc-4821-8034-103862368d56',
        session_id = session.get('session_id'),
    input={
        'message_type': 'text',
        'text': "start",
        'options': {
            'return_context': True
            }
        }
        ).get_result()
    isFood = False
    #若有輸入吃的東西
    for i in All_Food:
        if(i in input):
            print("now you have come")
            isFood = True
            break
    if(not isFood):   
        #翻譯成英文好分析tone
        translation = language_translator.translate(
        text=input,
        model_id='zh-TW-en').get_result()
        t_temp = translation.get('translations')
        #翻譯好的文字
        well_trans = t_temp[0].get('translation')
        #分析tone
        try:
            response_class = natural_language_understanding.analyze(
            text=well_trans,
            features=Features(classifications=ClassificationsOptions(model='tone-classifications-en-v1'))).get_result()
            tone_temp = response_class.get('classifications')
            #將分析好的tone 放入tone變數
            b_tone = tone_temp[0].get('class_name')
            a_tone = b_tone
            if(b_tone != "impolite" and b_tone != "polite"):
                a_tone = "impolite"
            response = assistant.message(
            assistant_id='67ec82fc-1dcc-4821-8034-103862368d56',
            session_id = session.get('session_id'),
            input={
                'message_type': 'text',
                'text': a_tone +" "+input,
                'options': {
                    'return_context': True
                    }
                }
                ).get_result()
            result = response.get('output').get('generic')
            print("The tone is : "+ a_tone +" "+input)
            if(result[0].get('text') == "感覺還行 那走吧"):
                return "恭喜你找到了她/他想吃什麼"
            elif(result[0].get('text') == "都不要吃啊！" or result[0].get('text') == "我不想跟你講話了"or result[0].get('text') == "算了 我自己想" or result[0].get('text') == "不理你了"):
                #這邊要結束遊戲
                return "gameover"
            elif(result[0].get('text') == "都行 但我要自己去吃"):
                return "gameover"
            return result[0].get('text')
        except:
            response = assistant.message(
            assistant_id='67ec82fc-1dcc-4821-8034-103862368d56',
            session_id = session.get('session_id'),
            input={
                'message_type': 'text',
                'text': "polite" +" "+input,
                'options': {
                    'return_context': True
                    }
                }
                ).get_result()
            result = response.get('output').get('generic')
            print("Exception tone is polite"+" "+input)
            if(result[0].get('text') == "感覺還行 那走吧"):
                return "恭喜你找到了她/他想吃什麼！"
            elif(result[0].get('text') == "都不要吃啊！" or result[0].get('text') == "我不想跟你講話了"or result[0].get('text') == "算了 我自己想" or result[0].get('text') == "不理你了"):
                #這邊要結束遊戲
                return "gameover"
            elif(result[0].get('text') == "都行 但我要自己去吃"):
                return "gameover"
            return result[0].get('text')
    else:
        if(wantfood[0] in input):
            response = assistant.message(
            assistant_id='67ec82fc-1dcc-4821-8034-103862368d56',
            session_id = session.get('session_id'),
            input={
            'message_type': 'text',
            'text': "answer "+input,
            'options': {
                'return_context': True
                }
            }
            ).get_result()
            print("Right now the res is : answer")
            result = response.get('output').get('generic')
            if(result[0].get('text') == "感覺還行 那走吧"):
                return "恭喜你找到了她/他想吃什麼"
            elif(result[0].get('text') == "都不要吃啊！" or result[0].get('text') == "我不想跟你講話了"or result[0].get('text') == "算了 我自己想" or result[0].get('text') == "不理你了"):
            #這邊要結束遊戲
                return "gameover"
            elif(result[0].get('text') == "都行 但我要自己去吃"):
                return "gameover"
            return result[0].get('text')
        else:
            response = assistant.message(
            assistant_id='67ec82fc-1dcc-4821-8034-103862368d56',
            session_id = session.get('session_id'),
            input={
            'message_type': 'text',
            'text': "not_answer "+input,
            'options': {
                'return_context': True
                }
            }
            ).get_result()
            print("right now is not the ansswer")
            result = response.get('output').get('generic')
            if(result[0].get('text') == "感覺還行 那走吧"):
                return "恭喜你找到了她/他想吃什麼!"
            elif(result[0].get('text') == "都不要吃啊！" or result[0].get('text') == "我不想跟你講話了"or result[0].get('text') == "算了 我自己想" or result[0].get('text') == "不理你了"):
            #這邊要結束遊戲
                return "你沒了"
            elif(result[0].get('text') == "都行 但我要自己去吃"):
                return "你沒了"
            return result[0].get('text')

if __name__ == "__main__":
    app.run()
