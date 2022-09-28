import web3
import configparser
import sys
import time
import re
import requests
from bs4 import BeautifulSoup
# from web3.utils.datastructures import HexBytes
#from web3.datastructures import HexBytes
import hexbytes
from hexbytes import HexBytes
import base64

import http.cookiejar as cookielib

configParser = configparser.RawConfigParser()
configFilePath = r'settings.ini'
configParser.read(configFilePath)

from_addr = configParser.get('options', 'from_addr')
to_addr = configParser.get('options', 'to_addr')
eth_amount = float(configParser.get('options', 'eth_amount'))
gas_limit = int(configParser.get('options', 'gas_limit'))
gas_price = int(configParser.get('options', 'gas_price'))

print ('From: {0}'.format(from_addr))
print ('Amount of ethereum to send: {0:.6f}'.format(eth_amount))
print ('Gas limit (smart contracts may need more): {0}'.format(gas_limit))
print ('Gas price (most important): {0}'.format(gas_price))
print ()

cookies = cookielib.MozillaCookieJar('cookies.txt')
cookies.load()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}

def makesouprequest(turl):
	while True:
		r = requests.get(turl, headers=headers)#, cookies=cookies, timeout=3)
		if r.status_code != 200:
			print('ERROR:', int(r.status_code))
			print('Retry after 1 sec...')
			time.sleep(1)
			continue
	tsoup = BeautifulSoup(r.text, 'html.parser')
	return tsoup

def findstatus(all_divs):
	for div in all_divs:
		if 'Status:' in div.text:
			return div.text
	return ''

def contractstatus():
	developer_addr = str(configParser.get('options', 'developer_addr'))
	developer_url = 'https://etherscan.io/address/' + developer_addr
	# headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}#,
				#"Accept-Encoding":"gzip, deflate", 
				#"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 
				#"DNT":"1",
				#"Connection":"close", 
				#"Upgrade-Insecure-Requests":"1"}

	# ignore transactions 
	# ignoretx = []
	ignoretx = ['0x9c34d24b182b720fcb5feadd564d2f47915bb4a90f6eac0178159f8ac3cf6b1d',
				 '0xb8e2a1935c63549c10ff15e61b81d8fc0878ff3e84e17b7656ebb37304ad1554',
				 '0x30325388b6b172a7dcd7a530349c0f74d6c0ee41c3d1e24196d5ba29538639ef',
				 '0x84475c3be3b44f5d00405548553b7e2c3da8274cb7dce3dd5be64eeeed601260',
				 '0x8f12d03407f143154995fbe310ff2b9121285e543b3d432282832b905b8c9a46']
	ignoretx = [] # REMOVE THIS LINE IN ACTUAL EXECUTION
	while(True):
		print('Checking...')
		soup = makesouprequest(developer_url)
		tx_divs = soup.find_all('div', id = 'transactions')[0]
		tx_body = tx_divs.find_all('tbody')[0]
		tx_rows = tx_body.find_all('tr')[0:3]
		for row in tx_rows:
			txhash = row.find_all('td')[0].text
			if txhash not in ignoretx:
				txurl = 'https://etherscan.io/tx/' + txhash
				txsoup = makesouprequest(txurl)
				destination = txsoup.find_all('span', id = 'spanToAdd')[0].text
				# check destination
				if destination.lower() == to_addr.lower():
					# find contract data
					inputdata = txsoup.find_all('textarea', id = 'inputdata')
					if(len(inputdata) > 0):
						# check contract data
						if('unpause() ***' in inputdata[0].text):
							print('ALERT: PENDING UNPAUSE COMMAND FOUND - WAITING CONFIRMATION')
							print('https://etherscan.io/tx/{0}'.format(txhash))
							status = 'Pending'
							while status == 'Pending':
								all_divs = txsoup.find_all('div', attrs = {'class':'row'}) # all divs with class row
								# find status message
								statusmsg = findstatus(all_divs)							
								if 'Success' in statusmsg:
									return True
								elif 'Fail' in statusmsg:
									status = 'Failure'
									ignoretx.append(txhash)
								else: # if pending or no status found, keep querying same transaction 
									txsoup = makesouprequest(txurl)

#w = web3.Web3(web3.HTTPProvider('https://mainnet.infura.io/805o3JxUvzvpJOAGRl56'))
# w = web3.Web3(web3.HTTPProvider('https://api.myetherapi.com/eth'))
w = web3.Web3(web3.HTTPProvider('https://api.myetherwallet.com/eth'))
balance = float(w.fromWei(w.eth.getBalance(from_addr), 'ether'))
print ('Ether balance in account: {0}'.format(balance))

if balance - eth_amount < 0.0004:
	print ('Not enough eth in account')
	sys.exit(0)

# run contract checking below
if contractstatus() == True:
	# attempt to send ethereum
	while True:
		try:
			transaction = {
			'to':to_addr,
			'from':from_addr,
			'value':int(eth_amount*(10**18)),
			'gas':gas_limit,
			'gasPrice':int(gas_price*(10**9)),
			'chainId':1,
			'nonce':w.eth.getTransactionCount(from_addr)
			}
			# https://stackoverflow.com/questions/157938/hiding-a-password-in-a-python-script-insecure-obfuscation-only
			key = base64.b64decode(configParser.get('options', 'key').encode()).decode()
			signed_transaction = w.eth.account.signTransaction(transaction, key)
			transaction_id = w.eth.sendRawTransaction(signed_transaction.rawTransaction)
			key = 'base64'
			break
		except Exception as e:
			print ('Error occured: {0}\t TRYING AGAIN...'.format(str(e)))

	print ('\n Transaction send. ID = https://etherscan.io/tx/{0}'.format(transaction_id.hex()))

	#w.eth.getTransactionCount(from_addr)

