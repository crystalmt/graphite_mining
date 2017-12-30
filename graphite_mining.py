import requests
import json
import socket

def getPoolStats(wallet_id):
    r = requests.get('http://api-zcash.flypool.org/miner/%s/currentStats' % (wallet_id,))
    return r.json()['data']

def getMinerStats(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send('%s\n' % (json.dumps({'id': 1, 'method': 'getstat'}),))
    data = json.loads(s.recv(1024))
    s.close()
    return data['result']

def getZCashRate():
    return requests.get('https://api.coinmarketcap.com/v1/ticker/zcash/?convert=USD').json()
