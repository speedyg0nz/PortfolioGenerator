# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 23:08:38 2016

@author: chongwee
"""
import csv
from yahoo_finance import Share
import os
from sys import exit
#pip install cvxpy. If this doesn't work on Windows, get binaries from http://www.lfd.uci.edu/~gohlke/pythonlibs/
import cvxpy as cvx 
import numpy as np
import datetime as dt
import calendar
import requests

def readSymbolsCSV(filepath):
    symbols = []    
    with open(filepath, 'r', newline='\n', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:            
            symbols.append(row[0])
    f.close()
    return symbols
    
def readDatesCSV(filepath):
    dates = []    
    with open(filepath, 'r', newline='\n', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:            
            dates.append(row[0])
    f.close()
    return dates 

def findLastTradingDayInPeriods(start,end,allTradingDates,frequency):
            
    startDate = dt.datetime.strptime(start, '%Y-%m-%d')
    endDate = dt.datetime.strptime(end, '%Y-%m-%d')

    lastTradingDays = []
    date = startDate        
    
    allDatesInPeriod = []
    while date <= endDate: 
        allDatesInPeriod.append(date.strftime('%Y-%m-%d'))
        if meetsDateRequirements(date,frequency):
            tradingDaysInPeriod = list(set(allTradingDates).intersection(allDatesInPeriod))
            if len(tradingDaysInPeriod) > 0:             
                lastTradingDays.append(max(tradingDaysInPeriod)) #append last/max trading day in period
            allDatesInPeriod = []
        date += dt.timedelta(days=1)     
    
    return lastTradingDays        

def meetsDateRequirements(date,frequency):
    if frequency == "daily":    
        return True
    elif frequency == "weekly":
        if date.isoweekday() == 7:
            return True
        else:
            return False
    elif frequency == "monthly":
        lastDayInMonth = calendar.monthrange(date.year,date.month)[1]
        if date.day == lastDayInMonth:
            return True
        else:
            return False
    elif frequency == "yearly":
        if date.day == 31 and date.month == 12:
            return True
        else:
            return False   
    else:
        print("Invalid frequency parameter passes to meetsDateRequirements")
        exit(0); #exit program due to invalid input (neither daily, weekly, monthly or yearly)

def retrieveQuoteFromGoogle(symbol,start_date,end_date):
    start = dt.date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10]))
    end = dt.date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10]))
    url_string = "http://www.google.com/finance/historical?q={0}".format(symbol)
    url_string += "&startdate={0}&enddate={1}&output=csv".format(start.strftime('%b %d, %Y'),end.strftime('%b %d, %Y'))    
    response = requests.get(url_string)
    quoteDict = {}  
    if response.status_code == 200:        
        open('temp.csv', 'wb').write(response.content)    
        with open('temp.csv', 'r', newline='\n', encoding="utf-8") as f:
            reader = csv.reader(f)
            reader.next()            
            for row in reader:            
                date = dt.datetime.strptime(row[0], '%d-%b-%y')
                dateStr = date.strftime('%Y-%m-%d')
                quoteDict[dateStr] = float(row[4])  
        f.close()  
    else:
        raise Exception('Unable to find quote on Google Finance')          
    print(quoteDict)
    return quoteDict #return close price from last trading day of week since it might not be friday     

def retrieveQuoteFromYahoo(symbol,start,end):        
    share = Share(symbol)  
    quoteList = share.get_historical(start,end)
    quoteDict = {}
    for quote in quoteList:
        quoteDict[quote['Date']] = float(quote['Adj_Close'])        
    return quoteDict

def retrieveHistoricalQuotes(symbol,start,end):    
    print("Retrieving historical prices for {0}...".format(symbol))    
    
    if checkFileExists(symbol,start,end):
        return readQuotesFromCSV(symbol,start,end)
    else:
        quoteDict = {}
        try:
            quoteDict = retrieveQuoteFromGoogle(symbol,start,end)
        except:
            quoteDict = retrieveQuoteFromYahoo(symbol,start,end)
        writeQuotesToCSV(symbol,start,end,quoteDict)
        return quoteDict

def readQuotesFromCSV(symbol,start,end):
    quotes = {}    
    directory = "quotes"
    filename = "{0}_{1}_{2}.csv".format(symbol,start,end)
    with open(os.path.join(directory,filename), 'r', newline='\n', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:            
            quotes[row[0]] = float(row[1])
    f.close()
    return quotes

def writeQuotesToCSV(symbol,start,end,quotes):
    directory = "quotes"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = "{0}_{1}_{2}.csv".format(symbol,start,end)
    with open(os.path.join(directory,filename), 'w', newline="\n", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        dates = quotes.keys()        
        for date in sorted(dates):        
            cells = [date,quotes[date]]                    
            writer.writerow(cells)        
    csvfile.close()
 
def writeReturnsToCSV(filename,returns,cols):    
    with open(filename, 'w', newline="\n", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        symbols = sorted(returns.keys())
        writer.writerow(symbols)    
        for i in range(cols):        
            cells = [i+1]
            for symbol in symbols:      
                #print(i)
                cells.append(returns[symbol][i])
            writer.writerow(cells)        
    csvfile.close()

def writeOptimalPortfolioToCSV(filename,combinedResults,symbols):
    with open(filename, 'w', newline="\n", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        cells = ['Variance','StDev','ExpRet','SharpeRatio']
        cells.extend(symbols)
        writer.writerow(cells)    
        for results in combinedResults:        
            cells = [results['variance'],results['stdev'],results['expRet'],results['sharpe']]
            cells.extend(results['weights'])
            writer.writerow(cells)        
    csvfile.close()

def checkFileExists(symbol,start,end):
    directory = "quotes"
    filename = "{0}_{1}_{2}.csv".format(symbol,start,end)
    if not os.path.exists(os.path.join(directory,filename)):
        return False
    else:
        return True    

def generatePortfolio(symbolsFilename,startDate,endDate,analysisStartDate,analysisEndDate,analysisPeriod,minExpRetForOptimization, maxExpRetForOptimization,numberOfSteps,minWeightPerStock,maxWeightPerStock,riskFreeRate,useExcessReturns,benchmarkSymbol,outputFilename):
    quotes = retrieveHistoricalQuotes("^GSPC",startDate,endDate)
    allTradingDays = sorted(quotes.keys())
    dates = findLastTradingDayInPeriods(analysisStartDate,analysisEndDate,allTradingDays,analysisPeriod)
    
    benchmarkQuotes = {}    
    if useExcessReturns:
        benchmarkQuotes = retrieveHistoricalQuotes(benchmarkSymbol,startDate,endDate)
        
    #start by getting the list of symbols to be considered for shortlisting
    symbols = sorted(readSymbolsCSV(symbolsFilename))
    
    #retrieve historical prices and calculate returns
    returns = {}
    for symbol in symbols:
        quotes = retrieveHistoricalQuotes(symbol,startDate,endDate)
        symbolReturns = []        
        previousTime = dates[0]
        for currentTime in dates[1:]:
            try:
                prev = quotes[previousTime]
                curr = quotes[currentTime]
                stockReturn = (curr-prev)/prev
                if useExcessReturns:
                    benchmarkPrev = benchmarkQuotes[previousTime]
                    benchmarkCurr = benchmarkQuotes[currentTime]
                    benchmarkReturn = (benchmarkCurr-benchmarkPrev)/benchmarkPrev
                    stockReturn = stockReturn - benchmarkReturn
                symbolReturns.append(stockReturn) #multiply by 100 if you work using percent
            except KeyError:       
                raise ValueError("Missing quotes for {0} between {1} and {2}".format(symbol,previousTime,currentTime))
            previousTime = currentTime
        returns[symbol] = symbolReturns
    
    #uncomment the following line if you wish to save the returns data to a csv file
    #writeReturnsToCSV("generatedReturns.csv",returns,len(dates)-1)
    
    #prepare the data for optimization using cvxpy
    returns2DArray = []
    expectedReturns = []
    for symbol in symbols:
        returns2DArray.append(returns[symbol])
        expectedReturns.append(np.average(returns[symbol]))
        
    expectedReturns = np.array(expectedReturns).T #transposed so we can multiply with weights later
    covMatrix = np.cov(returns2DArray)
    
    # Construct the efficient frontier.
    combinedResults = []
    
    print("Peforming portfolio optimization...")
    
    maxSharpe = 0.0
    minVariance = float("inf")
    maxSharpePortfolio = {}
    minVariancePortfolio = {}
    for expRet in np.linspace(minExpRetForOptimization, maxExpRetForOptimization, num=numberOfSteps, endpoint=True):    
        #define the variable for the solver to generate    
        w = cvx.Variable(len(symbols))     
        #set objective as minimum variance    
        objective = cvx.Minimize(cvx.sum_entries(covMatrix*w))    
        #weights must be under 1, sum of weights is 1, 
        constraints = [minWeightPerStock <= w, w <= maxWeightPerStock, cvx.sum_entries(w) == 1, cvx.sum_entries(expectedReturns*w) == expRet]    
        prob = cvx.Problem(objective, constraints)    
        # The optimal objective is returned by prob.solve().
        prob.solve()        
        #checks if result was optimal and output it to 
        if prob.status == 'optimal':           
            variance = cvx.sum_entries(covMatrix*w).value
            results = {}
            results['variance'] = variance
            results['stdev'] = np.sqrt(variance)
            results['expRet'] = expRet
            results['sharpe'] = (expRet-riskFreeRate)/np.sqrt(variance)
            results['weights'] = (np.array(w.value.T)[0]).tolist()
            combinedResults.append(results)
            
            if results['sharpe'] > maxSharpe:
                maxSharpe = results['sharpe']
                maxSharpePortfolio = results

            if variance < minVariance:
                minVariance = variance
                minVariancePortfolio = results                
    
    if outputFilename is not "":    
        writeOptimalPortfolioToCSV(outputFilename,combinedResults,symbols)
    
    print("Portfolio optimization complete.")
    
    
    
    return combinedResults, maxSharpePortfolio, minVariancePortfolio, symbols