import json
from web3 import Web3
from flask import Flask, request, render_template, session, url_for, redirect
from datetime import datetime
import pyqrcode 
import png

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

credentials = {}
keys = {}
count = 1 

@app.route('/',methods=['GET'])
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
	return render_template('index.html', value=1)

@app.route('/login',methods=['GET','POST'])
def login_page():
	if request.method=='GET':
		return render_template('login.html')
	if request.method=='POST':
		emailid=request.form['emailid']
		password=request.form['password']
		if emailid in credentials:
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
				return "Password does not match."
		return "Account does not exist. Create an account first."

@app.route('/signup',methods=['GET','POST'])
def signup_page():
	global count
	if request.method=='GET':
		return render_template('signup.html')
	if request.method=='POST':
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

@app.route('/manufacturer', methods=['GET'])
def manufacturer_home():
	return render_template('manufacturer.html', value=0, data=session['logged_in'])

@app.route('/manufacturer/add_product', methods=['GET','POST'])
def manufacturer_add():
	if request.method=='GET':
		return render_template('manufacturer.html', value=1, data=session['logged_in'])
	if request.method=='POST':
		upc=request.form['upc']
		qr=pyqrcode.create(upc)
		qr.png('myqr.png', scale = 6)
		upc=int(upc) 
		itemType=request.form['itemType']
		itemName=request.form['itemName']
		productNotes=request.form['productNotes']
		productPrice=request.form['productPrice']
		productPrice=Web3.toWei(productPrice,'ether')
		timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		location=request.form['location']
		tx_hash=contract.functions.manufactureItem(upc,itemType,itemName,productPrice,
			productNotes,timestamp,location).transact({"from":session['logged_in']['address']})
		tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
		# print(tx_receipt)
		return "Done"

@app.route('/manufacturer/package_product', methods=['GET','POST'])
def manufacturer_package():
	if request.method=='GET':
		return render_template('manufacturer.html', value=2, data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		location=request.form['location']
		tx_hash=contract.functions.packageItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
		tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
		# print(tx_receipt)
		return "Done"

@app.route('/manufacturer/sell_product', methods=['GET','POST'])
def manufacturer_sell():
	if request.method=='GET':
		return render_template('manufacturer.html', value=3, data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		location=request.form['location']
		tx_hash=contract.functions.sellItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
		tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
		# print(tx_receipt)
		return "Done"

@app.route('/manufacturer/ship_product', methods=['GET','POST'])
def manufacturer_ship():
	if request.method=='GET':
		return render_template('manufacturer.html', value=4, data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		location=request.form['location']
		tx_hash=contract.functions.shipItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
		tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
		# print(tx_receipt)
		return "Done"

@app.route('/distributor', methods=['GET'])
def distributor_home():
	return render_template('distributor.html', value=0, data=session['logged_in'])

@app.route('/distributor/buy_product', methods=['GET','POST'])
def distributor_buy():
	if request.method=='GET':
		sale=contract.functions.itemsForSale().call()
		print('Available products to buy: ')
		for item in sale:
			index=contract.functions.fetchProductDetails(item).call()[-1]
			item_info=json.loads(contract.functions.fetchItemHistory(item,index).call())
			if(item_info['Entry State']==2 and credentials[keys['0x'+item_info['By']]]['usertype']=='Manufacturer'):
				print(contract.functions.fetchProductDetails(item).call())
		return render_template('distributor.html', value=1, data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		price=request.form['price']
		price=Web3.toWei(price,'ether')
		timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		location=request.form['location']
		tx_hash=contract.functions.buyItem(upc,timestamp,location).transact({'from':session['logged_in']['address'],'value':price})
		tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
		contract.functions.remove(upc).transact({'from':session['logged_in']['address']})
		# print(tx_receipt)
		return "Done"

@app.route('/distributor/receive_product', methods=['GET','POST'])
def distributor_receive():
	if request.method=='GET':
		return render_template('distributor.html',value=2,data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		location=request.form['location']
		tx_hash=contract.functions.receiveItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
		tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
		# print(tx_receipt)
		return "Done"

@app.route('/distributor/sell_product', methods=['GET','POST'])
def distributor_sell():
	if request.method=='GET':
		return render_template('distributor.html', value=3, data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		location=request.form['location']
		tx_hash=contract.functions.sellItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
		tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
		# print(tx_receipt)
		return "Done"

@app.route('/distributor/ship_product', methods=['GET','POST'])
def distributor_ship():
	if request.method=='GET':
		return render_template('distributor.html', value=4, data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		location=request.form['location']
		tx_hash=contract.functions.shipItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
		tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
		# print(tx_receipt)
		return "Done"

@app.route('/retailer', methods=['GET'])
def retailer_home():
	return render_template('retailer.html', value=0, data=session['logged_in'])

@app.route('/retailer/buy_product', methods=['GET','POST'])
def retailer_buy():
	if request.method=='GET':
		sale=contract.functions.itemsForSale().call()
		print('Available products to buy: ')
		for item in sale:
			index=contract.functions.fetchProductDetails(item).call()[-1]
			item_info=json.loads(contract.functions.fetchItemHistory(item,index).call())
			if(item_info['Entry State']==2 and credentials[keys['0x'+item_info['By']]]['usertype']=='Distributor'):
				print(contract.functions.fetchProductDetails(item).call())
		return render_template('retailer.html', value=1, data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		price=request.form['price']
		price=Web3.toWei(price,'ether')
		timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		location=request.form['location']
		tx_hash=contract.functions.buyItem(upc,timestamp,location).transact({'from':session['logged_in']['address'],'value':price})
		tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
		contract.functions.remove(upc).transact({'from':session['logged_in']['address']})
		# print(tx_receipt)
		return "Done"

@app.route('/retailer/receive_product', methods=['GET','POST'])
def retailer_receive():
	if request.method=='GET':
		return render_template('retailer.html',value=2,data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		location=request.form['location']
		tx_hash=contract.functions.receiveItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
		tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
		# print(tx_receipt)
		return "Done"

@app.route('/retailer/sell_product', methods=['GET','POST'])
def retailer_sell():
	if request.method=='GET':
		return render_template('retailer.html', value=3, data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		location=request.form['location']
		tx_hash=contract.functions.sellItem(upc,timestamp,location).transact({'from':session['logged_in']['address']})
		tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
		# print(tx_receipt)
		return "Done"

@app.route('/consumer', methods=['GET'])
def consumer_home():
	return render_template('consumer.html', value=0, data=session['logged_in'])

@app.route('/consumer/buy_product', methods=['GET','POST'])
def consumer_buy():
	if request.method=='GET':
		sale=contract.functions.itemsForSale().call()
		print('Available products to buy: ')
		for item in sale:
			index=contract.functions.fetchProductDetails(item).call()[-1]
			item_info=json.loads(contract.functions.fetchItemHistory(item,index).call())
			if(item_info['Entry State']==2 and credentials[keys['0x'+item_info['By']]]['usertype']=='Retailer'):
				print(contract.functions.fetchProductDetails(item).call())
		return render_template('consumer.html', value=1, data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		price=request.form['price']
		price=Web3.toWei(price,'ether')
		timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		location=request.form['location']
		tx_hash=contract.functions.buyItem(upc,timestamp,location).transact({'from':session['logged_in']['address'],'value':price})
		tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
		contract.functions.remove(upc).transact({'from':session['logged_in']['address']})
		# print(tx_receipt)
		return "Done"

@app.route('/consumer/product_info', methods=['GET','POST'])
def product_info():
	if request.method=='GET':
		return render_template('consumer.html', value=2, data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		print(contract.functions.fetchProductDetails(upc).call())
		return "Done"

@app.route('/consumer/supply_chain_info', methods=['GET','POST'])
def supply_chain_info():
	if request.method=='GET':
		return render_template('consumer.html', value=3, data=session['logged_in'])
	if request.method=='POST':
		upc=int(request.form['upc'])
		index=contract.functions.fetchProductDetails(upc).call()[-1]
		for i in range(1,index+1):
			item_info=json.loads(contract.functions.fetchItemHistory(upc,i).call())
			print(item_info)
		return "Done"

@app.route('/guest_product_info', methods=['GET','POST'])
def home_product_info():
	if request.method=='GET':
		return render_template('index.html', value=2)
	if request.method=='POST':
		upc=int(request.form['upc'])
		print(contract.functions.fetchProductDetails(upc).call())
		return "Done"

@app.route('/guest_supply_chain_info', methods=['GET','POST'])
def home_supply_chain_info():
	if request.method=='GET':
		return render_template('index.html', value=3)
	if request.method=='POST':
		upc=int(request.form['upc'])
		index=contract.functions.fetchProductDetails(upc).call()[-1]
		for i in range(1,index+1):
			item_info=json.loads(contract.functions.fetchItemHistory(upc,i).call())
			print(item_info)
		return "Done"

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