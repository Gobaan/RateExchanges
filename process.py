import collections
import json
import math

import networkx
import pandas as pd

import cryptocompare
import utilities


class Exchange(object):
    def __init__(self, name, exchange):
        self.name = name
        self.rates = {}
        self.update(exchange)

    def update(self, exchange):
        if 'www.cryptocompare.com' not in exchange:
            return

        # TODO: Remove retarded values
        # TODO: Filter out bad exchanges
        for entry in exchange['www.cryptocompare.com'].entries:
            for trade in entry.trades:
                if trade[0] == ['BTC', 'USD']:
                    print(self.name, trade)
                self.rates[tuple(trade[0])] = trade[1]


def get_ranks(exchanges):
    rankings = collections.defaultdict(list)

    for exchange in exchanges:
        for pair in exchange.rates:
            rankings[pair] += [(exchange.rates[pair], exchange.name)]

    for pair in rankings:
        rankings[pair] = sorted(rankings[pair])

    return rankings


def calculate_spreads(rankings):
    # TODO: For every coin calculate the maxiumum spread
    percents = {}
    for pair in rankings:
        best = rankings[pair][-1][0]
        percents[pair] = [(rate[0] / best, rate[1]) for rate in rankings[pair]]

    return percents


def to_df(exchanges):
    rows = [(exchange.name, pair[0], pair[1], exchange.rates[pair])
            for exchange in exchanges
            for pair in exchange.rates]
    return pd.DataFrame(rows, columns=('exchange_name', 'src', 'dst', 'rate'))


def to_coin_graph(trades, penalty=0.01):
    """ Example: src=bitcoin, dst=ethereum, highest=10, lowest=9"""
    """ There may be an intermediate path that goes through a poor trade but leads to a good trade"""
    graph = networkx.DiGraph()
    trades.reset_index()
    buy = trades.loc[trades.reset_index().groupby(['src', 'dst'])['rate'].idxmax()]
    sell = trades.loc[trades.reset_index().groupby(['src', 'dst'])['rate'].idxmin()]
    for _, row in buy.iterrows():
        order = {'best_rate': float(-math.log(row.rate * (1 - penalty))), 'best_exchange': row.exchange_name}
        graph.add_edge(row.src, row.dst, **order)

    # every pair only exists once, so we flip the destination and source and the rate
    for _, row in sell.iterrows():
        order = {'worst_rate': float(-math.log(1 / row.rate * (1 + penalty))), 'worst_exchange': row.name}
        graph.add_edge(row.dst, row.src, **order)

    return graph


# TODO: Verify coin_graph isn't spitting out garbage

def to_graph(merged_frame):
    # Add all the pairs and their exchange rate to the graph
    # TODO: currently this is undirected because of the cryptocompare data
    # TODO: Once you connect the apis, this can have different buy/sell prices
    graph = networkx.Graph()
    usd_bases = []
    for index, row in merged_frame.iterrows():
        dst = f"{row.name_x}_{row.dst}"
        src = f"{row.name_x}_{row.src}"
        if row.dst == 'BTC':
            usd_bases += [dst]

        other_dst = f"{row.name_y}_{row.dst}"
        other_src = f"{row.name_y}_{row.src}"

        graph.add_edge(src, dst, rate=-math.log(row.rate_x))
        graph.add_edge(src, other_src, rate=0)
        graph.add_edge(dst, other_dst, rate=0)

    return graph, list(set(usd_bases))


def graph_to_gephi(graph, fname='default.gexf'):
    with open(fname, 'wb') as fp:
        networkx.write_gexf(graph, fp)


if __name__ == '__main__':
    # Task:
    # I wish find the best two exchanges to put my money such that I can buy coin C1 from exchange E1
    # Transfer Coin C1 to E2, sell Coin C1 for C2, Transfer Coin C2 Back To E1 and repurchase C1
    # Notes: within an exchange am I willing to do intermediate trades?

    # Arbitrage graph?

    with open("spread.json") as fp:
        encoder = utilities.get_encoder(cryptocompare.Exchange, cryptocompare.Entry, cryptocompare.Trade)
        exchanges = json.load(fp, object_hook=encoder.decode)
        processed_exchanges = [Exchange(name, exchange) for name, exchange in exchanges.items()]
        rankings = get_ranks(processed_exchanges)
        percents = calculate_spreads(rankings)

        frame = to_df(processed_exchanges)
        merged = frame.merge(frame, on=('src', 'dst'))
        merged['spread'] = merged.rate_x / merged.rate_y - 1
        top_spread = merged.sort_values(by='spread')
        graph = to_coin_graph(frame)
        print(graph.number_of_nodes())
        print(graph.number_of_edges())
        graph_to_gephi(graph)
