import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import pandas as pd
import pytz
import matplotlib.dates as mdates
import numpy as np

def get_timezone(dataset, provider, region):
    timezones = dataset[ (dataset['provider'] == provider) & (dataset['region'] == region) ]['timezone'].unique()
    
    if (len(timezones)) != 1:
        print(timezones)
        raise ValueError()
    timezone = timezones[0]
    return timezone

def plot_decompose(decomposed_data, timezone,
                   start = None, end = None,
                   figsize=(20,8), dtfmt='%d/%m',
                   xtickstepsize=2, xticksrotation=45):
        
    with plt.rc_context():
        plt.rc("figure", figsize=figsize)

        fig, axis = plt.subplots(figsize=(24,12), sharex=True, nrows=4)
        
        # Set xlims when not set:
        if (start is None) or (start is not None and type(start) is not str):
            start = int(decomposed_data.observed.index.min().timestamp() / 24 / 60 / 60)
        else:
            start = int(pd.Timestamp(start).timestamp()  / 24 / 60 / 60)
            
        if (end is None) or (end is not None and type(end) is not str):
            end = int(decomposed_data.observed.index.max().timestamp() / 24 / 60 / 60)
        else:
            end = int(pd.Timestamp(end).timestamp()  / 24 / 60 / 60)
        
        # Plot Components
        axis[0].plot(decomposed_data.observed)
        plt.setp(axis[0], ylabel='Observed')

        axis[1].plot(decomposed_data.resid)
        plt.setp(axis[1], ylabel='Residuals')
        
        axis[2].plot(decomposed_data.trend)
        plt.setp(axis[2], ylabel='Trend')
        
        axis[3].plot(decomposed_data.seasonal)
        plt.setp(axis[3], ylabel='Seasonal')
        
        hours = mdates.HourLocator(interval=12) #or use interval
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
        return fig

# Prints the results of augmented Dickey–Fuller test (ADF)
# h0 -> time series has a unit-root; is non-stationary --> data is time-dependent
# ---> if a time series has a unit root, it shows a systematic pattern that is unpredictable

# h1 -> time series has NOT unit-root; is stationary --> data is NOT time-dependent
# ---> 

# adf
# if h0 cannot be rejected, h0 is true -> non-stationary
# if h0 is rejected, h1 is true -> stationary


# rejection criterions:
# if p-value is less than x% (e.g. 5)
# of if test statistic is lower then critical value reject h0


# The null hypothesis of the Augmented Dickey-Fuller is that there is a unit root,
# with the alternative that there is no unit root.
# If the pvalue is above a critical size, then we cannot reject that there is a unit root.
# If the null hypothesis is failed to be rejected, this test may provide evidence that the series is non-stationary

# The p-values are obtained through regression surface approximation from MacKinnon 1994
# but using the updated 2010 tables.
# If the p-value is close to significant, then the critical values should be used to judge whether to reject the null.

# 
# -> The lag length should be chosen so that the residuals aren’t serially correlated. 
# https://www.statisticshowto.com/adf-augmented-dickey-fuller-test/
# https://www.statisticshowto.com/serial-correlation-autocorrelation/
# https://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.adfuller.html

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

# Kwiatkowski-Phillips-Schmidt-Shin test for stationarity.
# -> h0 ->  x is level or trend stationary i.e., not time-dependent
# -> h1 non-stationary -> time-depedent

# kpss
# if h0 cannot be rejected, h0 is true -> stationary
# if h0 is rejected, h1 is true -> non-stationary

# https://www.statsmodels.org/devel/generated/statsmodels.tsa.stattools.kpss.html?highlight=kpss#statsmodels.tsa.stattools.kpss

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

# https://www.statsmodels.org/dev/examples/notebooks/generated/stationarity_detrending_adf_kpss.html?highlight=kpss

# Case 1: Both tests conclude that the series is not stationary - The series is not stationary
# Case 2: Both tests conclude that the series is stationary - The series is stationary
# Case 3: KPSS indicates stationarity and ADF indicates non-stationarity - The series is trend stationary. Trend needs to be removed to make series strict stationary. The detrended series is checked for stationarity.
# Case 4: KPSS indicates non-stationarity and ADF indicates stationarity - The series is difference stationary. Differencing is to be used to make series stationary. The differenced series is checked for stationarity.

# Trend-stationary process -> https://en.wikipedia.org/wiki/Trend-stationary_process
# Differencey stationary -> process requires differencing to be made stationary, then it is called difference stationary and possesses one or more unit roots. https://en.wikipedia.org/wiki/Unit_root

from pandas.plotting import autocorrelation_plot

def stats_test(df, adflag=None, test_regression='ct'):
    
    case_desc = {
        "case_1" : "Case 1: Both tests conclude that the series is not stationary - The series is not stationary",
        "case_2" : "Case 2: Both tests conclude that the series is stationary - The series is stationary",
        "case_3" : "Case 3: KPSS indicates stationarity and ADF indicates non-stationarity - The series is trend stationary. Trend needs to be removed to make series strict stationary. The detrended series is checked for stationarity.",
        "case_4" : "Case 4: KPSS indicates non-stationarity and ADF indicates stationarity - The series is difference stationary. Differencing is to be used to make series stationary. The differenced series is checked for stationarity." 
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
    test_adfuller = adfuller(df, regression=test_regression, maxlag = adf_maxlag, autolag=adf_autolag, store=True)
    test_kpss = kpss(df, regression=test_regression, nlags=kpss_nlags, store=True)
    
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
    fig_corr, ax = plt.subplots(figsize=(16,6), sharex=True, ncols=1)
    autocorrelation_plot(df, ax=ax)
    
    fig_dist, axes = plt.subplots(figsize=(16,6), sharex=True, ncols=2)
    df.plot.density(ax=axes[0])
    df.plot.hist(ax=axes[1])
    
    return {"adfuller": {'test': test_adfuller, "result": adf_result},
            "kpss": {'test': test_kpss, "result": kpss_result},
            "case": case, "case_desc": case_desc[case], "fig_dist" : fig_dist, "fig_corr": fig_corr}

def seasonal_analysis(seasonal_df, dt_rounding, provider, region, timezone):
    
    fig, ax = plt.subplots(figsize=(10,6), sharex=True, nrows=1)
    sdf = pd.DataFrame(seasonal_df)
    
    if dt_rounding == "30min":
        strftime = 'H:%M'
        
    if dt_rounding == "H":
        strftime = 'H'
        
    if dt_rounding == "D":
        strftime = 'w'
    
    sdf['hist'] = sdf.index.tz_localize('UTC').tz_convert(timezone).strftime(f"%{strftime}")
    
    if (strftime == "w"):
        sdf['hist'] = sdf['hist'].replace('0', '7')
     
    sdf.boxplot('season', by='hist', showfliers=False, ax=ax)
    
    if (strftime == "w"):
        ax.set_xticklabels(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
 
    if strftime == "H:%M":
        ax.tick_params(axis='x', labelrotation=45)
        
    # Plot Median Line Across Boxplots
    x = sdf.groupby(by='hist').quantile(0.5).values
    x = np.insert(x, 0, np.nan)
    ax.plot(x, 'r--', alpha=0.5)
    fig.tight_layout()
    
    # Remove Titles
    fig.suptitle('')
    ax.set_title('')
    ax.set_xlabel('')
    
    return {"fig": fig, "data": sdf}

from statsmodels.tsa.seasonal import STL
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.stattools import kpss

def decompose(dataset, provider, region, dt_rounding,
              start=None, end=None,
              adflag=None, test_regression='ct', # Stats Test parameters
              dtfmt='%a %d/%m', xtickstepsize=2, xticksrotation=45,
              plotstart=None, plotend=None):
      
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
        
    # Filter based on slice + round to given dt_rounding size (e.g., per hour etc.)
    selected_df = dataset[dataset['driver_invocation'].between(startts, endts, inclusive='both')]
    df_providerregion = selected_df[ (selected_df['provider'] == provider) & (selected_df['region'] == region) ]
    df_providerregion.insert(0, "driver_invocation_rounded", df_providerregion['driver_invocation'].dt.round(dt_rounding))
    df_providerregion_runtime_mean = df_providerregion.groupby(['driver_invocation_rounded'])[['runtime']].mean()
       
    # Hint: asfreq adds records for gaps -> we fill those with means. 
    # TODO, check impact, alterantie code
    df_providerregion_runtime_mean = df_providerregion_runtime_mean.asfreq(dt_rounding)
    # Fill with asfreq with mean
    df_providerregion_runtime_mean = df_providerregion_runtime_mean.fillna(df_providerregion_runtime_mean.mean())
    
    # Decompose using either stl or seasonal_decompose
    # dfdecomp = seasonal_decompose(df_providerregion_runtime_mean, model='addtive' , period=decompose_period)
    if (dt_rounding == "30min"):
        dfdecomp = STL(df_providerregion_runtime_mean, robust=True, period=48).fit()
    else:
         #seasonal_decompose(df_providerregion_runtime_mean, model='addtive' , period=decompose_period)
        dfdecomp = STL(df_providerregion_runtime_mean, robust=True).fit()
    
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
    stats_test_result = stats_test(dfdecomp.observed, adflag=adflag, test_regression=test_regression)
    
    # Boxplot Seasonality
    seasonal_analysis_results = seasonal_analysis(dfdecomp.seasonal, dt_rounding, provider, region, timezone)
    plt.close('all'
              )
    return {
        'decompositon': {"data": dfdecomp, "fig": deompose_fig},
        'stats_test': stats_test_result,
        'seasonal_analysis': seasonal_analysis_results,
        'parameters': {
            'provider': provider, 'region': region, 'dt_rounding': dt_rounding,
            'start': start, 'end': end,
            'adflag' : adflag, 'test_regression': test_regression,
            'dtfmt': dtfmt, 'xtickstepsize': xtickstepsize, 'xticksrotation': xticksrotation,
            'plotstart': plotstart, 'plotstart': plotend
        }
    }

# import statsmodels.api as sm
# https://medium.com/@krzysztofdrelczuk/acf-autocorrelation-function-simple-explanation-with-python-example-492484c32711
# https://www.statsmodels.org/dev/generated/statsmodels.graphics.tsaplots.plot_acf.html
# sm.graphics.tsa.plot_acf(df_providerregion_runtime_mean, lags=decompose_period)
# x = pd.plotting.autocorrelation_plot(df_providerregion_runtime_mean)
# x.plot()
# plt.show()