import datetime
from cachetools.func import ttl_cache

from django.db.models import Sum, F, Q
from worth.utils import is_near_zero
from worth.dt import day_start_next_day
from accounts.models import Account
from markets.models import Ticker, NOT_FUTURES_EXCHANGES
from trades.models import Trade
from markets.utils import get_price


@ttl_cache(maxsize=1000, ttl=30)
def get_futures_pnl(d=None, a='MSRKIB'):
    a = Account.objects.get(name=a)

    qs = Trade.objects.values_list('ticker__ticker').filter(account=a).\
        filter(~Q(ticker__market__ib_exchange__in=NOT_FUTURES_EXCHANGES))

    if d is not None:
        dt = day_start_next_day(d)
        qs = qs.filter(dt__lt=dt)
    qs = qs.annotate(pos=Sum(F('q')),
                     qp=Sum(F('q') * F('p')),
                     c=Sum(F('commission')))
    result = []
    total = 0.0
    for ti, pos, qp, commission in qs:
        ticker = Ticker.objects.get(ticker=ti)
        market = ticker.market
        pos = int(pos)
        pnl = -qp
        if pos == 0:
            price = 0
        else:
            price = get_price(ticker, d)
            pnl += pos * price

        pnl *= market.cs
        pnl -= commission
        total += pnl
        result.append((ticker, pos, price, pnl))

    return result, total


def avg_open_price(account, ticker):
    if type(account) == str:
        account = Account.objects.get(name=account)

    if type(ticker) == str:
        ticker = Ticker.objects.get(ticker=ticker)

    pos = 0
    qp_sum = 0
    commissions = 0
    # Use LIFO
    qs = Trade.objects.filter(account=account, ticker=ticker).values_list('q', 'p', 'commission').order_by('dt')
    for q, p, c in qs:
        if is_near_zero(pos + q):
            qp_sum = 0
            pos = 0
            commissions = 0
        else:
            if q * pos < 0:
                qp_sum *= 1 - abs(q) / pos
                commissions -= c
            else:
                qp_sum += q * p
                commissions += c

            pos += q

    if is_near_zero(pos):
        avg_price = 0.0
    else:
        avg_price = (qp_sum - commissions) / pos

    return avg_price