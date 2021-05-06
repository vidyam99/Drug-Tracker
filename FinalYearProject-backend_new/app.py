import json
from web3 import Web3
from flask import Flask, request, render_template, session, url_for, redirect,flash,send_file
from datetime import datetime
from flask_cors import CORS,cross_origin
import pyqrcode 
import png
import requests,os
from pathlib import Path

app=Flask(__name__)
app.secret_key = 'BE Project'

ganache_url = "http://localhost:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
web3.eth.defaultAccount = web3.eth.accounts[0]

abi=json.load(open('abi.json','r'))
bytecode=json.load(open('bytecode.json','r'))['object']

SupplyChain = web3.eth.contract(abi=abi, bytecode=bytecode)

tx_hash = SupplyChain.constructor().transact()
tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

contract = web3.eth.contract(address = tx_receipt.contractAddress, abi=abi)

states={0:"Manufactured",1:"Packaged",2:"ForSale",3:"Sold",4:"Shipped",5:"Received",6:"Purchased"}
credentials = {}
keys = {}
count = 1

localhostt="http://127.0.0.1"

#DYNAMIC ROUTE

ngrokroute="http://c8014933ca51.ngrok.io"
DRUG_INFO_LINK=localhostt+':8000/Drug/'
PRODUCT_INFO_LINK=ngrokroute+'/product_info/'

#CONFIGURATION

app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'
app.static_folder = 'static'

cors = CORS(app, resources={r"/*": {"origins": "http://"+localhostt+":8000"}})

#DEFINING PATHS

location='\\static\\images\\'
dir_path = Path(os.path.dirname(os.path.realpath(__file__))+'\\'+location)

#ROUTES

@app.route('/',methods=['GET'])
@cross_origin()
def index():
	print(credentials)
	if 'logged_in' in session and session['logged_in']!=None:
		if session['logged_in']['usertype']=='Manufacturer':
			return redirect(url_for('manufacturer_home'))
		elif session['logged_in']['usertype']=='Distributor':
			return redirect(url_for('distributor_home'))
		elif session['logged_in']['usertype']=='Retailer':	
			return redirect(url_for('retailer_home'))
		elif session['logged_in']['usertype']=='Consumer':
			return redirect(url_for('consumer_home'))
	return render_template('index.html', value=0)

@app.route('/login',methods=['GET','POST'])
def login_page():
	if request.method=='GET':
		return render_template('login.html')
	if request.method=='POST':
		try:
			emailid=request.form['emailid']
			password=request.form['password']
			if emailid in credentials:
				print("no 3Error occured")
				if credentials[emailid]['password']==str(hash(password)):
					creds=credentials[emailid]
					creds['emailid']=emailid
					session['logged_in']=creds
					if session['logged_in']['usertype']=='Manufacturer':
						return redirect(url_for('manufacturer_home'))
					elif session['logged_in']['usertype']=='Distributor':
						return redirect(url_for('distributor_home'))
					elif session['logged_in']['usertype']=='Retailer':	
						return redirect(url_for('retailer_home'))
					elif session['logged_in']['usertype']=='Consumer':
						return redirect(url_for('consumer_home'))
					else:
						return render_template('index.html')
				else:
					flash("Password does not match.")
					return render_template('login.html')
			else:
				flash("Account does not exist. Create an account first.")
				return render_template('login.html')
		except:
			flash("Account does not exist. Create an account first.")
			return render_template('login.html')

@app.route('/signup',methods=['GET','POST'])
def signup_page():
	global count
	if request.method=='GET':
		return render_template('signup.html')
	if request.method=='POST':
		try:
			emailid=request.form['emailid']
			password=request.form['password']
			password=str(hash(password))
			usertype=request.form['usertype']
			name=request.form['name']
			mobile=request.form['mobile']
			address=web3.eth.accounts[count]
			count=count+1
			creds={'password':password, 'usertype':usertype, 'name':name, 'mobile':mobile, 'address':address}
			credentials[emailid]=creds
			creds['emailid']=emailid
			keys[address.lower()]=emailid
			session['logged_in']=creds
			if usertype=='Manufacturer':
				tx_hash=contract.functions.addManufacturer(address).transact()
				tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
				return redirect(url_for('manufacturer_home'))
			elif usertype=='Distributor':
				tx_hash=contract.functions.addDistributor(address).transact()
				tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
				return redirect(url_for('distributor_home'))
			elif usertype=='Retailer':	
				tx_hash=contract.functions.addRetailer(address).transact()
				tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
				return redirect(url_for('retailer_home'))
			elif usertype=='Consumer':
				tx_hash=contract.functions.addConsumer(address).transact()
				tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
				return redirect(url_for('consumer_home'))
		except Exception as e:
			flash('Some error occured')
			print(e)
			return render_template('signup.html')




#----------------------------------------MANUFACTURER------------------------------------------------


@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    return send_file(filename,as_attachment=True)

@app.route('/open/<path:filename>', methods=['GET', 'POST'])
def open(filename):
    return send_file(filename)

@app.route('/download_qrcode',methods=['GET','POST'])
def download_qrcode():
	if request.method=='GET':
		return render_template('download.html',data=session['logged_in'])
	if request.method=='POST':
		try:
			upc=request.form['upc']
			upc=int(upc)
			productitems=contract.functions.fetchProductDetails(upc).call()
			print(productitems[2])
			itemName=productitems[2]
			qr=pyqrcode.create(PRODUCT_INFO_LINK+itemName+'/'+str(upc))
			name=str(upc)+'.png'
			file_to_open=dir_path/name
			qr.png(file_to_open, scale = 6)
			return render_template('download.html',data=session['logged_in'],file=file_to_open)
		except Exception as e:
			print(e)
			flash("No such product exists")
			return render_template('download.html',data=session['logged_in'])

@app.route('/manufacturer', methods=['GET'])
def manufacturer_home():
	return render_template('manufacturer.html', value=0, data=session['logged_in'],role=1)

@app.route('/manufacturer/add_product', methods=['GET','POST'])
@cross_origin()
def manufacturer_add():
	options=requests.get(localhostt+':8000/DrugsName').json()['data']
	if request.method=='GET':
		return render_template('manufacturer.html',value=1, data=session['logged_in'],options=options,role=1)
	if request.method=='POST':
		try:
			upc=request.form['upc']
			upc=int(upc) 
			itemType=request.form['itemType']
			itemName=request.form['itemName']
			productNotes=request.form['productNotes']
			productPrice=request.form['productPrice']
			productQuantity=request.form['productQuantity']
			productQuantity=int(productQuantity)
			productExpiryDate=request.form['productExpiryDate']
			productBatch=request.form['productBatch']
			qr=pyqrcode.create(PRODUCT_INFO_LINK+itemName+'/'+str(upc))
			# print(1)
			name=str(upc)+'.png'
			file_to_open=dir_path/name
			qr.png(file_to_open, scale = 6)
			productPrice=Web3.toWei(productPrice,'ether')
			timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			location=request.form['location']
			# add quantity, expiryDate, batchNumber
			# print(2)
			tx_hash=contract.functions.manufactureItem(upc,itemType,itemName,productPrice,
			productNotes,timestamp,location,productQuantity,productExpiryDate,productBatch).transact({"from":session['logged_in']['address']})
			# print(3)
			tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
			# print(tx_receipt)
			# print(4)
			flash("Product added and packaged")
			tx_hash=contract.functions.packageItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
			# print(5)
			tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
			# print(6)
		except Exception as e:
			flash("Cannot add the product")
			print(e)
		finally:
			return render_template('manufacturer.html',value=0, data=session['logged_in'],role=1,file=file_to_open)


@app.route('/manufacturer/sell_product', methods=['GET','POST'])
def manufacturer_sell():
	if request.method=='GET':
		return render_template('manufacturer.html', value=3, data=session['logged_in'],role=1)
	if request.method=='POST':
		try:
			upc=int(request.form['upc'])
			timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			location=request.form['location']
			productQuantity=request.form['productQuantity']
			productQuantity=int(productQuantity)
			# add quantity
			print("Selling")
			print(0)
			tx_hash=contract.functions.sellItem(upc,timestamp,location,productQuantity).transact({'from':session['logged_in']['address']}) 
			# print(1)
			tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
			# print(2)
			flash("Product out for sale")
		except Exception as e:
			print(e)
			flash("Cannot sell the product . Check if product exists or has been sold")
		finally:
			return render_template('manufacturer.html', value=0, data=session['logged_in'],role=1,states=states)

@app.route('/manufacturer/ship_product', methods=['GET','POST'])
def manufacturer_ship():
	if request.method=='GET':
		return render_template('manufacturer.html', value=4, data=session['logged_in'])
	if request.method=='POST':
		try:
			upc=int(request.form['upc'])
			timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			location=request.form['location']
			# add quantity
			tx_hash=contract.functions.shipItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
			tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
			flash("Product shipped")
		except Exception as e:
			print(e)
			flash("Cannot ship the product")
		finally:
			return render_template('manufacturer.html', value=0, data=session['logged_in'],role=1,states=states)





#----------------------------------------DISTRIBUTOR------------------------------------------------





@app.route('/distributor', methods=['GET'])
def distributor_home():
	return render_template('distributor.html', value=0, data=session['logged_in'],role=2)

@app.route('/distributor/buy_product', methods=['GET','POST'])
def distributor_buy():
	if request.method=='GET':
		try:
			sale=contract.functions.itemsForSale().call()
			print('Available products to buy: ')
			print(sale)
			productitems=[]
			for item  in sale:
				print(item)
			for item in sale:
				itemDetails=contract.functions.fetchProductDetails(item).call()
				index=itemDetails[0]
				index=int(index)
				# print(index)
				item_info=json.loads(contract.functions.fetchItemHistory(item,index).call())
				print(item_info)
				print(item_info['Entry State'])
				if(item_info['Entry State']==2 and credentials[keys['0x'+item_info['By']]]['usertype']=='Manufacturer'):
					productitems.append(itemDetails)
					print(productitems)
				# display productitems properly in distributor.html
			return render_template('distributor.html', value=1, data=session['logged_in'],productitems=productitems,role=2,states=states)
		except Exception as e:
			print(e)
			flash("Some error occured")
			return render_template('distributor.html', value=1, data=session['logged_in'],role=2)
	if request.method=='POST':
		try:
			upc=int(request.form['upc'])
			price=request.form['price']
			price=Web3.toWei(price,'ether')
			timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			location=request.form['location']
			productQuantity=request.form['productQuantity']
			productQuantity=int(productQuantity)
			# new product id will be changed --> appended with 1
			# add quantity
			tx_hash=contract.functions.buyItem(upc,timestamp,location,productQuantity).transact({'from':session['logged_in']['address'],'value':price})
			tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
			# remove() function called within the contract -> no need here
			# contract.functions.remove(upc).transact({'from':session['logged_in']['address']})
			flash("Product bought")
			return render_template('distributor.html', value=2, data=session['logged_in'],role=2,states=states)
		except Exception as e:
			print(e)
			flash("Could not but the product or is already bought")
			return render_template('distributor.html', value=1, data=session['logged_in'],role=2)

@app.route('/distributor/receive_product', methods=['GET','POST'])
def distributor_receive():
	if request.method=='GET':
		return render_template('distributor.html',value=2,data=session['logged_in'],role=2)
	if request.method=='POST':
		try:
			upc=int(request.form['upc'])
			timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			location=request.form['location']
			# add quantity
			tx_hash=contract.functions.receiveItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
			tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
			flash("Product received")
			return render_template('distributor.html', value=3, data=session['logged_in'],role=2,states=states)
		except Exception as e:
			print(e)
			flash("Some error occured")
			return render_template('distributor.html', value=2, data=session['logged_in'],role=2)

@app.route('/distributor/sell_product', methods=['GET','POST'])
def distributor_sell():
	if request.method=='GET':
		return render_template('distributor.html', value=3, data=session['logged_in'],role=2)
	if request.method=='POST':
		try:
			upc=int(request.form['upc'])
			timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			location=request.form['location']
			productQuantity=request.form['productQuantity']
			productQuantity=int(productQuantity)
			tx_hash=contract.functions.sellItem(upc,timestamp,location,productQuantity).transact({'from':session['logged_in']['address']})
			tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
			flash("Product sold")
			return render_template('distributor.html', value=4, data=session['logged_in'],role=2,states=states)
		except:
			flash("Could not sell the product or already sold")
			return render_template('distributor.html', value=3, data=session['logged_in'],role=2)

@app.route('/distributor/ship_product', methods=['GET','POST'])
def distributor_ship():
	if request.method=='GET':
		return render_template('distributor.html', value=4, data=session['logged_in'],role=2)
	if request.method=='POST':
		try:
			upc=int(request.form['upc'])
			timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			location=request.form['location']
			tx_hash=contract.functions.shipItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
			tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
			flash("Product Shipped")
			return render_template('distributor.html', value=4, data=session['logged_in'],role=2,states=states)
		except:
			flash("Could not ship the product or already ship")
			return render_template('distributor.html', value=4, data=session['logged_in'],role=2)





#----------------------------------------RETAILER------------------------------------------------





@app.route('/retailer', methods=['GET'])
def retailer_home():
	return render_template('retailer.html', value=0, data=session['logged_in'],role=3)

@app.route('/retailer/buy_product', methods=['GET','POST'])
def retailer_buy():
	if request.method=='GET':
		sale=contract.functions.itemsForSale().call()
		print('Available products to buy: ')
		print(sale)
		productitems=[]
		for item in sale:
			itemDetails=contract.functions.fetchProductDetails(item).call()
			index=itemDetails[0]
			index=int(index)
			item_info=json.loads(contract.functions.fetchItemHistory(item,index).call())
			print(item_info)
			if(item_info['Entry State']==2 and credentials[keys['0x'+item_info['By']]]['usertype']=='Distributor'):
				productitems.append(itemDetails)
				print(productitems[-1])
			# display productitems properly in retailer.html
		return render_template('retailer.html', value=1, data=session['logged_in'],productitems=productitems,role=3)
	if request.method=='POST':
		try:
			upc=int(request.form['upc'])
			price=request.form['price']
			price=Web3.toWei(price,'ether')
			timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			location=request.form['location']
			productQuantity=request.form['productQuantity']
			productQuantity=int(productQuantity)
			tx_hash=contract.functions.buyItem(upc,timestamp,location,productQuantity).transact({'from':session['logged_in']['address'],'value':price})
			tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
			contract.functions.remove(upc).transact({'from':session['logged_in']['address']})
			flash("Product bought")
			return render_template('retailer.html', value=2, data=session['logged_in'],role=3,states=states)
		except:
			flash("Could not buy the item or already bought")
			return render_template('retailer.html', value=1, data=session['logged_in'],role=3)

@app.route('/retailer/receive_product', methods=['GET','POST'])
def retailer_receive():
	if request.method=='GET':
		return render_template('retailer.html',value=2,data=session['logged_in'],role=3)
	if request.method=='POST':
		try:
			upc=int(request.form['upc'])
			timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			location=request.form['location']
			tx_hash=contract.functions.receiveItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
			tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
			flash("Product received")
			return render_template('retailer.html',value=3,data=session['logged_in'],role=3,states=states)
		except:
			flash("Could not receive the product . Some error occured")
			return render_template('retailer.html',value=2,data=session['logged_in'],role=3)

@app.route('/retailer/sell_product', methods=['GET','POST'])
def retailer_sell():
	if request.method=='GET':
		return render_template('retailer.html', value=3, data=session['logged_in'],role=3)
	if request.method=='POST':
		try:
			upc=int(request.form['upc'])
			timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			location=request.form['location']
			productQuantity=request.form['productQuantity']
			productQuantity=int(productQuantity)
			tx_hash=contract.functions.sellItem(upc,timestamp,location,productQuantity).transact({'from':session['logged_in']['address']})
			tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
			flash("Product sold")
			return render_template('retailer.html',value=3,data=session['logged_in'],role=3,states=states)
		except:
			flash("Could not sell the product or the product has been sold")
			return render_template('retailer.html',value=3,data=session['logged_in'],role=3)





#----------------------------------------CONSUMER------------------------------------------------





@app.route('/consumer', methods=['GET'])
def consumer_home():
	return render_template('consumer.html', value=0, data=session['logged_in'],role=4)

@app.route('/consumer/buy_product', methods=['GET','POST'])
def consumer_buy():
	if request.method=='GET':
		sale=contract.functions.itemsForSale().call()
		print('Available products to buy: ')
		print(sale)
		productitems=[]
		for item in sale:
			itemDetails=contract.functions.fetchProductDetails(item).call()
			index=itemDetails[0]
			index=int(index)
			item_info=json.loads(contract.functions.fetchItemHistory(item,index).call())
			print(item_info)
			if(item_info['Entry State']==2 and credentials[keys['0x'+item_info['By']]]['usertype']=='Retailer'):
				productitems.append(itemDetails)
				print(productitems[-1])
			# display productitems properly in consumer.html
		return render_template('consumer.html', value=1, data=session['logged_in'],productitems=productitems,role=4,states=states)
	if request.method=='POST':
		try:
			upc=int(request.form['upc'])
			price=request.form['price']
			price=Web3.toWei(price,'ether')
			timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
			location=request.form['location']
			productQuantity=request.form['productQuantity']
			productQuantity=int(productQuantity)
			tx_hash=contract.functions.buyItem(upc,timestamp,location,productQuantity).transact({'from':session['logged_in']['address'],'value':price})
			tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
			contract.functions.remove(upc).transact({'from':session['logged_in']['address']})
			flash("Product bought")
			return render_template('consumer.html', value=2, data=session['logged_in'],role=4,states=states)
		except Exception as e:
			print(e)
			flash("Could not buy product or already bought")
			return render_template('consumer.html', value=1, data=session['logged_in'],role=4,states=states)

@app.route('/consumer/product_info', methods=['GET','POST'])
def product_info():
	if request.method=='GET':
		return render_template('consumer.html', value=2, data=session['logged_in'],role=4)
	if request.method=='POST':
		try:
			productitems=[]
			upc=int(request.form['upc'])
			# returns json
			productitems.append(contract.functions.fetchProductDetails(upc).call())
			# display productitems in consumer.html
			return render_template('consumer.html', value=2, data=session['logged_in'],productitems=productitems,role=4,states=states)
		except:
			return render_template('consumer.html', value=2, data=session['logged_in'],role=4)

@app.route('/consumer/supply_chain_info', methods=['GET','POST'])
def supply_chain_info():
	if request.method=='GET':
		return render_template('consumer.html', value=3, data=session['logged_in'],role=4)
	if request.method=='POST':
		try:
			productitems=[]
			upc=int(request.form['upc'])
			index=contract.functions.fetchProductDetails(upc).call()[0]
			for i in range(1,index+1):
				# item_info=json.loads(contract.functions.fetchItemHistory(upc,i).call())
				# print(item_info)
				productitems.append(contract.functions.fetchItemHistoryArray(upc,i).call())
			return render_template('consumer.html', value=3, data=session['logged_in'],productitems=productitems,role=4,states=states)
		except:
			flash('Some error occured')
			return render_template('consumer.html',value=3,data=session['logged_in'],role=4)






#----------------------------------------GUEST------------------------------------------------






@app.route('/guest_product_info', methods=['GET','POST'])
def home_product_info():
	if request.method=='GET':
		return render_template('index.html', value=2)
	if request.method=='POST':
		try:
			productitems=[]
			upc=int(request.form['upc'])
			# returns json
			productitems.append(contract.functions.fetchProductDetails(upc).call())
			# display productitems in index.html
			print(productitems)
			print(productitems[0])
			return render_template('index.html', value=2,productitems=productitems)
		except:
			flash("No such product found")
			return render_template('index.html', value=2)

@cross_origin
@app.route('/product_info/<drugname>/<identifier>', methods=['GET','POST'])
def c_product_info(drugname,identifier):
	print(drugname,identifier)
	try:
		try:
			approvaldata=requests.get(DRUG_INFO_LINK+drugname).json()['data']
			print(approvaldata)
		except:
			print("No such appoval data")
			return render_template('productdetails.html',value=0)
		productitems=[]
		upc=int(identifier)
		itemInfo=contract.functions.fetchProductDetails(upc).call()
		productitems.append(itemInfo)
		index=itemInfo[0]
		productsupplyitems=[]
		for i in range(1,index+1):
				# item_info=json.loads(contract.functions.fetchItemHistory(upc,i).call())
				# print(item_info)
				productsupplyitems.append(contract.functions.fetchItemHistoryArray(upc,i).call())
		return render_template('productdetails.html', value=1,productitems=productitems,productsupplyitems=productsupplyitems,approvaldata=approvaldata,states=states)
	except:
		flash("No such product found")
		return render_template('productdetails.html', value=0)

# @app.route('/product_supplychain_info/<identifier>', methods=['GET','POST'])
# def product_supply_info(identifier):
# 	try:
# 		productitems=[]
# 		upc=int(identifier)
# 		productitems.append(contract.functions.fetchProductDetails(upc).call())
# 		return render_template('productdetails.html', value=2,productitems=productitems)
# 	except:
# 		flash("No such product found")
# 		return render_template('productdetails.html', value=0)

@app.route('/guest_supply_chain_info', methods=['GET','POST'])
def home_supply_chain_info():
	if request.method=='GET':
		return render_template('index.html', value=3)
	if request.method=='POST':
		try:
			productitems=[]
			upc=int(request.form['upc'])
			index=contract.functions.fetchProductDetails(upc).call()[0]
			index=int(index)
			for i in range(1,index+1):
				# print(2)
				# item_info=json.loads(contract.functions.fetchItemHistory(upc,i).call())
				# print(3)
				# print(item_info)
				productitems.append(contract.functions.fetchItemHistoryArray(upc,i).call())
				# print(4)
			# print(5)
			print(productitems)
			return render_template('index.html', value=3,productitems=productitems,states=states)
		except Exception as e:
			print("Error occured")
			print(e)
			return render_template('index.html', value=3)

@app.route('/logout', methods=['GET'])
def logout_user():
	session.pop('logged_in', None)
	return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)

# pages -

# login signup:
# emailid
# password
# name 
# mobile no 

# manufacturer:
# add product
# package product
# sell product
# ship product

# distributor:
# buy product
# sell product
# ship product
# receive product

# retailer:
# buy product
# receive product
# sell product

# consumer:
# get product info
# get supply chain info
# buy product

# convert product price to Wei

# to do - add qr code, add verification api, display available products to the buyer, display info a little neatly, work on UI if time



#TO DO:
#add quantity of products bought
