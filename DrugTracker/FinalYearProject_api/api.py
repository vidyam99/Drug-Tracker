from flask import Flask
from flask_restful import Resource,Api
from firebase import firebase

#url=firebasecreds
#firebase=firebase.FirebaseApplication(YOUR_CREDS)
result=firebase.get('/DrugsInfo/','')
finalresult=[]
drugnames=[]
for key,value in result.items():
	for d in value['data']:
		finalresult.append(d)
		drugnames.append(d['Name'])
app=Flask(__name__)
api=Api(app)

class DrugInfoList(Resource):
	def __init__(self):
		pass
	def get(self):
		return {"data":finalresult}
class DrugNameList(Resource):
	def __init__(self):
		pass
	def get(self):
		return {"data":drugnames}
class Drugs(Resource):
	def __init__(self):
		pass
	def get(self,identifier):
		return {'data':next((item for item in finalresult if item['Name'] ==identifier),[])}
api.add_resource(DrugInfoList,'/DrugsInfo')
api.add_resource(DrugNameList,'/DrugsName')
api.add_resource(Drugs,'/Drug/<string:identifier>')
if __name__=="__main__":
	app.run(debug=True,port=8000)


#Azelnidipine tablets IP 8 mg