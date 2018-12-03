from flask import Flask, request
from flask_restful import Resource, Api
from flaskext.mysql import MySQL
app = Flask(__name__)
mysql = MySQL()
api = Api(app)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'newspapers'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

class Title(Resource):
    def get(self):

        conn = mysql.connect()
        cursor =conn.cursor()

        cursor.execute("SELECT title, description FROM newspapers.documents")
        data = cursor.fetchone()
        
        return str(data)

api.add_resource(Title, '/') # Route_1

if __name__ == '__main__':
     app.run(port='5002')