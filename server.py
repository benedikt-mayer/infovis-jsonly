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

        conn = mysql.connect()
        cursor = conn.cursor()

        query = ("SELECT doc.id, token.token "
                 "FROM newspapers.tokens AS token "
                 "INNER JOIN newspapers.documents_tokens AS doc_token "
                 "INNER JOIN newspapers.documents AS doc "
                 "WHERE token.id = doc_token.token_id "
                 "AND doc_token.document_id = doc.id "
				 "AND date not like '-'"
                 "LIMIT 0, 200")
        cursor.execute(query)
        articles = dict()
        data = cursor.fetchall()
        for item in data:
            if len(articles) < item[0]:
                articles[item[0]] = item[1]
            else:
                articles[item[0]] = articles[item[0]] + \
                    " " + item[1]
        print(articles[1])
        return articles[1]



		

api.add_resource(Title, '/')  # Route_1


def getSentiment(news_text):
    request_body = {
        'document': {
            'text': news_text,
            'type': 'default'
		},
        'results': [{'name':'friendly', 'patterns': False},
            {'name':'aggressive', 'patterns': False}],
        'patterns': False
	}
    url = 'https://api.precire.ai/v0.11'
    payload = json.dumps(request_body)
    response = requests.post(url,payload)
    #r = requests.get("https://jsonplaceholder.typicode.com/todos/1")
    print(response.content)

def addSentimentToFile():
    return json

if __name__ == '__main__':
    getSentiment("Ich hasse alle Leute")
    app.run(port='5002')
