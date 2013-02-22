"""
Convert raw transaction CSV data into candlestick CSV data

Input CSV data should be in the format returned by the bitcoincharts API

"""
from __future__ import division
import argparse
import sys
import csv
import datetime
import decimal


class Candle(object):
    """Represents a single time interval"""

    def __init__(self, length):
        self._begin_time = None
        self._first_transaction_time = None
        self._last_transaction_time = None
        self._length = length
        self._open = decimal.Decimal(0)
        self._high = decimal.Decimal(0)
        self._low = decimal.Decimal(0)
        self._close = decimal.Decimal(0)
        self._btc_volume = decimal.Decimal(0)
        self._fiat_volume = decimal.Decimal(0)

    @property
    def begin_time(self):
        return self._begin_time

    @property
    def end_time(self):
        return self._begin_time + self._length

    @property
    def csv_output(self):
        epoch_start = datetime.datetime.utcfromtimestamp(0)
        begin_seconds = (self._begin_time - epoch_start).total_seconds(),
        return {
                'begin_time': int(begin_seconds[0]),    # Why is this a tuple?
                'length': int(self._length.total_seconds()),
                'open': self._open,
                'high': self._high,
                'low': self._low,
                'close': self._close,
                'btc_volume': self._btc_volume,
                'fiat_volume': self._fiat_volume,
                }

    def add_transaction(self, transaction):
        transaction_time = datetime.datetime.utcfromtimestamp(int(transaction['unixtime']))
        price = decimal.Decimal(transaction['price'])
        if self._begin_time is None:
            epoch_start = datetime.datetime.utcfromtimestamp(0)
            transaction_delta = transaction_time - epoch_start
            periods = int(transaction_delta.total_seconds()) // int(period_length.total_seconds())
            self._begin_time = epoch_start + period_length * periods
        if self._first_transaction_time is None:
            self._first_transaction_time = transaction_time
            self._open = price
            self._low = price
        if price > self._high:
            self._high = price
        if price < self._low:
            self._low = price
        self._last_transaction_time = transaction_time
        self._close = price
        self._btc_volume += decimal.Decimal(transaction['amount'])
        self._fiat_volume += decimal.Decimal(transaction['amount']) * price

    def get_next_candle(self):
        next_candle = Candle(self._length)
        next_candle._begin_time = self.end_time
        next_candle._open = self._close
        next_candle._high = self._close
        next_candle._low = self._close
        next_candle._close = self._close
        return next_candle


parser = argparse.ArgumentParser(
        description="Convert raw transaction CSV data into candlestick CSV data",
        )
parser.add_argument(
    '-t', '--time-period',
    choices=['hourly', 'daily', 'weekly'],
    default='daily',
    help="Time period per candlestick",
    )
parser.add_argument(
    'input_file',
    nargs='?',
    default=sys.stdin,
    type=argparse.FileType('r'),
    help="CSV file containing raw transaction data",
    )
parser.add_argument(
    'output_file',
    nargs='?',
    default=sys.stdout,
    type=argparse.FileType('w'),
    help="Filename for candlestick CSV output",
    )
args = parser.parse_args()

transactions = csv.DictReader(
        args.input_file,
        fieldnames=['unixtime', 'price', 'amount'],
        )
candles = csv.DictWriter(
        args.output_file,
        fieldnames=[
            'begin_time',
            'length',
            'open',
            'high',
            'low',
            'close',
            'btc_volume',
            'fiat_volume',
            ],
        )

period_length = None
if args.time_period == 'hourly':
    period_length = datetime.timedelta(hours=1)
elif args.time_period == 'daily':
    period_length = datetime.timedelta(days=1)
elif args.time_period == 'weekly':
    period_length = datetime.timedelta(weeks=1)

candles.writeheader()
candle = None
for transaction in transactions:
    transaction_time = datetime.datetime.utcfromtimestamp(int(transaction['unixtime']))
    if candle is None:
        candle = Candle(period_length)
    else:
        while transaction_time >= candle.end_time:
            candles.writerow(candle.csv_output)
            candle = candle.get_next_candle()
    candle.add_transaction(transaction)
candles.writerow(candle.csv_output)
