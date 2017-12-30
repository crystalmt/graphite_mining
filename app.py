import socket
import sys
import time
from graphite_mining import getMinerStats, getPoolStats, getZCashRate

CARBON_SERVER = '127.0.0.1'
CARBON_PORT = 2003

MINER_API_HOST = '127.0.0.1'
MINER_API_PORT = 42000

WALLET_ID = ""

DELAY = 60

if __name__ == "__main__":
    sock = socket.socket()

    try:
        sock.connect( (CARBON_SERVER, CARBON_PORT) )
    except:
        print("Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server': CARBON_SERVER, 'port':CARBON_PORT })
        sys.exit(1)

    while True:
        now = int( time.time() )
        lines = []

        minerStats = getMinerStats(MINER_API_HOST, MINER_API_PORT)
        poolStats = getPoolStats(WALLET_ID)
        zcashRate = getZCashRate()

        zcashUSD = float(zcashRate[0]['price_usd'])
        rewards = (poolStats['unpaid'] + poolStats['unconfirmed']) / 100000000.

        for i in range(len(minerStats)):
            lines.append("mining.gpu_temp_%i %i %d" %
                    (i,minerStats[0]['temperature'],now))
            lines.append("mining.sols_%i %s %d" %
                    (i,minerStats[0]['speed_sps'],now))
            lines.append("mining.gpu_power_usage_%i %s %d" %
                    (i,minerStats[0]['gpu_power_usage'],now))
        lines.append("mining.flypool_rewards %f %d" % (rewards,now))
        lines.append("mining.zcash %f %d" % (zcashUSD,now))
        message = '\n'.join(lines) + '\n' #all lines must end in a newline
        print("sending message\n")
        print('-' * 80)
        print(message)
        print()
        sock.sendall(message)
        time.sleep(DELAY)
