

# This code runs a regression of stock indices to identify any indicative forward prices,
#trades an index and record the result.
#Disclosure: Nothing in this repository should be considered investment advice. Past performance is not necessarily indicative of future returns.
# These are general examples about how to import data using pandas for a small sample of financial data across different time intervals.
#Please note that the below code is written with the objective to explore various python features.

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import quandl
import pandas as pd
import seaborn as sns
sns.set()
from statsmodels import regression
import statsmodels.api as sm

class quandlclient(object):
    def __init__(self):
        pass
    def collectdata(self,ticker):

        # API key from your Quandl account
        quandl.ApiConfig.api_key = "yourquandlapikwy"

        # Calculate todays date and date in the past
        start_date = date.today() - relativedelta(days=1800)
        today_date = date.today() - relativedelta(days=1)

        #Request data from Quandl
        data = quandl.get(ticker, start_date=start_date, end_date=today_date)
        data.index.sort_values()
        return data

class regr():
    def __init__(self):
        pass

    def regranalysis(self,data):

        #Making sure only 60 days of data as we want to do a regression of day 1-20 over day 20-40 and based on that invest day 40-60
        data = data.tail(60)
        #Emptying data container for selected index data
        indexrsquared = []

        #Looping over all columns (indices)
        for column in data.columns[1:]:
            X = data.iloc[0:20,[0]] #Index day 1-20
            Y = data[[column]]      #Subindex
            Yregr = Y.iloc[20:40]   #Subindex day 20-40

            #Adding constant to get intercept in regression
            Xconst = sm.add_constant(X)
            #Harmonizing the Index in both dataframes
            Xconst.index= Yregr.index
            #Running the regression
            model = regression.linear_model.OLS(Yregr, Xconst).fit()
            a = model.params[0]
            b = model.params[1]

            #Harmonizing the Index in both dataframes
            X.index = Yregr.index

            #Copying data of subindex at first run for specific time period
            if not indexrsquared:
                indexrsquared.append(Y.columns.values[0]) #index name of sub Nasdaq
                indexrsquared.append(model.rsquared)  #Rsquared from regr

                indexrsquared.append(Y.iloc[40,0])           #Buy value sub nasdaq
                indexrsquared.append(pd.Timestamp(Y.iloc[[40]].index.values[0])) #Buy date sub nasdaq

                indexrsquared.append(Y.iloc[59,0])           #Sell value sub nasdaq
                indexrsquared.append(pd.Timestamp(Y.iloc[[40]].index.values[0])) #Sell date sub nasdaq

            #Copying data of subindex if rsquared is higher
            elif model.rsquared > indexrsquared[1]:
                #indexrsquared = []
                indexrsquared[0] = Y.columns.values[0] #index name of sub Nasdaq
                indexrsquared[1] = model.rsquared #Rsquared from regr

                indexrsquared[2] = Y.iloc[40,0] #Buy value sub nasdaq
                indexrsquared[3] = pd.Timestamp(Y.iloc[[40]].index.values[0]) #Buy date sub nasdaq

                indexrsquared[4] = Y.iloc[59,0] #Sell value sub nasdaq
                indexrsquared[5] = pd.Timestamp(Y.iloc[[40]].index.values[0]) #Sell date sub nasdaq

            else:
                pass
            #Emptying the Subindex data
            Y=[]

        #check Index return day 20-40 to decide if subindex should be short or long day 40-60

        Nasdaqmonthperf = (data.iloc[40,0] / data.iloc[20,0])

        if Nasdaqmonthperf > 0:
            indexrsquared.append("B") #buy ind
        elif Nasdaqmonthperf < 0:
            indexrsquared.append("S") #sell ind
        else:
            pass

        return indexrsquared

    def reporting(self, trades, data):

        #Calculate return
        trades['return'] = (trades['sellvalue']-trades['buyvalue'])/(trades['buyvalue'])

        #Plot
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        ax.plot(trades['selldate'], trades['return'].dropna().cumsum().apply(np.exp))


        plt.show()


def main():

    # creating object for connecting with quandl api
    timeseriesobject = quandlclient()
    # calling function to download daily price level data from quandl, defining ticker to download
    data = timeseriesobject.collectdata(["NASDAQOMX/NDX.1","NASDAQOMX/NQUSM.1","NASDAQOMX/NQUSS.1","NASDAQOMX/NQUSL.1","NASDAQOMX/NQBUY.1"])

    #create dataframe to hold trades
    columns=["indexname", "regrresult", "buyvalue", "buydate", "sellvalue", "selldate", "buyorsell"]
    trades = pd.DataFrame(columns=columns)

    # creating object for crunning regression
    regrobject = regr()

    #Transform data frame to contain the exact number of days
    periods = data.index.size /20
    periods = int(periods)
    totdays=periods*20
    data = data.tail(totdays)

    #Loop through the data using predefined timeperiods
    for i in range(periods-3):

        #Use 60 days for each run
        periodstart = 0
        periodend = 60
        periodstart = i*20
        periodend = periodend + i*20

        datasend = data.iloc[periodstart:periodend]

        #Run regression for the new period
        regrresult = regrobject.regranalysis(datasend)

        #Copy the data from the list over to the dataframe row by row
        trades.loc[len(trades)] = regrresult

    #Plot the trades
    trade = regrobject.reporting(trades,data)


if __name__ == "__main__":
     #calling main function
    main()
