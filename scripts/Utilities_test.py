import unittest
import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(__file__))
import Utilities as utils
import Constants as c
import numpy as np

class TestStringMethods(unittest.TestCase):
    def test_format_PRED(self):
        fmtString = utils.format_PRED("25", .25)
        self.assertEqual(fmtString, "Pred - PRED (25): 25.00%")

    def test_format_perf_metric(self):
        label = "Model - R Squared"
        fmtString = utils.format_perf_metric(label, .25)
        self.assertEqual(fmtString, "Model - R Squared: 0.25")

    def test_isRegularVersion_returnTrue(self):
        series = {
          c.VERSION: ["v3.4.5.6", "v3.4.5-rc1", "v3.4"],
          c.T_MODULE: [9876, 6745, 3659]
          }
        df = pd.DataFrame(series)
        filtered_versions = utils.isRegularVersion(df)

        self.assertTrue(len(filtered_versions) == 2)

    def test_is_all_same(self):
        data = [1,1,1,1,1,1]
        df = pd.Series(data)

        result = utils.is_all_same(df)
        self.assertTrue(result)

    def test_percentage_nan(self):
        series = {
          c.VERSION: ["v3.4.5.6", "v3.4.5-rc1", "v3.4"],
          c.T_MODULE: [9876, 9876, np.nan]
          }
        df = pd.DataFrame(series)

        result = utils.percentage_nan(df)

        self.assertEqual(result, 0.167)

    def test_percentage_error_when_y_zero_and_ypred_isnt(self):
        y = 0
        y_pred = 2

        result = utils.percent_error(y, y_pred)

        self.assertEqual(result, 2)

    def test_percentage_error_when_y_and_ypred_0(self):
        y = 0
        y_pred = 0

        result = utils.percent_error(y, y_pred)

        self.assertEqual(result, 0)

    def test_percentage_error_when_y_and_ypred_different(self):
        y = 18
        y_pred = 9.8

        result = utils.percent_error(y, y_pred)

        self.assertEqual(result, 0.46)

    def test_create_percent_error_df(self):
         df = pd.DataFrame({ "y": [1093,0,18], "y_pred": [403,0,9.8] })

         y = df['y']
         y_pred = df['y_pred']

         result = utils.create_percent_error_df(y, y_pred)

         self.assertEqual(result[c.PERCENT_ERROR].values[0], 0.63)
         self.assertEqual(result[c.PERCENT_ERROR].values[1], 0)
         self.assertEqual(result[c.PERCENT_ERROR].values[2], 0.46)

    def test_make_contrib_forecast(self):
        prediction_months = 36
        team_size = 5

        result = utils.make_contrib_forecast(prediction_months, team_size)
        is_all_same = utils.is_all_same(pd.Series(result))

        self.assertEqual(len(result), 36)
        self.assertTrue(is_all_same)


if __name__ == '__main__':
    unittest.main()
