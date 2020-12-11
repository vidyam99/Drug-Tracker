from flask import Flask
from flask_restful import Resource,Api
from firebase import firebase

firebase=firebase.FirebaseApplication('https://trackpack-99f6c.firebaseio.com/',None)
result=firebase.get('/DrugsInfo/','')
app=Flask(__name__)
api=Api(app)

class Drugs(Resource):
	def __init__(self):
		pass
	def get(self):
		return result
api.add_resource(Drugs,'/')
if __name__=="__main__":
	app.run(debug=True)