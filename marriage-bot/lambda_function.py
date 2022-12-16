import json
import os
import boto3
from boto3.session import Session

from io import BytesIO
import requests

from linebot import LineBotApi
from linebot.models import TextSendMessage

bucket_name = os.getenv('S3_BUCKET_NAME', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
table_name = os.getenv('DYNAMODB_TABLE_NAME', None)

line_bot_api = LineBotApi(channel_access_token)

# Headerの生成
HEADER = {
    'Content-type':
    'application/json',
    'Authorization':
    'Bearer ' + channel_access_token
}


def get_dynamo_table(table_name):
    session = Session(
        region_name='ap-northeast-1'
    )

    dynamodb = session.resource('dynamodb')
    dynamo_table = dynamodb.Table(table_name)
    return dynamo_table


def lambda_handler(event, context):

    body = json.loads(event['body'])
    print(body)

    # Webhookの接続確認用
    if len(body['events']) == 0:
        return {
            'statusCode': 200,
            'body': ''
        }
    # bodyからevent を取得する
    body_event = body['events'][0]
    reply_token = body_event['replyToken']
    message_type = body_event['message']['type']
    event_type = body_event['type']
    message_id = body_event['message']['id']

    # ユーザIDを取得
    user_id = body_event['source']['userId']

    if event_type == 'message':
        if message_type == 'text':
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text='テキストを受信しました。'))

        elif message_type == 'image':
            try:
                error_message = ''
                image_file = requests.get(
                    'https://api-data.line.me/v2/bot/message/' + message_id + '/content', headers=HEADER)
                image_bin = BytesIO(image_file.content)
                image = image_bin.getvalue()

                response_message = '写真を受け付けました\n幸せ戦闘力を測定しています...'
                line_bot_api.reply_message(
                    reply_token,
                    TextSendMessage(text=response_message))

                # DynamoDBに画像のIDとLINEのメッセージを保存
                item = body

                # レコード作成
                item['image_id'] = message_id
                item['user_id'] = user_id

                # レコード登録
                dynamo_table = get_dynamo_table(table_name)
                dynamo_table.put_item(Item=item)

                # 画像をS3に保存
                s3 = boto3.client('s3')
                s3.put_object(Bucket=bucket_name, Body=image,
                              Key=message_id+"_"+user_id+'.jpg')

            except Exception as e:
                error_message = str(e)
                line_bot_api.reply_message(
                    reply_token,
                    TextSendMessage(text=error_message))
                return

        elif message_type == 'sticker':
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text='スタンプを受信しました。'))

        else:
            line_bot_api.reply_message(
                reply_token,
                TextSendMessage(text='メッセージタイプ' + message_type))

    elif event_type == 'postback':
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text='タイプ:' + event_type))
