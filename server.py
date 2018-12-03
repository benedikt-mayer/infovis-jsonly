import mysql.connector
import datetime


cnx = mysql.connector.connect(user='root', password='root',
                              host='127.0.0.1',
                              database='newspapers', auth_plugin='mysql_native_password')

cursor = cnx.cursor()

# query = ("SELECT *"
#          "FROM newspapers.tokens AS token"
#          "INNER JOIN newspapers.documents_tokens AS doc_token"
#          "WHERE token.id = doc_token.token_id AND doc_token.document_id = 1;")
query = ("SELECT title, description FROM newspapers.documents;")

cursor.execute(query)

for (title, description) in cursor:
    print("title: {}, description: {}".format(
        title, description))

cursor.close()
cnx.close()