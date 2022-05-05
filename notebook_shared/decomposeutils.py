import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytz
from pandas.plotting import autocorrelation_plot
from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import adfuller, kpss


def get_timezone(dataset, provider, region):
    timezones = dataset[(dataset['provider'] == provider) & (
        dataset['region'] == region)]['timezone'].unique()

    if (len(timezones)) != 1:
        print(timezones)
        raise ValueError()
    timezone = timezones[0]
    return timezone


def plot_decompose(decomposed_data, timezone,
                   start=None, end=None,
                   figsize=(20, 8), dtfmt='%d/%m',
                   xtickstepsize=2, xticksrotation=45):

    with plt.rc_context():
        plt.rc("figure", figsize=figsize)

        fig, axis = plt.subplots(figsize=(24, 10), sharex=True, nrows=4, gridspec_kw={
                                 'height_ratios': [1, 1, 2, 2]})

        # Set xlims when not set:
        if (start is None) or (start is not None and type(start) is not str):
            start = int(
                decomposed_data.observed.index.min().timestamp() / 24 / 60 / 60)
        else:
            start = int(pd.Timestamp(start).timestamp() / 24 / 60 / 60)

        if (end is None) or (end is not None and type(end) is not str):
            end = int(decomposed_data.observed.index.max(
            ).timestamp() / 24 / 60 / 60)
        else:
            end = int(pd.Timestamp(end).timestamp() / 24 / 60 / 60)

        # Plot Components
        axis[0].plot(decomposed_data.observed)
        plt.setp(axis[0], ylabel='Observed')

        axis[1].plot(decomposed_data.resid)
        plt.setp(axis[1], ylabel='Residuals')

        axis[2].plot(decomposed_data.trend)
        plt.setp(axis[2], ylabel='Trend')

        axis[3].plot(decomposed_data.seasonal)
        plt.setp(axis[3], ylabel='Seasonal')

        hours = mdates.HourLocator(interval=12)  # or use interval
        hours.MAXTICKS = 3392

        h_fmt = mdates.DateFormatter(dtfmt, tz=pytz.timezone(timezone))

        for ax in axis:
            ax.set_xlim(start, end)
            ax.xaxis.set_major_locator(hours)
            ax.xaxis.set_major_formatter(h_fmt)
            ax.xaxis.set_ticks(np.arange(start, end, xtickstepsize))
            ax.xaxis_date(tz=timezone)

        fig.autofmt_xdate()
        plt.xticks(rotation=xticksrotation)
        fig.tight_layout()
        return fig


def analyse_adf(test, level=0.01):

    tab = {
        "test statistic": test[3].adfstat,
        "p value": test[1],
        "used lag": test[3].usedlag,
        "nobs": test[3].nobs,
        "critical value  1%": test[3].critvalues['1%'],
        "critical value  5%": test[3].critvalues['5%'],
        "critical value 10%": test[3].critvalues['10%'],
    }

    test_as_str = "----Augmented Dickey-Fuller unit root test for unit root - Test Results----\n"
    h0_rejected = False
    if test[0] < test[3].critvalues['1%'] and level >= 0.01:
        test_as_str += 'H0 can be rejected with 1% confidence.\n'
        test_as_str += f'-> {test[3].HA} -> stationary, there is no unit root, not time-dependent \n'
        h0_rejected = True
    elif test[0] < test[3].critvalues['5%'] and level >= 0.05:
        test_as_str += 'H0 can be rejected with 5% confidence.\n'
        test_as_str += f'-> {test[3].HA} -> stationary, there is no unit root, not time-dependent \n'
        h0_rejected = True
    else:
        test_as_str += 'H0 cannot be rejected.\n'
        test_as_str += f'-> {test[3].H0} -> non-stationary, there is a unit root, time-dependent \n'

    for k, v in tab.items():
        test_as_str += "{:<20} {:<15}\n".format(k, v)
    return {"h0_rejected": h0_rejected, "text": test_as_str, "data": tab}


def analyse_kpss(test, level=0.01):

    tab = {
        "test statistic":  test[0],
        "p value": test[1],
        "used lag": test[3].lags,
        "nobs": test[3].nobs,
        "critical value  1%": test[2]['1%'],
        "critical value  5%": test[2]['5%'],
        "critical value 10%": test[2]['10%'],
    }

    test_as_str = "----Kwiatkowski-Phillips-Schmidt-Shin test for stationarity - Test Results----\n"
    h0_rejected = False
    if test[0] < test[2]['1%'] and level >= 0.01:
        test_as_str += 'H0 can be rejected with 1% confidence.\n'
        test_as_str += f'-> {test[3].HA} -> time-dependent \n'
        h0_rejected = True
    elif test[0] < test[2]['5%'] and level >= 0.05:
        test_as_str += 'H0 can be rejected with 5% confidence.\n'
        test_as_str += f'-> {test[3].HA} -> time-dependent \n'
        h0_rejected = True
    else:
        test_as_str += 'H0 cannot be rejected.\n'
        test_as_str += f'-> {test[3].H0} -> not time-dependent \n'

    for k, v in tab.items():
        test_as_str += "{:<20} {:<15}\n".format(k, v)
    return {"h0_rejected": h0_rejected, "text": test_as_str, "data": tab}


def stats_test(df, adflag=None, test_regression='ct'):

    case_desc = {
        "case_1": "Case 1: Both tests conclude that the series is not stationary - The series is not stationary",
        "case_2": "Case 2: Both tests conclude that the series is stationary - The series is stationary",
        "case_3": "Case 3: KPSS indicates stationarity and ADF indicates non-stationarity - The series is trend stationary. Trend needs to be removed to make series strict stationary. The detrended series is checked for stationarity.",
        "case_4": "Case 4: KPSS indicates non-stationarity and ADF indicates stationarity - The series is difference stationary. Differencing is to be used to make series stationary. The differenced series is checked for stationarity."
    }

    # Check If Adfuller autolag is set to None, then use specific lags:
    if adflag is None:
        adf_autolag = 'AIC'
        adf_maxlag = None
        kpss_nlags = 'auto'
    else:
        adf_autolag = None
        adf_maxlag = adflag
        kpss_nlags = adflag

    # Apply Ad
    test_adfuller = adfuller(df, regression=test_regression,
                             maxlag=adf_maxlag, autolag=adf_autolag, store=True)
    test_kpss = kpss(df, regression=test_regression,
                     nlags=kpss_nlags, store=True)

    adf_result = analyse_adf(test_adfuller)
    kpss_result = analyse_kpss(test_kpss)

    # Interfere cases:
    if (adf_result['h0_rejected'] == False and kpss_result['h0_rejected'] == True):
        case = 'case_1'

    elif (adf_result['h0_rejected'] == True and kpss_result['h0_rejected'] == False):
        case = 'case_2'

    elif (adf_result['h0_rejected'] == False and kpss_result['h0_rejected'] == False):
        case = 'case_3'

    elif (adf_result['h0_rejected'] == True and kpss_result['h0_rejected'] == True):
        case = 'case_4'
    else:
        raise Exception("Raise Impossible Error")

    # TODO check if residulas need to be used -> possibly yes
    fig_corr, ax = plt.subplots(figsize=(16, 6), sharex=True, ncols=1)
    autocorrelation_plot(df, ax=ax)

    fig_dist, axes = plt.subplots(figsize=(16, 6), sharex=True, ncols=2)
    df.plot.density(ax=axes[0])
    df.plot.hist(ax=axes[1])

    fig_dist.tight_layout()
    return {"adfuller": {'test': test_adfuller, "result": adf_result},
            "kpss": {'test': test_kpss, "result": kpss_result},
            "case": case, "case_desc": case_desc[case], "fig_dist": fig_dist, "fig_corr": fig_corr}


def seasonal_analysis(seasonal_df, dt_rounding, provider, region, timezone):

    fig, ax = plt.subplots(figsize=(10, 6), sharex=True, nrows=1)
    sdf = pd.DataFrame(seasonal_df)

    if dt_rounding == "30min":
        strftime = 'H:%M'

    if dt_rounding == "H":
        strftime = 'H'

    if dt_rounding == "D":
        strftime = 'w'

    sdf['hist'] = sdf.index.tz_localize('UTC').tz_convert(
        timezone).strftime(f"%{strftime}")

    if (strftime == "w"):
        sdf['hist'] = sdf['hist'].replace('0', '7')

    sdf.boxplot('season', by='hist', showfliers=False, ax=ax)

    if (strftime == "w"):
        ax.set_xticklabels(['Monday', 'Tuesday', 'Wednesday',
                           'Thursday', 'Friday', 'Saturday', 'Sunday'])

    if strftime == "H:%M":
        ax.tick_params(axis='x', labelrotation=45)

    # Plot Median Line Across Boxplots
    x = sdf.groupby(by='hist').quantile(0.5).values
    x = np.insert(x, 0, np.nan)
    ax.plot(x, 'r--', alpha=0.5)

    # Remove Titles
    fig.suptitle('')
    ax.set_title('')
    ax.set_xlabel('')

    fig.tight_layout()
    return {"fig": fig, "data": sdf}


def decompose(dataset, provider, region, decompose_col, dt_rounding,
              start=None, end=None,
              adflag=None, test_regression='ct',  # Stats Test parameters
              dtfmt='%a %d/%m', xtickstepsize=2, xticksrotation=45,
              plotstart=None, plotend=None, statsTest = True, agg='mean'):

    # Slice data for decomposition
    if (start is None) or (start is not None and type(start) is not str):
        startts = dataset['driver_invocation'].min()
    else:
        startts = pd.Timestamp(start)
    if (end is None) or (end is not None and type(end) is not str):
        endts = dataset['driver_invocation'].max()
    else:
        endts = pd.Timestamp(end)

    if dt_rounding not in ['30min', 'H', 'D']:
        raise ValueError('passed dt_rounding is illegal!')

    if agg not in ['median', 'mean']:
        raise ValueError('passed agg is illegal!')

    # Filter based on slice + round to given dt_rounding size (e.g., per hour etc.)
    selected_df = dataset[dataset['driver_invocation'].between(
        startts, endts, inclusive='both')]
    df_providerregion = selected_df[(selected_df['provider'] == provider) & (
        selected_df['region'] == region)]
    df_providerregion.insert(0, "driver_invocation_rounded",
                             df_providerregion['driver_invocation'].dt.round(dt_rounding))
    if agg == 'median':
        df_agg = df_providerregion.groupby(['driver_invocation_rounded'])[[decompose_col]].median()
    else:
        df_agg = df_providerregion.groupby(['driver_invocation_rounded'])[[decompose_col]].mean()

    # Hint: asfreq adds records for gaps -> we fill those with means.
    # TODO, asfreq changes granularity
    df_agg = df_agg.asfreq(dt_rounding)
    # Fill with asfreq with mean / med
    if agg == 'median':
        df_agg = df_agg.fillna(df_agg.median())
    else:
        df_agg = df_agg.fillna(df_agg.mean())

    # Decompose using either stl or seasonal_decompose
    # dfdecomp = seasonal_decompose(df_agg, model='addtive' , period=decompose_period)
    if (dt_rounding == "30min"):
        dfdecomp = STL(df_agg, robust=True, period=48).fit()
    else:
        #seasonal_decompose(df_agg, model='addtive' , period=decompose_period)
        dfdecomp = STL(df_agg, robust=True).fit()

    # Get Timezone to plot time-aware plots
    timezone = get_timezone(selected_df, provider, region)

    # print(provider, region, timezone)

    # Filter the plotable area if choose to.
    if plotstart is None:
        plotstart = start
    if plotend is None:
        plotend = end

    deompose_fig = plot_decompose(dfdecomp, timezone, dtfmt=dtfmt, xtickstepsize=xtickstepsize, xticksrotation=xticksrotation,
                                  start=plotstart, end=plotend)

    # Execute Statistical Test Analysis
    if statsTest:
        stats_test_result = stats_test(
            dfdecomp.observed, adflag=adflag, test_regression=test_regression)
    else:
        stats_test_result = None
        
    # Boxplot Seasonality
    seasonal_analysis_results = seasonal_analysis(
        dfdecomp.seasonal, dt_rounding, provider, region, timezone)
    plt.close('all')

    return {
        'decomposition': {"data": dfdecomp, "fig": deompose_fig},
        'stats_test': stats_test_result,
        'seasonal_analysis': seasonal_analysis_results,
        'parameters': {
            'provider': provider, 
            'region': region,
            'decompose_col': decompose_col,
            'timezone': timezone, 
            'dt_rounding': dt_rounding, 
            'start': start, 
            'end': end,
            'adflag': adflag, 
            'test_regression': test_regression,
            'dtfmt': dtfmt, 
            'xtickstepsize': xtickstepsize, 'xticksrotation': xticksrotation,
            'plotstart': plotstart, 'plotstart': plotend,
            'agg': agg
        }
    }
