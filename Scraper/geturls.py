from firebase import firebase
import requests
from pdfreader import getdetails
from bs4 import BeautifulSoup
firebase=firebase.FirebaseApplication('https://trackpack-99f6c.firebaseio.com/',None)
result=firebase.get('/URLSCollection/','-MNJ-Bag5v5GO4vxru2D')
data=result["urls"]
for entry in data:
	if entry:
		try:
			url="https://cdsco.gov.in"+entry[3]
			if url=='https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadApprovalNewDrugs/2001.pdf':
				continue
			response=requests.get(url)
			if response.status_code==200:
				soupone=BeautifulSoup(response.content,'lxml')
				file_link=soupone.find('iframe')['src']
				print("https://cdsco.gov.in"+file_link)
				print(getdetails("https://cdsco.gov.in"+file_link))
		except:
			continue