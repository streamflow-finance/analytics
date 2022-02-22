import time

from pycoingecko import CoinGeckoAPI
import json
import requests
import redis

import os


class Jobs:
    TOKEN_PRICES = 'TOKENS_PRICES'


def poll_tokens_prices(freq):
    cg = CoinGeckoAPI()
    while True:
        r = redis.Redis(host='localhost', port=6379)
        uq_mints = {}
        for dataset in ['contracts-community', 'contracts-streamflow']:
            data = json.loads(r.get(dataset))
            for stream, contract in data.get('data').items():
                mint = contract.get('mint')
                if uq_mints.get(mint) is None:
                    try:
                        token_data = cg.get_coin_info_from_contract_address_by_id('solana', mint)
                        print("fetching from cg")
                    except ValueError as e:
                        time.sleep(1)
                        continue
                    tickers = token_data.get('tickers')
                    for i in tickers:
                        if i.get('target') == 'USD' or i.get('target') == 'USDC' or i.get('target') == 'USDT':
                            uq_mints[mint] = i.get('last')
                    time.sleep(1)
        r.set('token-prices', json.dumps(uq_mints))
        print(f'iteration done at {time.time()}')
        time.sleep(freq)


if __name__ == '__main__':
    job = os.environ.get('JOB')
    freq = os.environ.get('POLL_FREQUENCY')
    poll_tokens_prices(int(freq))
    # if job == Jobs.TOKEN_PRICES:
    #     poll_tokens_prices()
    # else:
    #     raise ValueError(f"No job {job} options: {Jobs.TOKEN_META}, {Jobs.TOKEN_PRICES}")
