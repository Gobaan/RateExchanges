import pytest

import process


@pytest.fixture
def exchanges():
    import json
    import utilities
    import cryptocompare
    with open("sample_crawl.json") as fp:
        encoder = utilities.get_encoder(cryptocompare.Exchange, cryptocompare.Entry, cryptocompare.Trade)
        exchanges = json.load(fp, object_hook=encoder.decode)
        return [process.Exchange(name, exchange) for name, exchange in exchanges.items()]


@pytest.fixture
def frame(exchanges):
    return process.to_df(exchanges)


def test_pandas(frame):
    # TODO: Currently this and the python code don't agree
    # But I context switched to the graph approach, test this if you are to continue
    merged = frame.merge(frame, on=('src', 'dst'))
    merged['spread'] = merged.rate_x / merged.rate_y - 1
    top_spread = merged.groupby(('src', 'dst')).agg({'spread': max}).reset_index()
    top_spread = top_spread.sort_values(by='spread', ascending=False)
    ripple_spreads = top_spread[top_spread.dst == 'XRP'].iloc[0]
    assert ripple_spreads.spread == 0.062648263963769546


def test_pythonic(exchanges):
    rankings = process.get_ranks(exchanges)
    percents = process.calculate_spreads(rankings)
    assert percents[('BTC', 'XRP')][0] == (0.9410451547437849, 'C-CEX')


def test_graph_theory(frame):
    graph = process.to_coin_graph(frame)
    short_cycles = process.calculate_short_cycles(graph)
    process.graph_to_gephi(short_cycles, "positive.gexf")
    assert short_cycles.number_of_nodes() == 235
