## Blockchain based Supply Chain Monitoring System (for Drugs) 

A blockchain based system which traces a drug back to its origin to verify the authenticity of drug and the whole supply chain of the drug can be visible to customer.


### Comprises of the following main components:
    1.Blockchain Smart Contract written in Solidity to store the supplychain information
    2.Web Application with Flask backend to add / buy / sell / ship / receive product
    3.REST API to fetch verified drug information from database
    4.Scraping service to get verified drugs from CDSCO website
    5.QRCODE Generator (included in Flask Backend)
    6.Flutter application to scan QRCode

![System Design]()

Initial steps:

1. CDSCO portal holds the data of the verified drugs in pdf format .These pdfs are scraped using the scraper service and stored in Firebase.This service will be called periodically (since the data doesn't change often).

2. An API makes call to this firebase database to get the verified drug information.

(README to be updated ) 

