import socket
import sys
import argparse
import time
from graphite_mining import MiningCarbonClient, FlyPoolStats, MinerStats, ZCashRate


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Carbon mining client.")

    parser.add_argument("--carbon_server", type=str, required=True, help="carbon server host")
    parser.add_argument("--carbon_port", type=int, required=True, help="carbon server port")

    parser.add_argument("--wallet", type=str, required=True, help="zcash wallet")

    parser.add_argument("--miner_api_host", type=str, required=True, help="miner api host")
    parser.add_argument("--miner_api_port", type=int, required=True, help="miner api port")

    parser.add_argument("--delay", type=int, default=60, help="delay interval")

    args = parser.parse_args()

    client = MiningCarbonClient(args.delay)
    client.connect(args.carbon_server, args.carbon_port)

    client.addWorker(MinerStats("mining.gpu", args.miner_api_host, args.miner_api_port))
    client.addWorker(ZCashRate("mining.zcash"))
    client.addWorker(FlyPoolStats("mining.flypool_rewards", args.wallet))

    client.run()
