# happiness-scounter-aws

## 仕様

幸せ戦闘力はRekognition の幸せ値(S)に5500を掛け算して求める。  
幸せ値S*5500 が 50万以上の場合は新郎の写真付きで返信する。  

なお、幸せ値は1～100までのfloat 型で小数の有効桁数は3桁までとする。

## DynamoDBの設定

テーブル名：LineMessages  

パーティション名：image_id  
ソートキー：user_id  

テーブル名：RekoEmotions  
パーティションキー：object_id  
ソートキー：無し  

## Lambda の環境変数

画像の受付API

DYNAMODB_TABLE_NAME: LineMessages  
LINE_CHANNEL_ACCESS_TOKEN：チャネルアクセストークン  
S3_BUCKET_NAME：受け付けた画像の格納先  

Amazon Rekognition 用 API  
DYNAMODB_TABLE_NAME: RekoEmotions  
LINE_CHANNEL_ACCESS_TOKEN：チャネルアクセストークン  

## IAM

画像の受付API

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::{バケット名}/*"
        },
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:ap-northeast-1:XXXXXXXXXXX:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:ap-northeast-1:XXXXXXXXXXX:log-group:/aws/lambda/{関数名}:*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "dynamodb:PutItem",
            "Resource": "arn:aws:dynamodb:ap-northeast-1:XXXXXXXXXXX:table/LineMessages"
        }
    ]
}

```

Amazon Rekognition 用 API  

```json

{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "dynamodb:PutItem",
            "Resource": "arn:aws:dynamodb:ap-northeast-1:XXXXXXXXXXX:table/RekoEmotions"
        },
        {
            "Sid": "GetImagesMetadata",
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::{バケット名}/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "rekognition:DetectFaces"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": "arn:aws:logs:ap-northeast-1:XXXXXXXXXXX:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:ap-northeast-1:XXXXXXXXXXX:log-group:/aws/lambda/{関数名}:*"
            ]
        }
    ]
}

```

## 返信用FlexMessage の画像について

返信用FlexMessageに添付する画像は返信用Lambda の環境変数 `IMAGE_URL`を利用
