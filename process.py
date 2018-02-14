import collections
import math

import networkx
import pandas as pd


# Tasks: Unit tests for current code
#       Print a sorted list of the scores for every cycle
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
    """
    :param trades: Data frame containing all the trades for this coin
    :param penalty: Penalty paid for moving from one exchange to another
    :return Graph(Coin:Coin) mapping coins to their exchange rates
    Simplifies the graph by always trading at the best possible buy/sell spread.
    If we make the pessimistic assumption that the coin is never in the right exchange for the trade, we have to
    always pay a penalty fee to the miners to move our coin from one exchange to another.

    Example: src=bitcoin, dst=ethereum, highest=10, lowest=9
    Penalty is 10%
    If min_rate = 0.1 and max_rate is 0.2 then we want to sell this coin for 0.11/usd and buy this coin for 0.18/usd
    so sell rate is 0.11/usd and backwards rate is 5.55usd/coin.
    If min_Rate is 1.2 and max rate is 2.4 then we want to sell this coin for 1.32/usd and buy this coin for 2.16/usd
    so sell rate is 1.32/usd and backwards rate is 0.4629 usd/coin
    """
    graph = networkx.DiGraph()
    trades.reset_index()

    buy = trades.loc[trades.reset_index().groupby(['src', 'dst'])['rate'].idxmax()]
    sell = trades.loc[trades.reset_index().groupby(['src', 'dst'])['rate'].idxmin()]
    buy_penalty = math.log(1 - penalty)
    sell_penalty = math.log(1 + penalty)

    for _, row in buy.iterrows():
        order = {'penalized_rate': -math.log(row.rate) - buy_penalty,
                 'best_exchange': row.exchange_name,
                 'raw_rate': row.rate}
        graph.add_edge(row.src, row.dst, **order)

    for _, row in sell.iterrows():
        order = {'penalized_rate': math.log(row.rate) + sell_penalty,
                 'worst_exchange': row.name,
                 'raw_rate': row.rate}
        graph.add_edge(row.dst, row.src, **order)

    return graph


def calculate_short_cycles(coin_graph):
    """
    :param coin_graph: Graph(Coin:Coin)
    :return: Graph(Coin:Coin) only containing currency pairs that can be exchange for a direct profit against each other
    """
    new_graph = networkx.DiGraph()
    rates = networkx.get_edge_attributes(coin_graph, "penalized_rate")
    for (u, v) in rates:
        if rates[u, v] + rates[v, u] < 0:
            new_graph.add_edge(u, v, rate=rates[u, v])
    return new_graph


def to_exchange_graph(frame):
    """
    params: frame: DataFrame(name:Name of exchange, src:Coin base, dst:Coin target, rate:Exchange rate)
    returns: Graph((Exchange_coin):(Exchange_coin)) Graph storing the cost of converting a coin to either another
    coin, or to another exchange
    This graph simulates the exchange ecosystem perfectly, but has much more nodes, for now we have abandoned this code
    Basically allows exchanges to trade coins within themselves, and connects exchanges to each other using
    a penalty, simulating transfering from one wallet to another
    """
    # TODO: Once you connect the apis, this can have different buy/sell prices
    # TODO: ALERT APRIL 30, 2018 IF THIS CODE IS UNTOUCHED REMOVE IT
    graph = networkx.DiGraph()
    usd_bases = []
    merged_frame = frame.merge(frame, on=('src', 'dst'))
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
