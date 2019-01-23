# -*- coding: utf-8 -*-
from flask import Flask, request, Response
from flask_restful import Resource
from flask_cors import CORS
from flaskext.mysql import MySQL
import requests
import json
import collections

# initialize the app
app = Flask(__name__)
mysql = MySQL()

# initialize database constants
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'newspapers'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# use cors for local execution
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
mysql.init_app(app)

topic_aliases = {
    "SPD": "SPD",
    "CDU": "CDU",
    "AfD": "Alternative für Deutschland"
}

# route for sentiment data retrieval including database and precire


@app.route("/Sentiment/<topic>", methods=["GET"])
def sentiment(topic):
    # get articles and save them to their json file
    print("getting articles")
    getArticles(topic)
    return "done"


# route for the frontend to get data about their topic
@app.route("/<topic>", methods=["GET"])
def index(topic):
    # retrieve the data and return it as a json
    file_name = topic + ".json"
    response = app.response_class(
        response=json.dumps(getDataFromJson(file_name)),
        status=200,
        mimetype='application/json'
    )
    return response


def getDataFromJson(file_name):
    # return the data from the appropriate json file
    with open(file_name, encoding='utf-8') as data_file:
        data = json.load(data_file)
        print(data)
        return data


def getArticles(topic):
    # connect the database cursor
    conn = mysql.connect()
    cursor = conn.cursor()
    file_name = topic + ".json"
    topic_alias = topic_aliases.get(topic)

    keyword_query = ("SELECT "
                     "doc.id, "
                     "GROUP_CONCAT(keyword.keyword "
                     "SEPARATOR ', ') AS concat_keyword, "
                     "doc.title "
                     "FROM "
                     "newspapers.documents_keywords AS doc_keyword "
                     "INNER JOIN "
                     "newspapers.keywords AS keyword "
                     "INNER JOIN "
                     "newspapers.documents AS doc "
                     "WHERE "
                     "keyword.id = doc_keyword.keyword_id "
                     "AND doc_keyword.document_id = doc.id "
                     "AND date NOT LIKE '-' "
                     "AND newsportal NOT LIKE '%Guardian%' "
                     "AND newsportal NOT LIKE '%New York Times%' "
                     "AND newsportal NOT LIKE '%Donaukurier%' "
                     "AND newsportal NOT LIKE '%Russia Today%' "
                     "AND url NOT LIKE '%bild-international/%' "
                     "AND ((description like '%" + topic +
                     "%') OR (description like '%" + topic_alias + "%')) "
                     "GROUP BY doc_keyword.document_id "
                     "ORDER BY doc.id "
                     "LIMIT 0 , 1000000")

    query = ("SELECT doc.id, token.token, doc.author, doc.newsportal, doc.title, doc.date "
             "FROM newspapers.tokens AS token "
             "INNER JOIN newspapers.documents_tokens AS doc_token "
             "INNER JOIN newspapers.documents AS doc "
             "WHERE token.id = doc_token.token_id "
             "AND doc_token.document_id = doc.id "
             "AND date not like '-' "
             "AND newsportal not like '%Guardian%' "
             "AND newsportal not like '%New York Times%' "
             "AND newsportal not like '%Donaukurier%' "
             "AND newsportal not like '%Russia Today%' "
             "AND url not like '%bild-international/%' "
             "AND (( description like '%" + topic +
             "%') OR (description like '%" + topic_alias + "%')) "
             "LIMIT 0, 10000000")
    # fetch the article text data
    cursor.execute(query)
    articles = dict()
    data = cursor.fetchall()

    # now fetch the keyword data
    cursor.close()
    cursor = conn.cursor()
    cursor.execute(keyword_query)
    keyword_data = cursor.fetchall()
    print(keyword_data)
    # get the document ids for all the articles with the topic in the keywords
    keyword_document_ids = []
    for keyword_item in keyword_data:
        current_id = keyword_item[0]
        current_keywords = keyword_item[1]
        if (topic in current_keywords):
            keyword_document_ids.append(current_id)
    print(keyword_document_ids)

    for item in data:
        current_id = item[0]
        # first check if the current id is in the keyword_document_ids
        if (current_id in keyword_document_ids):
            print("-------------")
            print("current_id: " + str(current_id))
            print("current_id is in keyword_document_ids")
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
    # create the proper file and dump an empty array into it
    with open(file_name, mode='w', encoding='utf-8') as feedsjson:
        json.dump([], feedsjson, sort_keys=True, indent=4,
                  ensure_ascii=False)
    # now fill the file with our data
    for current_id, values in articles.items():
        getSentiment(document_id=current_id, news_text=values[0], author=values[1],
                     newsportal=values[2], title=values[3], date=values[4], file_name=file_name)


# returns and saves the sentiment in the proper file
def getSentiment(document_id, news_text, author, newsportal, title, date, file_name):
    # request for precire
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
    # parse the response
    response["id"] = document_id
    response["author"] = author
    response["newsportal"] = newsportal
    response["title"] = title
    response["date"] = date

    print(response)

    # now get the existing data, make it a dictionary
    with open(file_name, encoding='utf-8') as existing_data:
        feeds = json.load(existing_data)

    # finally, append the dictionary and write to the file again
    with open(file_name, mode='w', encoding='utf-8') as feedsjson:
        feeds.append(response)
        json.dump(feeds, feedsjson, sort_keys=True, indent=4,
                  ensure_ascii=False)


# run the server on port 5002
if __name__ == '__main__':
    app.run(port='5002')
