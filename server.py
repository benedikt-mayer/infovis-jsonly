# -*- coding: utf-8 -*-
from flask import Flask, request, Response
from flask_restful import Resource
from flask_cors import CORS
from flaskext.mysql import MySQL
import requests
import json
import collections
app = Flask(__name__)
mysql = MySQL()
# api = Api(app)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'newspapers'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
mysql.init_app(app)

# MAASSEN_FILE = "maassen.json"
# SPD_FILE = "SPD.json"
# KEYWORD = "SPD"
# FILE_NAME = SPD_FILE


# class DoSentimentAnalysis(Resource):
@app.route("/Sentiment/<topic>", methods=["GET"])
def sentiment(topic):
    print("getting articles")
    getArticles(topic)
    return "done"


# class Title(Resource):
@app.route("/<topic>", methods=["GET"])
def index(topic):
    # return getArticles()
    file_name = topic + ".json"
    response = app.response_class(
        response=json.dumps(getDataFromJson(file_name)),
        status=200,
        mimetype='application/json'
    )
    return response


# api.add_resource(DoSentimentAnalysis, '/Sentiment')  # Route_2
# api.add_resource(Title, '/<article>')  # Route_1


def getDataFromJson(file_name):
    with open(file_name, encoding='utf-8') as data_file:
        data = json.load(data_file)

        # print(data.keys())

        # result = collections.defaultdict(dict)

        # for index in data.keys():
        #     for key in data[index]["results"].keys():
        #         value = data[index]["results"][key]["percentile"] / 100.0
        #         result[int(index)][key] = value

        # result.update(int(index): key)
        # result.update([int(index)][key]: value)

        # result[int(index)]["Name"] = "Bernd Baumann"
        # result[int(index)]["Zeitung"] = "Süddeutsche Zeitung"
        print(data)
        return data


def getArticles(topic):
    conn = mysql.connect()
    cursor = conn.cursor()
    file_name = topic + ".json"

    query = ("SELECT doc.id, token.token, doc.author, doc.newsportal, doc.title, doc.date "
             "FROM newspapers.tokens AS token "
             "INNER JOIN newspapers.documents_tokens AS doc_token "
             "INNER JOIN newspapers.documents AS doc "
             "WHERE token.id = doc_token.token_id "
             "AND doc_token.document_id = doc.id "
             "AND date not like '-' "
             "AND newsportal not like '%Guardian%'"
             "AND newsportal not like '%New York Times%'"
             "AND url not like '%bild-international/%'"
             "AND description like '%" + topic + "%'"
             "LIMIT 0, 1000000")
    # item[1] = "wer"  # item 5
    # item[0] = "20"  # item 5
    # item[0] = "20"  # item 6
    # item[1] = "geigt"  # item 6
    # articles["20"] = ("wer zuerst geigt", "petersen", "bild")
    # articles["20"] = "wer zuerst geigt"
    # ("20", "wer zuerst geigt", "petersen")
    cursor.execute(query)
    articles = dict()
    data = cursor.fetchall()
    for item in data:
        current_id = item[0]
        next_word = item[1]
        if not (current_id in articles):
            articles[current_id] = (
                # item[2-5] are the remaining properties like title, author, etc.
                next_word, item[2], item[3], item[4], item[5])
        else:
            """ update the tuple of article with id current_id
                to do this, get the existing text of the tuple 
                (at articles[current_id][0]), add the next_word to it
                 and then concatenate it with the rest of the 
                 tuple (articles[current_id][1:])
            """
            articles[current_id] = ((
                articles[current_id][0] + " " + next_word),) + articles[current_id][1:]
    print(articles)
    with open(file_name, mode='w', encoding='utf-8') as feedsjson:
        json.dump([], feedsjson, sort_keys=True, indent=4,
                  ensure_ascii=False)
    for current_id, values in articles.items():
        getSentiment(document_id=current_id, news_text=values[0], author=values[1],
                     newsportal=values[2], title=values[3], date=values[4], file_name=file_name)
    # print("size: " + str(len(articles)))
    # return articles[1]


def getSentiment(document_id, news_text, author, newsportal, title, date, file_name):
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
    headers = {'Content-Language': 'de',
               'Content-Type': 'application/json',
               'Ocp-Apim-Subscription-Key': '2cee3729b9554442be89d57521ae6950'}
    url = 'https://api.precire.ai/v0.11'
    payload = json.dumps(request_body)
    response = requests.post(url, data=payload, headers=headers).json()
    response["id"] = document_id
    response["author"] = author
    response["newsportal"] = newsportal
    response["title"] = title
    response["date"] = date

    print(response)

    with open(file_name, encoding='utf-8') as existing_data:
        feeds = json.load(existing_data)

    with open(file_name, mode='w', encoding='utf-8') as feedsjson:
        feeds.append(response)
        json.dump(feeds, feedsjson, sort_keys=True, indent=4,
                  ensure_ascii=False)


if __name__ == '__main__':
    # getArticles()
    app.run(port='5002')
