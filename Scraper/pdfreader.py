# import urllib.request
# from PyPDF2 import PdfFileWriter, PdfFileReader
# from io import StringIO

# #url = "https://cdsco.gov.in/opencms/opencms/system/modules/CDSCO.WEB/elements/download_file_division.jsp?num_id=MzIxMQ=="
# url="https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadApprovalNewDrugs/1961_1970.pdf"
# writer = PdfFileWriter()

# req=urllib.request.Request(url)
# with urllib.request.urlopen(req) as response:
# 	remoteFile = response.read()
# memoryFile = StringIO(remoteFile)
# pdfFile = PdfFileReader(memoryFile)

# for pageNum in xrange(pdfFile.getNumPages()):
#         currentPage = pdfFile.getPage(pageNum)
#         #currentPage.mergePage(watermark.getPage(0))
#         writer.addPage(currentPage)


# outputStream = open("output.pdf","wb")
# writer.write(outputStream)
# outputStream.close()

# import urllib.request
# response=urllib.request.urlopen("https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadApprovalNewDrugs/1961_1970.pdf")  
# print(content.read())

import io
import requests
import PyPDF2
import tabula
import json
from firebase import firebase
firebase=firebase.FirebaseApplication('https://trackpack-99f6c.firebaseio.com/',None)
def getdetails(url):
	response = requests.get(url, stream=True)
	pdf = PyPDF2.PdfFileReader(io.BytesIO(response.content))
	#print(pdf)
	#df=tabula.read_pdf(url,pages="all")
	tabula.convert_into(url,"outputnew.json",output_format="json",pages="all")
	# for page in range(pdf.getNumPages()):
	#         print(pdf.getPage(page).extractText())
	with open("outputnew.json") as file:
		file_data=json.load(file)
	sol=[]
	for row in range(len(file_data)):
		data=file_data[row]["data"]
		#print(data)
		n=len(data)
		for i in range(n):
			if row==0 and i==0:
				continue
			temp=[]
			m=len(data[i])
			#print(m)
			#print(data[i])
			if m>=6:
				temp.append(data[i][0]["text"].replace('\r'," "))
				temp.append((data[i][1]["text"]+data[i][2]["text"]).replace('\r'," "))
				ans=""
				for s in range(3,m-1):
					ans+=data[i][s]["text"].replace('\r'," ")
				temp.append(ans)
				temp.append(data[i][-1]["text"].replace('\r'," "))
			elif m==5:
				temp.append(data[i][0]["text"].replace('\r'," "))
				temp.append(data[i][1]["text"].replace('\r'," "))
				temp.append((data[i][2]["text"]+data[i][3]["text"]).replace('\r'," "))
				temp.append(data[i][4]["text"].replace('\r'," "))
			else:
				temp.append(data[i][0]["text"].replace('\r'," "))
				temp.append(data[i][1]["text"].replace('\r'," "))
				temp.append(data[i][2]["text"].replace('\r'," "))
				temp.append(data[i][3]["text"].replace('\r'," "))
			if sol and temp[0]=='':
				for sr in range(len(temp)):
					sol[-1][sr]+=" "+temp[sr]
			else:
				sol.append(temp)
		datadict={"data":[]}
		for i in sol:
			temp={}
			temp["Entry_Id"]=i[0]
			temp["Name"]=i[1]
			temp["Indication"]=i[2]
			temp["Date"]=i[3]
			datadict["data"].append(temp)
		print(datadict)
		return datadict
		#result=firebase.post('/DrugsInfo/',datadict)

#getdetails('https://cdsco.gov.in/opencms/resources/UploadCDSCOWeb/2018/UploadApprovalNewDrugs/1981_1990.pdf')