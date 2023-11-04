from dotenv import load_dotenv
import signal
import sys
import os
import sqlite3
import requests
import asyncio
import json
import logging #relatively new to this, but it seems to be popular (logging erros, etc)
from pathlib import Path
import socket
import threading

PORT = 5050
HEADER = 64
machineIP = requests.get('https://api.ipify.org')
SERVER = socket.gethostbyname(socket.gethostname()) #socket.gethostbyname('localhost') #later will make it public
#machineIP.content.decode('utf-8')
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"
load_dotenv()
APIKEY = os.getenv("APIKEY")

#Initialise connection
try:
    connectionInit = sqlite3.connect(f'{Path(__file__).parent.joinpath("Database","Crypto.db")}')
    print("Successful")
except:
    print("Failure")
    sys.exit(1)
#Shell scrip will move the databse from this into the folder called Database
'''
Will focus on this later on (more advanced)
'''


#create socket object
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

#if database was usccessfully created, we want to be able to execute comands
executeCom = connectionInit.cursor()

#API DAILY LIMIT REACHED
dailyLimitReached = "Thank you for using Alpha Vantage! Our standard API rate limit is 25 requests per day. Please subscribe to any of the premium plans at https://www.alphavantage.co/premium/ to instantly remove all daily rate limits."


#logging configurations
logging.basicConfig(filename=f'{Path(__file__).parent.joinpath("logs","logs.log")}', format='%(asctime)s %(message)s', filemode='a') #set to append

#will create logger object and also set threshold of logger
logs = logging.getLogger()
logs.setLevel(logging.DEBUG)

#https://www.alphavantage.co/documentation/

CWD = os.getcwd()
os.chdir(f'{Path(__file__).parent.joinpath("Database")}')
print("Testing")
try:
    checkIfTableExist = """ SELECT count(name) FROM  sqlite_master WHERE type='table' AND name='Crypto';
        """
    #print("Table is ",executeCom.execute(checkIfTableExist))
    try:
        if executeCom.fetchone()[0] == 1: #returns 1 if table does exist
            print("Table already exist")
            #fix this to make sure table is not created if it lready exists
            #        ID INTEGER PRIMARY KEY, 
        else:
            table = """CREATE TABLE Crypto(
            CryptoSignature CHAR(10) NOT NULL, 
            CryptoName CHAR(25) NOT NULL, 
            CurrencySignature CHAR(10) NOT NULL, 
            CurrencyName CHAR(25) NOT NULL, 
            ExchangeRate INTEGER, 
            LastRefreshed CHAR(20), 
            TimeZone CHAR(5) NOT NULL
            ); """
            executeCom.execute(table)
            #What if the table already exists???
            print("SQL executed")
    except:
            table = """CREATE TABLE Crypto(
            CryptoSignature CHAR(10) NOT NULL, 
            CryptoName CHAR(25) NOT NULL, 
            CurrencySignature CHAR(10) NOT NULL, 
            CurrencyName CHAR(25) NOT NULL, 
            ExchangeRate INTEGER, 
            LastRefreshed CHAR(20), 
            TimeZone CHAR(5) NOT NULL
            ); """
            executeCom.execute(table)
            #What if the table already exists???
            print("SQL executed")
except Exception  as e:
    #I bel
    print(e)

print("Testing")
#Now it seems like in order for us to execute our SQL, we have to be in the direcotry where the databse is
#so chnage current working direcotry to the databsae
'''first = """INSERT INTO Crypto VALUES
                   ("BTC","Bitcoin","USD","United States Dollar",34385.47000000,"2023-11-03 17:51:01","UTC"),
                   ("ETH","Ethereum","USD","United States Dollar",1803.45000000,"2023-11-03 17:51:01","UTC"),
                   ("BNB","Binance-Coin","USD","United States Dollar","228.32777855","2023-11-03 17:51:01","UTC"),
                   ("XRP","Ripple","USD","United States Dollar",0.60430000,"2023-11-03 17:51:06","UTC"),
                   ("SOL","Solana","USD","United States Dollar",38.75000000,"2023-11-03 17:51:08","UTC"),
                   ("ADA","Cardano","USD","United States Dollar",0.31650000,"2023-11-03 17:51:12","UTC"),
                   ("DODGE","DodgeCoin","USD","United States Dollar",0.06730000,"2023-11-03 17:51:07","UTC")
                   """
executeCom.execute(first)

connectionInit.commit()
'''
res = executeCom.execute("SELECT * from Crypto")
print(res.fetchall())
#Now after executign the command, we will go back to the direcotry where the main file is
#going back
os.chdir(CWD)

if (sys.version_info.major < 3 and sys.version_info.minor < 10):
    loop = asyncio.get_event_loop()
else:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

asyncio.set_event_loop(loop)
'''
Since i have a bit of expirenec with crypto, i will begin with that
'''
Assets = ["BTC", "ETH", "BNB","XRP","SOL", "ADA", "DOGE"] #add more later

def init():
    server.listen()

def handleClient(conn, addr):
    print(f"New connection: {addr} connected on port {conn}")
    connected =True
    while connected:
        msg_length = conn.recv(HEADER).decode('utf-8')
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode('utf-8')
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"{addr} \t {msg}")
            conn.send("MSG received".encode('utf-8'))
    conn.close()

async def getStatus(code:int):
    assert (code == 200) #returns asertion error
async def getData(callback) -> None:
    print(f"Server starting on Port {PORT}")
    init() #call server to start here
    while True:
        for i in range(len(Assets)):
            #It is going to take time to fect data from the API, so use async
            r = requests.get(f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={Assets[i]}&to_currency=USD&apikey={APIKEY}')
            await callback(r.status_code)
            #load the json, first clean the response
            clean = json.loads(r.content)
            #print(clean)

            #Do not want such a long error/waring messaghing, so going to generate return a nice message for user and log error
            if(clean.Information == dailyLimitReached):
                #write to the log file we had
                logs.warning("Daily API usage reached")
        
        conn, addr = server.accept()
        thread = threading.Thread(target=handleClient,args=(conn,addr))
        thread.start()
        print(f"Active Connections: {threading.activeCount()-1}")

def signal_handeler(signal, frame):
    loop.stop()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handeler)


asyncio.ensure_future(getData(getStatus))
loop.run_forever()
connectionInit.close()
executeCom.close()