from datetime import datetime
import json
from django.db.models import Sum, Max, F
from django.conf import settings
from collections import defaultdict

from worth.utils import cround
from trades.models import Trade
from accounts.models import CashRecord, Account
from markets.models import Ticker
from worth.utils import is_near_zero, set_tz
from markets.utils import get_price
from markets.tbgyahoo import yahooQuote, yahoo_url
from analytics.models import PPMResult


def get_balances(account=None, ticker=None):
    # balances[<account>]->[<ticker>]-><qty>
    balances = defaultdict(lambda: defaultdict(lambda: 0.0))

    qs = Trade.equity_trades(account, ticker)

    cash_f = (ticker is not None) and (ticker == 'CASH')

    qs = qs.values_list('account__name', 'ticker__ticker', 'reinvest', 'q', 'p', 'commission')
    for a, ti, reinvest, q, p, c in qs:
        portfolio = balances[a]

        if not reinvest:
            cash_amount = -q * p - c
            portfolio['CASH'] += cash_amount

        if not cash_f:
            portfolio[ti] += q

    qs = CashRecord.objects
    if account is not None:
        qs = qs.filter(account__name=account)

    qs = qs.values('account__name').order_by('account__name').annotate(total=Sum('amt'))
    for result in qs:
        total = result['total']
        if abs(total) < 0.001:
            continue
        a = result['account__name']
        balances[a]['CASH'] += total

    empty_accounts = [a for a in balances if abs(balances[a]['CASH']) < 0.001]
    for a in empty_accounts:
        del balances[a]['CASH']
        if len(balances[a].keys()) == 0:
            del balances[a]

    # Scale results for demo purposes.  PPM_FACTOR defaults to False.
    factor = settings.PPM_FACTOR
    if factor is not False:
        for k, v in balances.items():
            for j in v.keys():
                v[j] *= factor

    return balances


def get_futures_balances(account=None, ticker=None):
    # result[<ticker>]=[<position>, <pnl>, <current_price>]
    result = defaultdict(lambda: [0.0, 0.0])
    # sums[<ticker>]->[<sum q>, <sum q*p>, <sum c>]
    sums = defaultdict(lambda: [0.0, 0.0, 0.0])

    qs = Trade.futures_trades(account, ticker)
    qs = qs.values_list('ticker__ticker', 'q', 'p', 'commission', 'ticker__market__ib_price_factor')
    for ti, q, p, c, f in qs:
        s = sums[ti]
        s[0] += q
        s[1] += q * p * f
        s[2] += c

    for ti in sums:
        position, pnl, c_sum = sums[ti]

        ticker = Ticker.objects.get(ticker=ti)
        pnl *= ticker.market.ib_price_factor

        if not is_near_zero(position):
            p = get_price(ticker)
            pnl += -position * p
        else:
            p = ''

        pnl *= -ticker.market.cs
        pnl -= c_sum

        result[ti] = [position, pnl, p]

    return result


def get_futures_pnl():
    a = Account.objects.get(name='FUTURES')
    # dt = set_tz(datetime(2022, 2, 15, 0, 0, 0))

    qs = Trade.objects.values_list('ticker__ticker').filter(account=a)
    # qs = qs.filter(dt__gt=dt)
    qs = qs.annotate(pos=Sum(F('q')),
                     qp=Sum(F('q') * F('p')),
                     c=Sum(F('commission')))
    result = []
    total = 0.0
    for ti, pos, qp, commission in qs:
        ticker = Ticker.objects.get(ticker=ti)
        market = ticker.market
        pos = int(pos)
        pnl = -qp * market.ib_price_factor
        if pos == 0:
            price = 0
        else:
            price = get_price(ticker)
            pnl += pos * price

        pnl *= market.cs
        pnl -= commission
        total += pnl
        result.append((ticker.ticker, pos, price, pnl))

    return result, total


def valuations(account=None, ticker=None):
    formats = json.dumps({'columnDefs': [{'targets': [2, 3, 4], 'className': 'dt-body-right'}],
                          # 'ordering': False
                          })

    headings = ['Account', 'Ticker', 'Q', 'P', 'Value']
    data = []
    balances = get_balances(account, ticker)

    total_worth = 0
    for a in balances.keys():
        portfolio = balances[a]
        for ticker in portfolio.keys():
            t = Ticker.objects.get(ticker=ticker)
            q = portfolio[ticker]
            if is_near_zero(q):
                continue

            p = get_price(t)
            value = q * p
            total_worth += value

            qstr = cround(q, 3)
            pstr = cround(p, t.market.pprec)
            vstr = cround(value, 3)

            if ticker == 'CASH':
                url = 'CASH'
            else:
                url = yahoo_url(t)

            data.append([a, url, qstr, pstr, vstr])

    futures_balances = get_futures_balances()
    for ticker in futures_balances:
        t = Ticker.objects.get(ticker=ticker)
        position, pnl, p = futures_balances[ticker]
        total_worth += pnl
        qstr = cround(position, 3)
        pstr = cround(p, t.market.pprec)
        vstr = cround(pnl, 3)
        data.append(['FUTURES', yahoo_url(t), qstr, pstr, vstr])

    data.append(['AAA Total', '', '', '', cround(total_worth, 3)])

    PPMResult.objects.create(value=total_worth)

    return headings, data, formats
