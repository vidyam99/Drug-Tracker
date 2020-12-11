import requests
from collections import defaultdict
from bs4 import BeautifulSoup
from firebase import firebase
firebase=firebase.FirebaseApplication('https://trackpack-99f6c.firebaseio.com/',None)
url=input().strip()
response=requests.get(url)
if response.status_code==200:
	print("Opened")
	soupone=BeautifulSoup(response.content,'lxml')
	table=soupone.find('table')
	table_rows=table.find_all('tr')
	links=[]
	all_data=defaultdict(list)
	for row in table_rows:
		table_row_data=row.find_all('td')
		row_data=[]
		for data in table_row_data:
			if data.find('a'):
				links.append(data.find('a')['href'])
				row_data.append(links[-1])
			else:
				row_data.append(data.text)
		all_data["urls"].append(row_data[:])
#print(*links,sep="\n")
result=firebase.post('/URLSCollection/',all_data)
print(result)