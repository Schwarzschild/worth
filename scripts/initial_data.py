import re

from django.db import transaction
from project.utils import yyyymmdd2dt
from accounts.models import Account
from markets.models import Market, Ticker
from trades.models import Trade


@transaction.atomic
def add_accounts():
    data = [
        ['TDA', 'MSRK', 'TDA', '232-304102'],
        ['MSIRAIB', 'MS', 'IB', 'U4421888'],
        ['MSRKIB', 'MSRK', 'IB', 'U625895'],
        ['RKCSIRA2', 'RK', 'CS', '6624-0050'],
        ['TRP', 'RK', 'TRP', 'Plan ID 61475'],
        ['MSRKFidelity', 'MSRK', 'Fidelity', 'Z03-842406']
    ]
    for n, o, b, a in data:
        Account(name=n, owner=o, broker=b, broker_account=a).save()


@transaction.atomic
def add_markets():
    data = [
        ['_CASH_', 'Cash Account', '_CASH_', '_CASH_', 1, 0, 1, 1, 4],
        ['_NOCASH_', 'Placeholder for accounts  non cash accounts', '_CASH_', '_CASH_', 1, 0, 1, 1, 4],
        ['ZM', 'Zoom', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['BEVVF', 'Bee Vectoring ADR', 'SMART', 'STOCK', 1, 0, 1, 1, 4],
        ['NFLX', 'Netflix', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['BA', 'Boeing', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['TSLA', 'Tesla', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['PYPL', 'Paypal', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['AAPL', 'Apple', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['TWLO', 'Twilio', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['MNDT', 'Mandiant', 'SMART', 'STOCK', 1, 0, 1, 1, 4],
        ['AMKR', 'Amkor', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['DOCN', 'Digital Ocean', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['NVDA', 'Nvidia', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['OKTA', 'Okta', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['MSFT', 'Microsoft', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['CRM', 'Salesforce', 'ARCA', 'STOCK', 1, 0, 1, 1, 4],
        ['NG', 'Natural Gas Futures', 'CME', 'NYM', 10000, 2.36, 1, 1, 3],
        ['CL', 'Light Sweet Crude Oil Futures', 'CME', 'NYM', 1000, 2.36, 1, 1, 2],
        ['ES', 'E-Mini S&P 500 Futures', 'CME', 'CME', 50, 2.01, 1, 1, 2],
        ['KC', 'Coffee', 'NYBOT', 'NYB', 37500, 2.46, 1, 0.01, 4]
    ]
    for s, n, ie, ye, cs, c, ipf, ypf, pprec in data:
        Market(symbol=s, name=n, ib_exchange=ie, yahoo_exchange=ye, cs=cs, commission=c,
               ib_price_factor=ipf, yahoo_price_factor=ypf, pprec=pprec).save()

    data = [
        ['_CASH_', '_CASH_'],
        ['_NOCASH_', '_NOCASH_'],
        ['ZM', 'ZM'],
        ['BEVVF', 'BEVVF'],
        ['NFLX', 'NFLX'],
        ['BA', 'BA'],
        ['TSLA', 'TSLA'],
        ['PYPL', 'PYPL'],
        ['AAPL', 'AAPL'],
        ['TWLO', 'TWLO'],
        ['MNDT', 'MNDT'],
        ['AMKR', 'AMKR'],
        ['DOCN', 'DOCN'],
        ['NVDA', 'NVDA'],
        ['OKTA', 'OKTA'],
        ['MSFT', 'MSFT'],
        ['CRM', 'CRM'],
        ['NG', 'NGK2022'],
        ['ES', 'ESM2022'],
        ['KC', 'KCK2022'],
    ]

    for s, t in data:
        print(s)
        m = Market.objects.get(symbol=s)
        t = Ticker(ticker=t)
        t.market = m
        t.save()


def add_account(a):
    if Account.objects.filter(name=a).exists():
        account = Account.objects.get(name=a)
    else:
        account = Account(name=a, owner='MSRK', broker='', broker_account=a, description='')
        account.save()
    return account


def add_ticker(t):
    if Ticker.objects.filter(ticker=t).exists():
        ticker = Ticker.objects.get(ticker=t)
    else:
        m = Market(symbol=t, name=t)
        m.save()

        ticker = Ticker(ticker=t, market=m)
        ticker.save()

    return ticker


@transaction.atomic
def add_trades():
    # Remember that the old cash account is now ticker=_CASH_
    # If ca = "none" then use ticker = _NOCASH_
    cash = Ticker.objects.get(ticker='_CASH_')

    fn = '/Users/ms/data/trades.dat'
    with open(fn) as fh:
        lines = fh.readlines()
        for line in lines:
            line = re.sub(r'\!.*\n', r'\n', line)
            line = line.replace('\n', '')
            if not line:
                continue

            print(line)
            a, t, ca, d, r_f, q, p, c, c_f, note, junk = line.split('|')

            a = add_account(a)
            if t == 'Cash':
                t = cash
            else:
                t = add_ticker(t)

            dt = yyyymmdd2dt(d)

            r_f = r_f == '1'

            q = float(q)
            p = float(p)
            if c == '':
                c = 0.0
            else:
                c = float(c)

            if ca == 'none':
                if note:
                    note += ''
                note += 'ca=none'

            trade = Trade(dt=dt, account=a, ticker=t, reinvest=r_f, q=q, p=p, commission=c, note=note)
            trade.save()


# add_accounts()
# add_markets()
# add_trades()
