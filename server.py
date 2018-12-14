# -*- coding: utf-8 -*-
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from flaskext.mysql import MySQL
app = Flask(__name__)
mysql = MySQL()
api = Api(app)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'newspapers'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# app.config['MYSQL_DATABASE_CHARSET'] = 'utf8'
mysql.init_app(app)


class Title(Resource):
    def get(self):

        conn = mysql.connect()
        cursor = conn.cursor()

        # cursor.execute("SELECT title, description FROM newspapers.documents")
        query = ("SELECT doc.id, token.token "
                 "FROM newspapers.tokens AS token "
                 "INNER JOIN newspapers.documents_tokens AS doc_token "
                 "INNER JOIN newspapers.documents AS doc "
                 "WHERE token.id = doc_token.token_id "
                 "AND doc_token.document_id = doc.id "
                 "LIMIT 0, 200")
        cursor.execute(query)
#         cursor.execute("""SELECT doc.id, token.token
# FROM
#     newspapers.tokens AS token
#         INNER JOIN
#     newspapers.documents_tokens AS doc_token
#         INNER JOIN
#     newspapers.documents AS doc
# WHERE
#     token.id = doc_token.token_id
#         AND doc_token.document_id = doc.id
# """)
        articles = dict()
        data = cursor.fetchall()
        for item in data:
            if len(articles) < item[0]:
                articles[item[0]] = item[1]  # .decode("utf-8")
            else:
                articles[item[0]] = articles[item[0]] + \
                    " " + item[1]  # .decode("utf-8")
        print(articles[1])
        return articles[1]
        # return data


api.add_resource(Title, '/')  # Route_1

if __name__ == '__main__':
    app.run(port='5002')
