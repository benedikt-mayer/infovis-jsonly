# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from flaskext.mysql import MySQL
import requests
import json
app = Flask(__name__)
mysql = MySQL()
api = Api(app)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'newspapers'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
mysql.init_app(app)


class Title(Resource):
    def get(self):
        # return getArticles()
        return getDataFromJson()


api.add_resource(Title, '/')  # Route_1


def getDataFromJson():
    with open('data.json') as data_file:
        data = json.load(data_file)["results"]

        for key in data.keys():
            data[key] = data[key]["percentile"] / 100.0

        data["Name"] = "Bernd Baumann"
        data["Zeitung"] = "Süddeutsche Zeitung"
        print(data)
        return data


def getArticles():
    conn = mysql.connect()
    cursor = conn.cursor()

    query = ("SELECT doc.id, token.token "
             "FROM newspapers.tokens AS token "
             "INNER JOIN newspapers.documents_tokens AS doc_token "
             "INNER JOIN newspapers.documents AS doc "
             "WHERE token.id = doc_token.token_id "
             "AND doc_token.document_id = doc.id "
             "AND date not like '-' "
             "LIMIT 0, 10000")
    cursor.execute(query)
    articles = dict()
    data = cursor.fetchall()
    for item in data:
        if not (item[0] in articles):
            articles[item[0]] = item[1]
        else:
            articles[item[0]] = articles[item[0]] + " " + item[1]
    print(articles)
    print("size: " + str(len(articles)))
    return articles[1]


def getSentiment(news_text):
    request_body = {
        'document': {
            'text': news_text,
            'type': 'default'
        },
        'results': [
            {'name': 'reliable', 'patterns': False},
            {'name': 'motivating', 'patterns': False},
            {'name': 'optimistic', 'patterns': False},
            {'name': 'positive', 'patterns': False},
            {'name': 'composed', 'patterns': False},
            {'name': 'goal_oriented', 'patterns': False},
            {'name': 'supportive', 'patterns': False},
            {'name': 'self_confident', 'patterns': False},
            {'name': 'visionary', 'patterns': False},
            {'name': 'aggressive', 'patterns': False}
        ],
        'patterns': False,
    }
    headers = {'Content-Language': 'en',
               'Content-Type': 'application/json',
               'Ocp-Apim-Subscription-Key': '36cf4fce3cc54086a69039e3421eac77'}
    url = 'https://api.precire.ai/v0.11'
    payload = json.dumps(request_body)
    jsonData = requests.post(url, data=payload, headers=headers).json()
    # jsonData = requests.get(
    #     "https://jsonplaceholder.typicode.com/todos/1").json()
    with open('data.json', 'w') as outfile:
        json.dump(jsonData, outfile, sort_keys=True, indent=4,
                  ensure_ascii=False)
    print(jsonData)


if __name__ == '__main__':
    # getSentiment("Why does the federal government enable one"
    #              "of the closest friends of Vladimir Putin to stay and work permanently in Germany ? The man hates homosexuals and Nato, and finances "
    #              "anti-Western research in Europe . BILD has learned that Russian businessman Vladimir Yakunin has recently received a D-visa for taking "
    #              "up work in Germany . German state news channel “Deutsche Welle” reported on this earlier . A spokesperson of Yakunin’s think tank "
    #              "“Dialogue for Civilizations” (DOC) confirmed to BILD: “Mr . Vladimir Yakunin has received a visa that is valid for six months . It is a "
    #              "temporary work visa of type D.” Yakunin, she said, is the DOC chairman and “therefore spends a lot of time in Berlin” . The spokesperson "
    #              "added: “For this reason, he would like to have a visa for Germany, and there is nothing more behind it.” The visa issuance allegedly has "
    #              "“no influence at all on the work of the institute” . However, BILD has learned that Yakunin might stay in Germany for much longer . "
    #              "Because, as a rule, a D-visa is followed by a residence permit, a so-called “Blue Card” . The latter can also be extended"
    #              "regularly . Georgian President Giorgi Margvelashvili gives his account on the situation in his country, exactly 10 years after the "
    #              "Russian invasion Syria /'s White Helmets head Raed Saleh talked to BILD about the scenarios for Idlib and propaganda attacks against his "
    #              "organization The visa issuance for Yakunin is controversial because the Russian has been on two sanctions lists since 2014 that concern "
    #              "his freedom of travel, assets, and legal capacity – in the")
    app.run(port='5002')
