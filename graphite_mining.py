import requests
import json
import socket
import time
import sys

class MiningCarbonClient(object):

    def __init__(self, delay=60):
        self.sock = socket.socket()
        self.delay = delay
        self.workers = {}

    def connect(self, host, port):
        try:
            self.sock.connect( (host, port) )
        except:
            print("Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?"
                    % { 'server': args.carbon_server, 'port':args.carbon_port })
            sys.exit(1)

    def addWorker(self, worker):
        if not self.workers.get(worker.name):
            self.workers[worker.name] = worker

    def run(self):
        while True:
            lines = [w.getResult() for w in self.workers.itervalues() if w.validate()]
            lines = [item for sublist in lines for item in sublist]
            message = '\n'.join(lines) + '\n'
            print("sending message\n")
            print('-' * 80)
            print(message)
            print()
            self.sock.sendall(message)
            time.sleep(self.delay)

class Worker(object):

    def __init__(self, name):
        self.name = name

    def getResult(self):
        return []

    def validate(self):
        pass

    def now(self):
        return int( time.time() )

class FlyPoolStats(Worker):

    def __init__(self, name, wallet_id):
        self.apiUrl = 'http://api-zcash.flypool.org/miner/%s/currentStats' % (wallet_id,)
        super(FlyPoolStats, self).__init__(name)

    def getResult(self):
        rewards = 0.
        r = requests.get(self.apiUrl)
        data = r.json()['data']
        rewards = (data['unpaid'] + data['unconfirmed']) / 100000000.
        return ["%s %f %d" % (self.name, rewards, self.now())]

    def validate(self):
        r = requests.get(self.apiUrl)
        return r.status_code == 200

class MinerStats(Worker):

    def __init__(self, name, host, port):
        self.connection_params = (host, port)
        super(MinerStats, self).__init__(name)

    def getResult(self):
        results = []
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self.connection_params)
        s.send('%s\n' % (json.dumps({'id': 1, 'method': 'getstat'}),))
        data = json.loads(s.recv(1024))["result"]
        s.close()
        for i in range(len(data)):
            results.append("mining.gpu_temp_%i %i %d" % (i, data[i]['temperature'], self.now()))
            results.append("mining.sols_%i %s %d" % (i, data[i]['speed_sps'], self.now()))
            results.append("mining.gpu_power_usage_%i %s %d" % (i,data[i]['gpu_power_usage'],self.now()))
        return results

    def validate(self):
        #TO-DO: Implement validate
        return True

class ZCashRate(Worker):

    def __init__(self, name):
        self.url = 'https://api.coinmarketcap.com/v1/ticker/zcash/?convert=USD'
        super(ZCashRate, self).__init__(name)

    def getResult(self):
        data = float(requests.get(self.url).json()[0]['price_usd'])
        return ["%s %f %d" % (self.name, data, self.now())]

    def validate(self):
        r = requests.get(self.url)
        return r.status_code == 200
