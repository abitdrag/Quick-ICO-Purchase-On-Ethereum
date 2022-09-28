# Introduction
This repository demonstrate one of the way to purchase coin automatically on listing of it on Ethereum Blockchain. Transaction details are fetched from Etherscan using webscrapping. Once the required transaction is located, we wait for it to get confirmed. Then ETH is sent to destination address.  

# How to use
**Import libraries**     
Web3:   
`pip install web3`  
Configparser:    
`pip install configparser`   
BeautifulSoup:   
`pip install beautifulsoup4`   
HexBytes:    
`pip install hexbytes`   

**Fill the configuration file - settings.ini:**    
Add your source address (from where you are sending ETH) as ***from_addr***    
Add key of source address as ***key***   
Add destination address (where you are sending ETH) as ***to_addr***   
Add ETH amount you want to send as ***eth_amount***   
Add gas limit of your transaction as ***gas_limit***   
Add gas price of your transaction as ***gas_price***   
