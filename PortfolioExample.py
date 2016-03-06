# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 10:51:42 2016

@author: chongwee
"""

import PortfolioGenerator as pg

symbolsFilename     = 'symbols-shortlist.csv' #contains all the symbols to be considered
outputFilename      = 'optimalPortfolio.csv' #filepath for the optimization outputs, leave empty to not write to file
startDate           = '2006-01-03' #start date to retrieve historical prices
endDate             = '2016-03-06' #end date to retrieve historical prices
analysisStartDate   = '2013-01-03' #usually same as price dates but this allows for additional flexibility in analysis, esp if certain stocks started trading later than others (e.g. FB, PYPL)
analysisEndDate     = '2016-03-06' #usually same as price dates but this allows for additional flexibility in analysis, esp if certain stocks started trading later than others (e.g. FB, PYPL)
minWeightPerStock   = 0.0 #from 0 to 1
maxWeightPerStock   = 0.05 #from 0 to 1
minExpRetForOpt     = 0  #per frequency period, from 0 to 1
maxExpRetForOpt     = 0.10  #per frequency period, from 0 to 1
numberOfSteps       = 101 #any number, the larger the higher the resolution of the frontier
analysisPeriod      = "weekly" #daily, weekly, monthly or yearly
riskFreeRate        = 0.0 #per frequency period, from 0 to 1, 1 meaning 100%
useExcessReturns    = False #use excess returns over benchmark instead of pure returns
benchmarkSymbol     = '^GSPC' #benchmark stock/index to calculate excess returns against


try:
    combinedResults, maxSharpePortfolio, minVariancePortfolio, symbols = pg.generatePortfolio(symbolsFilename,
                        startDate,
                        endDate,
                        analysisStartDate,
                        analysisEndDate,
                        analysisPeriod,
                        minExpRetForOpt, 
                        maxExpRetForOpt,
                        numberOfSteps,
                        minWeightPerStock,
                        maxWeightPerStock,
                        riskFreeRate,
                        useExcessReturns,
                        benchmarkSymbol,
                        outputFilename)
    
    #following section shows how to retrieve the optimization results
                        
    print("\n========== Max Sharpe Portfolio ==========\n")
    print("Expected Returns:\t{}".format(maxSharpePortfolio['expRet']))
    print("Sharpe Ratio:\t{}".format(maxSharpePortfolio['sharpe']))
    print("Std Dev:\t{}\n".format(maxSharpePortfolio['stdev']))
    for i in range(len(symbols)):
        if maxSharpePortfolio['weights'][i] > 0.00001: #ignore near zero weightage
            print("Weight, {0}:\t{1:.3f}".format(symbols[i],maxSharpePortfolio['weights'][i]))
            
    
    print("\n========== Min Variance Portfolio ==========\n")
    print("Expected Returns:\t{}".format(minVariancePortfolio['expRet']))
    print("Sharpe Ratio:\t{}".format(minVariancePortfolio['sharpe']))
    print("Std Dev:\t{}\n".format(minVariancePortfolio['stdev']))
    for i in range(len(symbols)):
        if minVariancePortfolio['weights'][i] > 0.00001: #ignore near zero weightage
            print("Weight, {0}:\t{1:.3f}".format(symbols[i],minVariancePortfolio['weights'][i]))
        
except ValueError as err:
    print(err.args[0])