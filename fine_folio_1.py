def fine_folio_core(stocks_to_work):

    import pandas as pd
    import numpy as np
    import pandas_datareader as pdr
    import pandas_datareader.data as web
    import matplotlib.pyplot as plt
    import datetime as dt
    from pandas.plotting import register_matplotlib_converters

    register_matplotlib_converters()
    import statsmodels.api as sm
    from statsmodels.tsa.stattools import adfuller
    from statsmodels.tsa.stattools import pacf
    from statsmodels.tsa.stattools import acf
    from statsmodels.tsa.filters import bk_filter
    import arch
    from arch import arch_model
    from statsmodels.tsa.arima_model import ARIMA
    from statsmodels.graphics import tsaplots
    from statsmodels.graphics.tsaplots import plot_acf
    import csv

    df = pd.DataFrame(index=None, columns=None)
    asset_length_list = list()


    start = dt.datetime(2018, 1, 1)
    end = dt.datetime(2018, 12, 31)  # '2019-12-31'

    moex_list = list(
        ['NVTK', 'FEES', 'GAZP', 'TATN', 'MTSS', 'CHMF', 'UPRO', 'ENRU', 'RUAL', 'ALRS', 'SNGS',
         'BANE', 'AFKS', 'NLMK', 'HYDR', 'SBER', 'LKOH', 'VTBR', 'AFLT', 'ROSN', 'MAGN', 'GMKN', 'PLZL', 'SIBN',
         'POLY', 'IRAO', 'PHOR', 'MTLR', 'RTKM', 'TRMK'])

    short_list = list(['NVTK', 'SBER', 'FEES', 'AFLT'])
    blue_chips_moex = list(['GAZP', 'SBER', 'LKOH', 'GMKN', 'NVTK', 'TATN', 'ROSN', 'MGNT', 'MTSS',
    'VTBR', 'SNGS', 'ALRS', 'CHMF', 'MOEX', 'IRAO'])

    if stocks_to_work == 'blue_chips_moex':
        asset_list = blue_chips_moex
    elif stocks_to_work == 'moex_list':
        asset_list = moex_list
    else:
        print('something went wrong')

    for i in asset_list:

        asset = web.DataReader(i, 'moex', start=start, end=end)
        asset = asset.fillna(method='backfill')
        asset_r = asset['CLOSE'].pct_change(1)

        print("starting the process for {0}".format(i))


        # plt.plot(aflt_r)
        # plt.title('AFLT Returns First Difference')
        # plt.show()

        # Augmented Dickey-Fuller Test (ADF) Statistical Test

        # To determine if a time series is stationary or not, we will use the ADF test which is
        # a type of unit root test. Unit roots are a cause for non-stationarity,
        # the ADF test will test if unit root is present.
        # A time series is stationary if a single shift in time doesn’t change the time series
        # statistical properties, in which case unit root does not exist.
        # The Null and Alternate hypothesis of the Augmented Dickey-Fuller test is defined as follows:
        # - Null Hypothesis states there is the presence of a unit root.
        # - Alternate Hypothesis states there is no unit root. In other words, Stationarity exists.#

        # The Akaike Information Criterion (AIC) is used to determine the lag.

        # The adfuller function returns a tuple of statistics from the ADF test such as
        # the Test Statistic, P-Value, Number of Lags Used, Number of Observations
        # used for the ADF regression and a dictionary of Critical Values.

        # If the P-Value is less than the Significance Level defined,
        # we reject the Null Hypothesis that the time series contains a unit root.
        # In other words, by rejecting the Null hypothesis,
        # we can conclude that the time series is stationary.

        # If the P-Value is very close to your significance level,
        # you can use the Critical Values to help you reach
        # a conclusion regarding the stationarity of your time series.

        class StationarityTests:  # class stores stationarity results
            def __init__(self, significance=.05):
                self.SignificanceLevel = significance
                self.pValue = None
                self.isStationary = None

            def ADF_Stationarity_Test(self, timeseries, printResults=True):
                # Dickey-Fuller test:
                adfTest = adfuller(timeseries, autolag='AIC')

                self.pValue = adfTest[1]

                if (self.pValue < self.SignificanceLevel):
                    self.isStationary = True
                else:
                    self.isStationary = False

                if printResults:
                    dfResults = pd.Series(adfTest[0:4],
                                          index=['ADF Test Statistic', 'P-Value', '# Lags Used', '# Observations Used'])
                    # Add Critical Values
                    for key, value in adfTest[4].items():
                        dfResults['Critical Value (%s)' % key] = value
                    print('Augmented Dickey-Fuller Test Results:')
                    print(dfResults)


        sTest = StationarityTests()
        # sTest.ADF_Stationarity_Test(aflt_r, printResults = True)
        # print("Is the time series stationary? {0}".format(sTest.isStationary))

        asset_r = asset_r.rolling(window=3).mean()
        asset_r = asset_r.fillna(method='backfill')

        asset_r = np.log1p(asset_r)  # natural logarithm

        asset_r_c = sm.tsa.filters.bkfilter(asset_r, 2, 8, 3)  # why? need more details on that

        print('Below is the timeseries after applying Bakster-King filter')
        print(asset_r_c)

        # plt.plot(aflt_r_c)
        # plt.show()

        sTest.ADF_Stationarity_Test(asset_r, printResults=True)
        print("Is the time series stationary? {0}".format(sTest.isStationary))

        # At this moment we know our time series is stationary, so we could use
        # ARIMA-GARCH model and than predict next period return.

        asset_r_c.index = pd.DatetimeIndex(asset_r_c.index).to_period('D')
        # aflt_r_c_rescale = aflt_r_c*100

        pacf_asset = pacf(asset_r_c, nlags=40, method='ywunbiased', alpha=.05)
        # [0] is index to access partial autocorrelation, [1] accesses confidence interval
        for a in range(40):
            p_list = list(*np.where(pacf_asset[0][a] > pacf_asset[1][a][0] or pacf_asset[0][a] > pacf_asset[1][a][1]))

        p_pacf = max(p_list) + 1  # because there couldn't be a 0 lag I've added 1
        print(p_pacf)
        # optimal p_pacf index is the one after which pacf starts to be around 0

        acf_asset = acf(asset_r_c, unbiased=False, nlags=40, qstat=False, fft=None, alpha=.05, missing='none')
        for s in range(40):
            q_list = list(*np.where(acf_asset[0][s] > acf_asset[1][s][0] or acf_asset[0][s] > acf_asset[1][s][1]))

        q_acf = max(q_list) + 1  # because there couldn't be a 0 lag I've added 1
        print(q_acf)

        # tsaplots.plot_acf(acf_aflt)
        # plt.show()

        arima_model = ARIMA(asset_r_c, order=(p_pacf, 0, q_acf)).fit(method='mle', trend='nc')
        am = arch_model(asset_r_c, vol='Garch', p=1, o=0, q=1, dist='Normal', rescale=False)
        am = am.fit()
        mu_pred = arima_model.forecast()[0]
        et_pred = am.forecast(horizon=1).mean['h.1'].iloc[-1]

        next_return = mu_pred + et_pred
        print(next_return)

        next_return = pd.Series(next_return, index=asset_r_c.tail(1).index + 1)
        asset_r_c_forecast = asset_r_c.append(next_return, ignore_index=True)
        print(asset_r_c_forecast)
        length = len(asset_r_c_forecast)
        asset_length_list.append(length)
        # df=asset_r_c_forecast.to_frame().combine_first(df)
        df.reindex(asset_r_c.index)
        df = df.append(asset_r_c_forecast, ignore_index=True)

    print('finished loop')

    max_length = max(asset_length_list)

    asset_length_diff_list = [max_length - x for x in asset_length_list]

    print('this are the length of series {}'.format(asset_length_list), 'the max length {}'.format(max_length))

    new_df = pd.DataFrame(index=None, columns=None)

    for add in range(len(asset_list)):
        new_series = df.iloc[add, :].shift(periods=asset_length_diff_list[add])
        new_df = new_df.append(new_series, ignore_index=True)

    print(new_df)
    new_df = new_df.transpose()
    max_diff = max(asset_length_diff_list)
    new_df = new_df.iloc[max_diff:]
    new_df.columns = asset_list
    #new_df.to_csv(r'C:\Users\DCAPITAL\Documents\FM\result_2.csv', index=True, header=True)


    def get_ret_vol_sr(weights):
        weights = np.array(weights)
        ret = np.sum(new_df.mean() * weights) * 252
        vol = np.sqrt(np.dot(weights.T, np.dot(new_df.cov() * 252, weights)))
        sr = ret / vol
        return np.array([ret, vol, sr])


    from scipy.optimize import minimize


    # minimize negative Sharpe Ratio
    def neg_sharpe(weights):
        return get_ret_vol_sr(weights)[2] * -1


    # check allocation sums to 1
    def check_sum(weights):
        return np.sum(weights) - 1


    # create constraint variable
    cons = ({'type': 'eq', 'fun': check_sum})
    # create weight boundaries
    bounds = ((0.01,1),)*len(asset_list)

    # initial guess

    init_guess = list()
    init_guess_value = 1/len(asset_list)
    for i in range(len(asset_list)):
        init_guess.append([init_guess_value])
    print(init_guess)
    opt_results = minimize(neg_sharpe, init_guess, method='SLSQP', bounds=bounds, constraints=cons)

    optimal_weights = opt_results.x
    optimal_weights = pd.Series(optimal_weights, index=asset_list)
    optimal_weights = optimal_weights.round(decimals=2)
    print(get_ret_vol_sr(opt_results.x), optimal_weights)

    # plot the data
    # plt.figure(figsize=(12,8))
    # plt.scatter(vol_arr,ret_arr,c=sharpe_arr,cmap='plasma')
    # plt.colorbar(label='Sharpe Ratio')
    # plt.xlabel('Volatility')
    # plt.ylabel('Return')
    # plt.show()

    start_b = dt.datetime(2019, 1, 1)  # '2018-01-02'
    end_b = dt.datetime(2019, 12, 31)  # '2019-12-31'

    capital = 100000
    backtest_df = pd.DataFrame(index=None, columns=None)
    #backtest_df = pd.DataFrame(pd.np.empty((0, len(asset_list))))


    asset_b_length_list = list()
    year_dates = pd.date_range('2019-01-01', '2019-12-31', freq='D')
    #year_dates = year_dates.to_period()
    backtest_df = backtest_df.reindex(year_dates)

    for i, allo in zip(asset_list,optimal_weights):

        asset_b = web.DataReader(i, 'moex', start=start_b, end=end_b)
        #asset_b = asset_b.fillna(method='backfill')
        asset_b_r = asset_b['CLOSE'].pct_change(1)
        asset_b_r.index = pd.DatetimeIndex(asset_b_r.index)
        #asset_b_r = asset_b_r.fillna(method='backfill')
        asset_b_r = asset_b_r*allo*capital
        length = len(asset_b_r)
        asset_b_length_list.append(length)
        print(asset_b_length_list)
        asset_b_r = asset_b_r.to_frame()
        backtest_df = backtest_df.merge(asset_b_r, left_index=True, right_index=True, how='inner')
        #backtest_df = pd.concat([backtest_df, asset_b_r], axis=1, ignore_index=False)

    backtest_df.columns = asset_list
    backtest_df['Total'] = backtest_df[:1].sum(axis=1)
    for s in range(1,len(backtest_df)):
        backtest_df['Total'][s] = backtest_df.iloc[s].sum() + backtest_df['Total'][s-1]
    #backtest_df.to_csv(r'C:\Users\DCAPITAL\Documents\FM\backtest_2.csv', index=True, header=True)

    print(backtest_df)
    picture = backtest_df['Total'].plot(figsize=(10,8))
    #plt.show()
    return (optimal_weights)
