import json

from app.trading212 import Trading212Client

client = Trading212Client()



def test_summary():

    summary = client.account_summary()

    assert "cash" in summary
    assert "totalValue" in summary

    res = json.dumps(summary, default=lambda o: o.__dict__)

    print(res)


def test_positions():

    positions = client.positions()

    assert isinstance(positions, list)
    res = json.dumps(positions, default=lambda o: o.__dict__)

    print(res)

def test_exchanges():
    exchanges = client.exchanges()
    assert isinstance(exchanges, list)
    res = json.dumps(exchanges, default=lambda o: o.__dict__)

    print(res)