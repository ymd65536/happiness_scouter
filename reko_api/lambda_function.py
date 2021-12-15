import decimal
import os
import json
import boto3
import requests
from decimal import *
from boto3.session import Session
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.models import  FlexSendMessage

# 戦闘力の倍率
level = 5500
target_score = 5000 * 100.0

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
table_name = os.getenv('DYNAMODB_TABLE_NAME', None)

# FlexMessage Image
flex_ref_image = os.getenv('IMAGE_URL', None)
line_bot_api = LineBotApi(channel_access_token)

#Headerの生成
HEADER = {
    'Content-type':
    'application/json',
    'Authorization':
    'Bearer ' +channel_access_token
}

def lambda_handler(event, context):

    records = event['Records']

    # Webhookの接続確認用
    if len(records) == 0:
        return {
            'statusCode': 200,
            'body': ''
        }
    # S3からバケット名を取得
    images_bucket = records[0]['s3']['bucket']['name']
    
    # S3からオブジェクト名を取得
    image_key = str(records[0]['s3']['object']['key'])

    # ファイル名にはuser_idが付与される想定
    file_extend = image_key.split('.')
    user_id = file_extend[0].split('_')[1]

    # Rekognition を実行
    try:

        rekognition = boto3.client('rekognition')
        reko_response = rekognition.detect_faces(
            Image={
                'S3Object': {
                    'Bucket': images_bucket,
                    'Name': image_key,
                },
            },
            Attributes=['ALL']
        )
        print(reko_response)
        len_face_details = len(reko_response['FaceDetails'])

        if len_face_details == 0 :

            messages = TextSendMessage(text='顔がありません！')
            line_bot_api.push_message(
                to=user_id,
                messages=messages
            )

        else:
            face_details = reko_response['FaceDetails'][0]
            emotions = face_details['Emotions']

            # 返信用FlexMessage を作成する
            flex_message = emotion_flexmessage(emotions)
            flex_message_obj = FlexSendMessage(
                alt_text='alt_text',
                # contentsパラメタに, dict型の値を渡す
                contents=flex_message
            )
            # 送信するFlexMessage を作成
            line_bot_api.push_message(user_id,flex_message_obj)

            profile = requests.get('https://api.line.me/v2/bot/profile/{0}'.format(user_id),headers=HEADER)
            profile_json = profile.json()
            user_name = profile_json['displayName']

            # DynamoDBにRekognition の結果を保存
            emo = {}
            emo['Emotions'] = emotions_conv(emotions)
            emotion_items = emo_json(emo['Emotions'])
            
            print("DyanmoDB 登録")
            item = {}
            item = emotion_items
            item['user_name'] = user_name
            print("オブジェクトID登録")
            print(type(item))
            item['object_id'] = image_key
            print("オブジェクトID登録完了")

            # レコード登録
            dynamo_table = get_dynamo_table(table_name)
            dynamo_table.put_item(Item=item)
            # LINEにpush
            #messages = TextSendMessage(text=str(emotions))
            #line_bot_api.push_message(
            #    to=user_id,
            #    messages=messages
            #)

    except Exception as e:
        print(e)
        return

def emotion_flexmessage(emotions):
    message = """
{
  "type": "bubble",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "box",
        "layout": "vertical",
        "spacing": "sm",
        "margin": "lg",
        "contents": [
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "感情",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "割合",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "スコア",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "幸せ",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "穏やか",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "驚き",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "恐れ",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "困惑",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "嫌悪",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "怒り",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "悲しみ",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "戦闘力",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "align": "start",
                "contents": []
              },
              {
                "type": "text",
                "text": "====",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          }
        ]
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "flex": 0,
    "spacing": "sm",
    "contents": [
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "測定完了！！",
            "align": "center",
            "contents": []
          }
        ]
      }
    ]
  }
}
"""

    original_message = """
{
  "type": "bubble",
  "hero": {
    "type": "image",
    "url": "https://www.google.com/images/branding/googlelogo/1x/googlelogo_light_color_272x92dp.png",
    "size": "full",
    "aspectRatio": "20:13",
    "aspectMode": "cover",
    "action": {
      "type": "uri",
      "label": "Line",
      "uri": "https://google.com/"
    }
  },
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "box",
        "layout": "vertical",
        "spacing": "sm",
        "margin": "lg",
        "contents": [
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "感情",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "割合",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "スコア",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "幸せ",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "穏やか",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "驚き",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "恐れ",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "困惑",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "嫌悪",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "怒り",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "悲しみ",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          },
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "text": "戦闘力",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "align": "start",
                "contents": []
              },
              {
                "type": "text",
                "text": "=======>",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "align": "start",
                "contents": []
              },
              {
                "type": "text",
                "text": "0.0",
                "size": "md",
                "color": "#000000FF",
                "flex": 1,
                "contents": []
              }
            ]
          }
        ]
      }
    ]
  },
  "footer": {
    "type": "box",
    "layout": "vertical",
    "flex": 0,
    "spacing": "sm",
    "contents": [
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "新郎新婦と同じくらい幸せです！！",
            "align": "center",
            "contents": []
          }
        ]
      }
    ]
  }
}
    """

    combat_power = 0.0
    for emotion in emotions:
        emotion_type = emotion['Type']
        emotion_value = round(emotion['Confidence'],3)
        emotion_confidence = str(emotion_value)
        emotion_score = str(emotion_value*level)
        if emotion_type == 'HAPPY':
            emotion_happy = emotion_confidence
            happy_score = emotion_score
            combat_power = emotion_value * level
        elif emotion_type == 'SAD':
            emotion_sad = emotion_confidence
            sad_score = emotion_score
        elif emotion_type == 'ANGRY':
            emotion_angry = emotion_confidence
            angry_score = emotion_score
        elif emotion_type == 'SURPRISED':
            emotion_surprised = emotion_confidence
            surprised_score = emotion_score
        elif emotion_type == 'DISGUSTED':
            emotion_disgusted = emotion_confidence
            disgusted_score = emotion_score
        elif emotion_type == 'CALM':
            emotion_calm = emotion_confidence
            calm_score = emotion_score
        elif emotion_type == 'CONFUSED':
            emotion_confused = emotion_confidence
            confused_score = emotion_score
        elif emotion_type == 'FEAR':
            emotion_fear = emotion_confidence
            fear_score = emotion_score

    # 戦闘力がtarget_score 以上であれば、返信メッセージを変更する

    if combat_power >= target_score :
      print("特別なメッセージで対応")
      flex_message_json_dict = json.loads(original_message)
      flex_message_json_dict['hero']['url'] = flex_ref_image
      flex_message_json_dict['hero']['action']['uri'] = flex_ref_image
    else:
      print("通常のメッセージで対応")
      flex_message_json_dict = json.loads(message)


    combat_power = str(combat_power)
    flex_message_json_dict['body']['contents'][0]['contents'][1]['contents'][1]['text'] = emotion_happy
    flex_message_json_dict['body']['contents'][0]['contents'][2]['contents'][1]['text'] = emotion_calm
    flex_message_json_dict['body']['contents'][0]['contents'][3]['contents'][1]['text'] = emotion_surprised
    flex_message_json_dict['body']['contents'][0]['contents'][4]['contents'][1]['text'] = emotion_fear
    flex_message_json_dict['body']['contents'][0]['contents'][5]['contents'][1]['text'] = emotion_confused
    flex_message_json_dict['body']['contents'][0]['contents'][6]['contents'][1]['text'] = emotion_disgusted
    flex_message_json_dict['body']['contents'][0]['contents'][7]['contents'][1]['text'] = emotion_angry
    flex_message_json_dict['body']['contents'][0]['contents'][8]['contents'][1]['text'] = emotion_sad

    flex_message_json_dict['body']['contents'][0]['contents'][1]['contents'][2]['text'] = happy_score
    flex_message_json_dict['body']['contents'][0]['contents'][2]['contents'][2]['text'] = calm_score
    flex_message_json_dict['body']['contents'][0]['contents'][3]['contents'][2]['text'] = surprised_score
    flex_message_json_dict['body']['contents'][0]['contents'][4]['contents'][2]['text'] = fear_score
    flex_message_json_dict['body']['contents'][0]['contents'][5]['contents'][2]['text'] = confused_score
    flex_message_json_dict['body']['contents'][0]['contents'][6]['contents'][2]['text'] = disgusted_score
    flex_message_json_dict['body']['contents'][0]['contents'][7]['contents'][2]['text'] = angry_score
    flex_message_json_dict['body']['contents'][0]['contents'][8]['contents'][2]['text'] = sad_score
    flex_message_json_dict['body']['contents'][0]['contents'][9]['contents'][2]['text'] = combat_power

    return flex_message_json_dict

def get_dynamo_table(table_name):
    session = Session(
            region_name='ap-northeast-1'
    )
 
    dynamodb = session.resource('dynamodb')
    dynamo_table = dynamodb.Table(table_name)
    return dynamo_table

# DyanmoDBはfloat 型に対応していない
# decimal に変換する必要があるが、データはそのまま残しておきたい
def emotions_conv(emotions):
    len_emotions = len(emotions)
    for cnt_i in range(len_emotions):
        emotions[cnt_i]['Confidence'] =  decimal.Decimal(str(round(emotions[cnt_i]['Confidence'],3)))
    return emotions

def emo_json(emotions):
  emotion_items = {}

  for emotion in emotions:
    emotion_value = round(emotion['Confidence'],3)
    emotion_score = str(emotion_value*level)
    emotion_items[emotion['Type']] = emotion_score
  
  return emotion_items

            