import socket
import sys
import time
import argparse
from graphite_mining import getMinerStats, getPoolStats, getZCashRate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Carbon mining client.")

    parser.add_argument("--carbon_server", type=str, required=True, help="carbon server host")
    parser.add_argument("--carbon_port", type=int, required=True, help="carbon server port")

    parser.add_argument("--wallet", type=str, required=True, help="zcash wallet")

    parser.add_argument("--miner_api_host", type=str, required=True, help="miner api host")
    parser.add_argument("--miner_api_port", type=int, required=True, help="miner api port")

    parser.add_argument("--delay", type=int, default=60, help="delay interval")

    args = parser.parse_args()

    sock = socket.socket()

    try:
        sock.connect( (args.carbon_server, args.carbon_port) )
    except:
        print("Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server': args.carbon_server, 'port':args.carbon_port })
        sys.exit(1)

    while True:
        now = int( time.time() )
        lines = []

        minerStats = getMinerStats(args.miner_api_host, args.miner_api_port)
        poolStats = getPoolStats(args.wallet)
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
        time.sleep(args.delay)
