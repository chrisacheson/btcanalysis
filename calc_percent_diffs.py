"""
Calculate percent changes from candlestick CSV data

Input CSV data should be in the format returned by raw_to_candles.py

"""
from __future__ import division
import argparse
import sys
import csv
import decimal


def percent_diff(a, b, decimal_places=2):
    """Calculate b - a as a percentage of a"""
    if a == 0:
        return 0
    else:
        return round((b - a) * 100 / a, decimal_places)


parser = argparse.ArgumentParser(
        description="Calculate percent changes from candlestick CSV data",
        )
parser.add_argument(
    'input_file',
    nargs='?',
    default=sys.stdin,
    type=argparse.FileType('r'),
    help="CSV file containing candlestick data",
    )
parser.add_argument(
    'output_file',
    nargs='?',
    default=sys.stdout,
    type=argparse.FileType('w'),
    help="Filename for percent diff CSV output",
    )
args = parser.parse_args()

candles = csv.DictReader(args.input_file)
diffs = csv.DictWriter(
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

diffs.writeheader()
previous_candle = None
for candle in candles:
    if previous_candle is not None:
        diff = {}
        diff['begin_time'] = candle['begin_time']
        diff['length'] = candle['length']

        previous_open = decimal.Decimal(previous_candle['open'])
        current_open = decimal.Decimal(candle['open'])
        diff['open'] = percent_diff(previous_open, current_open)

        previous_high = decimal.Decimal(previous_candle['high'])
        current_high = decimal.Decimal(candle['high'])
        diff['high'] = percent_diff(previous_high, current_high)

        previous_low = decimal.Decimal(previous_candle['low'])
        current_low = decimal.Decimal(candle['low'])
        diff['low'] = percent_diff(previous_low, current_low)

        previous_close = decimal.Decimal(previous_candle['close'])
        current_close = decimal.Decimal(candle['close'])
        diff['close'] = percent_diff(previous_close, current_close)

        previous_btc_vol = decimal.Decimal(previous_candle['btc_volume'])
        current_btc_vol = decimal.Decimal(candle['btc_volume'])
        diff['btc_volume'] = percent_diff(previous_btc_vol, current_btc_vol)

        previous_fiat_vol = decimal.Decimal(previous_candle['fiat_volume'])
        current_fiat_vol = decimal.Decimal(candle['fiat_volume'])
        diff['fiat_volume'] = percent_diff(previous_fiat_vol, current_fiat_vol)

        diffs.writerow(diff)
    previous_candle = candle
