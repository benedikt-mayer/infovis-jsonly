from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
import mysql.connector
import datetime
# from flask.ext.jsonpify import jsonify

# db_connect = create_engine('sqlite:///chinook.db')
app = Flask(__name__)
api = Api(app)

class Employees(Resource):
    def get(self):
        
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
        result = cursor.fetchall()
        # title = result[0].title
        # description = result[0].description
        cursor.close()
        cnx.close()
        # return "title: {}, description: {}".format(title, description)
        return str(result[0])

        # conn = db_connect.connect() # connect to database
        # query = conn.execute("select * from employees") # This line performs query and returns json result
        # return {'employees': [i[0] for i in query.cursor.fetchall()]} # Fetches first column that is Employee ID
        # return "hi"

# class Tracks(Resource):
#     def get(self):
#         conn = db_connect.connect()
#         query = conn.execute("select trackid, name, composer, unitprice from tracks;")
#         result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
#         return jsonify(result)

# class Employees_Name(Resource):
#     def get(self, employee_id):
#         conn = db_connect.connect()
#         query = conn.execute("select * from employees where EmployeeId =%d "  %int(employee_id))
#         result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
#         return jsonify(result)
        

api.add_resource(Employees, '/employees') # Route_1
# api.add_resource(Tracks, '/tracks') # Route_2
# api.add_resource(Employees_Name, '/employees/<employee_id>') # Route_3


if __name__ == '__main__':
     app.run(port='5002')