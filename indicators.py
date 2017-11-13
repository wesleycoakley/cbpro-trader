#
# indicators.py
# Mike Cardillo
#
# System for containing all technical indicators and processing associated data

import talib
import logging
import numpy as np
from decimal import Decimal


class IndicatorSubsystem:
    def __init__(self, period_list):
        self.logger = logging.getLogger('trader-logger')
        self.current_indicators = {}
        for period in period_list:
            self.current_indicators[period.name] = {}

    def recalculate_indicators(self, cur_period, order_book):
        total_periods = len(cur_period.candlesticks)
        if total_periods > 0:
            cur_bid = float(order_book.get_bid() + Decimal('0.01'))
            cur_ask = float(order_book.get_ask() - Decimal('0.01'))
            closing_prices = cur_period.get_closing_prices()
            closing_prices_bid = np.append(closing_prices, cur_bid)
            closing_prices_ask = np.append(closing_prices, cur_ask)
            closing_prices_close = np.append(closing_prices, cur_period.cur_candlestick.close)


            self.calculate_bbands(cur_period.name, closing_prices_close)
            self.calculate_macd(cur_period.name, closing_prices_close)

            self.current_indicators[cur_period.name]['close'] = cur_period.cur_candlestick.close
            self.current_indicators[cur_period.name]['total_periods'] = total_periods

            self.logger.debug("[INDICATORS %s] Periods: %d MACD: %f MACD_SIG: %f MACD_HIST: %f" %
                              (cur_period.name, self.current_indicators[cur_period.name]['total_periods'], self.current_indicators[cur_period.name]['macd'],
                               self.current_indicators[cur_period.name]['macd_sig'], self.current_indicators[cur_period.name]['macd_hist']))

    def calculate_bbands(self, period_name, close):
        upperband_1, middleband_1, lowerband_1 = talib.BBANDS(close, timeperiod=20, nbdevup=1, nbdevdn=1, matype=0)

        self.current_indicators[period_name]['bband_upper_1'] = upperband_1[-1]
        self.current_indicators[period_name]['bband_lower_1'] = lowerband_1[-1]

        upperband_2, middleband_2, lowerband_2 = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)

        self.current_indicators[period_name]['bband_upper_2'] = upperband_2[-1]
        self.current_indicators[period_name]['bband_lower_2'] = lowerband_2[-1]

    def calculate_macd(self, period_name, closing_prices):
        macd, macd_sig, macd_hist = talib.MACD(closing_prices, fastperiod=10,
                                               slowperiod=26, signalperiod=9)
        self.current_indicators[period_name]['macd'] = macd[-1]
        self.current_indicators[period_name]['macd_sig'] = macd_sig[-1]
        self.current_indicators[period_name]['macd_hist'] = macd_hist[-1]
        self.current_indicators[period_name]['macd_hist_diff'] = Decimal(macd_hist[-1]) - Decimal(macd_hist[-2])

    def calculate_vol_macd(self, period_name, volumes):
        macd, macd_sig, macd_hist = talib.MACD(volumes, fastperiod=50,
                                               slowperiod=200, signalperiod=14)
        self.current_indicators[period_name]['vol_macd'] = macd[-1]
        self.current_indicators[period_name]['vol_macd_sig'] = macd_sig[-1]
        self.current_indicators[period_name]['vol_macd_hist'] = macd_hist[-1]

    def calculate_avg_volume(self, period_name, volumes):
        avg_vol = talib.SMA(volumes, timeperiod=15)

        self.current_indicators[period_name]['avg_volume'] = avg_vol[-1]

    def calculate_obv(self, period_name, closing_prices, volumes, bid_or_ask):
        # cryptowat.ch does not include the first value in their OBV
        # calculation, we we won't either to provide parity
        obv = talib.OBV(closing_prices[1:], volumes[1:])
        obv_ema = talib.EMA(obv, timeperiod=21)

        self.current_indicators[period_name][bid_or_ask]['obv_ema'] = obv_ema[-1]
        self.current_indicators[period_name][bid_or_ask]['obv'] = obv[-1]

    def calculate_sar(self, period_name, highs, lows):
        sar = talib.SAR(highs, lows)

        self.current_indicators[period_name]['sar'] = sar[-1]

    def calculate_mfi(self, period_name, highs, lows, closing_prices, volumes):
        mfi = talib.MFI(highs, lows, closing_prices, volumes)

        self.current_indicators[period_name]['mfi'] = mfi[-1]
