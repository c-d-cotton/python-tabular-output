#!/usr/bin/env python3

import copy
import decimal
import numpy as np
import os
import pandas as pd
from pathlib import Path
import statsmodels.formula.api as smf
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/')


from tab_general_func import printlofl
from tab_general_func import tabularconvert
from tab_general_func import mergetabsecs
from tab_general_func import getcoefftabmatrixgen

# Test Auxilliary Functions:{{{1
def getmodelstest():
    # set random number seed
    np.random.seed(1)

    x1 = np.random.normal(loc = 0, scale = 1, size = [100])
    x2 = np.random.normal(loc = 0, scale = 1, size = [100])
    x3 = np.random.normal(loc = 0, scale = 1, size = [100])
    u = np.random.normal(loc = 0, scale = 3, size = [100])
    
    y = x1 + x2 + u

    df = pd.DataFrame({'y': y, 'x1': x1, 'x2': x2, 'x3': x3})

    model1 = smf.ols(formula = 'y ~ x1', data=df).fit()
    model2 = smf.ols(formula = 'y ~ x1 + x2', data=df).fit()
    model3 = smf.ols(formula = 'y ~ x1 + x2 + x3', data=df).fit()

    return([model1, model2, model3])


# Get Matrices from Model List:{{{1
def getcoeffmatrices(sm_models, coefflist = None):
    """
    sm_models should be a list of model.fit() from statsmodels
    """

    # get coefflist if coefflist is None
    if coefflist is None:
        coefflist = []
        for model in sm_models:
            coeffs = list(model.params.index)
            for coeff in coeffs:
                if coeff not in coefflist:
                    coefflist.append(coeff)

    numrow = len(coefflist)
    numcol = len(sm_models)

    # create empty list
    betamatrix = [None] * (numrow * numcol)
    # reshape as listoflists
    betamatrix = [betamatrix[i: i + numcol] for i in range(0, len(betamatrix), numcol)]

    # create additional empty matrices
    pvalmatrix = copy.deepcopy(betamatrix)
    sematrix = copy.deepcopy(betamatrix)

    for col in range(numcol):
        betas = list(sm_models[col].params)
        pvals = list(sm_models[col].pvalues)
        ses = list(sm_models[col].bse)
        coeffs = list(sm_models[col].params.index)
        for thisregi in range(len(betas)):
            coeff = coeffs[thisregi]
            if coeff in coefflist:
                row = coefflist.index(coeff)

                betamatrix[row][col] = betas[thisregi]
                pvalmatrix[row][col] = pvals[thisregi]
                sematrix[row][col] = ses[thisregi]

    return(coefflist, betamatrix, pvalmatrix, sematrix)
            

def getcoeffmatrices_test():
    coefflist = None
    # coefflist = ['x2', 'x1']

    models = getmodelstest()
    coefflist, betamatrix, pvalmatrix, sematrix = getcoeffmatrices(models, coefflist = coefflist)
    print(coefflist)
    print('')
    print(betamatrix)
    print('')
    print(pvalmatrix)
    print('')
    print(sematrix)

# getcoeffmatrices_test()
def getparammatrix(sm_models, paramlist = 'def'):
    if paramlist == 'def':
        paramlist = ['nobs']
    if paramlist is None:
        paramlist = []

    numcol = len(sm_models)
    numrow = len(paramlist)

    # create empty list
    parammatrix = [None] * (numrow * numcol)
    # reshape as listoflists
    parammatrix = [parammatrix[i: i + numcol] for i in range(0, len(parammatrix), numcol)]

    for col in range(numcol):
        for row in range(numrow):
            parammatrix[row][col] = getattr(sm_models[col], paramlist[row])

    return(paramlist, parammatrix)


def getparammatrix_test():
    paramlist = 'def'
    paramlist = ['nobs', 'aic', 'rsquared', 'rsquared_adj']

    models = getmodelstest()
    parammatrix = getparammatrix(models, paramlist = paramlist)


# getparammatrix_test()
# Adjust Matrices:{{{1
def getcoefftabmatrix(
    # coeff matrices arguments
    sm_models, coefflist = None,
    # format options
    coeffnames = None, coeffdecimal = 3, stardict = 'def',
    # print options
    printtab = False, printmaxcolsize = None,
    # output options
    returntabsec = False,
    ):
    """
    Returns a listoflist of following form:
    var1, 0.002**, 0.004**
        , (0.001), (0.001)
    var2,        , 0.008***
        ,        , (0.000)
    i.e. row of coefficients with stars for a given variable with standard deviations in brackets in next row

    coeff matrix arguments:
    sm_models: list of statsmodels.fit()
    coefflist = list of variables to show in the tabsec

    format arguments:
    coeffnames = list of names to use in table (same length as coefflist) OR dictionary from name in statsmodel to name I want in the tabular (can contain superfluous names)
    coeffdecimal = 3: decimal places in coefficients and standard errors
    stardict = 'def' then use default i.e. * <0.05, ** <0.01, *** < 0.001. If None/{} then do not include

    print options:
    printtab = False. If True then print the listoflists
    printmaxcolsize = None then just use actual length. If [None, 10] then no restriction on first column but second is shortened to 10 characters long

    output options:
    returntabsec = False. If True then return tabsec rather than listoflists
    """

    # get matrices
    coefflist, betamatrix, pvalmatrix, sematrix = getcoeffmatrices(sm_models, coefflist = coefflist)

    # get the coefflist to show in the table
    if coeffnames is not None:
        if isinstance(coeffnames, list):
            coefflist = coeffnames
        elif isinstance(coeffnames, dict):
            for i in range(len(coefflist)):
                if coefflist[i] in coeffnames:
                    coefflist[i] = coeffnames[coefflist[i]]
        else:
            raise ValueError('Type for coeffnames not defined.')

    # convert the coeffnames and numerical matrices into a coeffmatrixtab using the general function
    # also print if I want to
    coefftabmatrix = getcoefftabmatrixgen(
    # matrix inputs
    coefflist, betamatrix, pvalmatrix, sematrix, 
    # format otions
    stardict = stardict, coeffdecimal = coeffdecimal,
    # print options
    printtab = printtab, printmaxcolsize = printmaxcolsize,
    )

    # maybe convert into a tabsec
    if returntabsec is True:
        coefftabmatrix = tabularconvert(coefftabmatrix)

    return(coefftabmatrix)
        

def getcoefftabmatrix_test():
    coefflist = None
    # coefflist = ['x2', 'x1']

    coeffnames = {'x1': 'x1_var', 'x2': 'x2_var2', 'x3': 'x3_var3'}
    coeffdecimal = 5
    stardict = {0.5: '!!!!!'}

    printtab = True
    printmaxcolsize = [10, None, 10, 10]

    returntabsec = False


    models = getmodelstest()

    coefftabmatrix = getcoefftabmatrix(
    # coeff matrices arguments
    models, coefflist = coefflist,
    # format options
    coeffnames = coeffnames, coeffdecimal = coeffdecimal, stardict = stardict,
    # print options
    printtab = printtab, printmaxcolsize = printmaxcolsize,
    # output options
    returntabsec = returntabsec,
    )


# getcoefftabmatrix_test()
def getparamtabmatrix(
    # matrix arguments
    sm_models, paramlist = 'def',
    # format
    paramnames = None, paramdecimal = None,
    # print options
    printtab = False, printmaxcolsize = None,
    # output options
    returntabsec = False,
    ):
    """
    matrix arguments:
    sm_models: a list of statsmodels.fit() models
    paramlist = 'def': list of properties of the fit() method that I wish to include in the parameter table e.g. nobs, ess, aic. If None, include nothing. If 'def', include 'nobs'

    format arguments:
    paramnames = None: Names for the parameters that I'll put in tabular. If paramlist == 'def' then equals N.
    paramdecimal = None: Can be an integer or a list. List represents decimal places for each parameter. If paramlist == 'def' then paramdecimal = 0

    print arguments:
    printtab = False: If True then print the matrix
    printmaxcolsize = None: Can be an integer or list to specify the max size of a row when printing

    returntabsec = False. If True then return tabsec rather than listoflists
    
    """
    numrow = len(paramlist)
    numcol = len(sm_models)

    if paramlist == 'def':
        paramlist = ['nobs']
        paramnames = ['N']
        paramdecimal = [0]

    # verify correct lengths
    if not isinstance(paramdecimal, list):
        paramdecimal = [paramdecimal] * numrow
    if len(paramdecimal) != numrow:
        raise ValueError('paramdecimal is the wrong length.')
    if paramnames is None:
        paramnames = paramlist
    if len(paramnames) != numrow:
        raise ValueError('paramnames is the wrong length.')

    paramlist, parammatrix = getparammatrix(sm_models, paramlist = paramlist)



    # apply decimals
    for i in range(numrow):
        for j in range(numcol):
            parammatrix[i][j] = str(round(decimal.Decimal(parammatrix[i][j]), paramdecimal[i]))

    # add in index column
    for i in range(numrow):
        parammatrix[i] = [paramnames[i]] + parammatrix[i]

    if printtab is True:
        printlofl(parammatrix, maxcolsize = printmaxcolsize)

    # maybe convert into a tabsec
    if returntabsec is True:
        parammatrix = tabularconvert(parammatrix)

    return(parammatrix)


def getparamtabmatrix_test():
    paramlist = ['nobs', 'aic', 'ess']
    paramnames = ['N', 'AIC', 'ESS']
    paramdecimal = [0, 3, 1]

    printmaxcolsize = None

    models = getmodelstest()

    getparamtabmatrix(
    # matrix arguments
    models, paramlist = paramlist,
    # format
    paramnames = paramnames, paramdecimal = paramdecimal,
    # print options
    printtab = True, printmaxcolsize = printmaxcolsize,
    # output options
    returntabsec = False,
    )


# getparamtabmatrix_test()
def getsmresultstable(
    # matrices arguments
    sm_models, coefflist = None, paramlist = 'def',
    # format options - coeff
    coeffnames = None, coeffdecimal = 3, stardict = 'def',
    # format options - param
    paramnames = None, paramdecimal = None,
    # format options - other
    ynames = None, colalign = None, hlines_tabsec = 'all',
    # additional list of lists before/between/after other matrices
    beforelofl = None, betweenlofl = None, afterlofl = None,
    # print options
    printtab = False, printmaxcolsize = None,
    # output options
    savename = None,
    ):
    """
    coeff matrix arguments:
    sm_models: list of statsmodels.fit()
    coefflist = list of variables to show in the tabsec
    paramlist = 'def': list of properties of the fit() method that I wish to include in the parameter table e.g. nobs, ess, aic. If None, include nothing. If 'def', include 'nobs'

    format arguments - coeff:
    coeffnames = list of names to use in table (same length as coefflist) OR dictionary from name in statsmodel to name I want in the tabular (can contain superfluous names)
    coeffdecimal = 3: decimal places in coefficients and standard errors
    stardict = 'def' then use default i.e. * <0.05, ** <0.01, *** < 0.001. If None/{} then do not include

    format arguments - param:
    paramnames = None: Names for the parameters that I'll put in tabular. If paramlist == 'def' then equals N.
    paramdecimal = None: Can be an integer or a list. List represents decimal places for each parameter. If paramlist == 'def' then paramdecimal = 0

    format options - y:
    ynames = None: Specifies how to describe the y variables. If None, then just put (1), (2), (3) etc. If string, still include the numbers but put the variable in the top left. If a list the same length as the number of columns, put name of yvar above each column.

    print options:
    printtab = False. If True then print the listoflists
    printmaxcolsize = None then just use actual length. If [None, 10] then no restriction on first column but second is shortened to 10 characters long

    output options:
    savename: place where I can save the output file

    """

    numcol = len(sm_models)

    # GET YNAMES
    if ynames is None:
        ynames = [''] + ['(' + str(i) + ')' for i in range(1, numcol + 1)]
    else:
        if isinstance(ynames, str):
            ynames = [ynames] + ['(' + str(i) + ')' for i in range(1, numcol + 1)]
        else:
            ynames = [''] + ynames
    # convert to list of lists
    ynames = [ynames]

    # GET COEFFTABMATRIX
    coefftabmatrix = getcoefftabmatrix(
    # coeff matrices arguments
    sm_models, coefflist = coefflist,
    # format options
    coeffnames = coeffnames, coeffdecimal = coeffdecimal, stardict = stardict,
    )

    if paramlist is not None and paramlist is not []:
        # GET PARAMTABMATRIX
        paramtabmatrix = getparamtabmatrix(
        # matrix arguments
        sm_models, paramlist = paramlist,
        # format
        paramnames = paramnames, paramdecimal = paramdecimal,
        )

    lofl_all = []
    tabsecs_all = []

    if beforelofl is not None:
        lofl_all = lofl_all + beforelofl
        tabsecs_all.append(tabularconvert(beforelofl))

    lofl_all = lofl_all + ynames
    tabsecs_all.append(tabularconvert(ynames))

    lofl_all = lofl_all + coefftabmatrix
    tabsecs_all.append(tabularconvert(coefftabmatrix))

    if beforelofl is not None:
        lofl_all = lofl_all + betweenlofl
        tabsecs_all.append(tabularconvert(betweenlofl))

    if paramlist is not None and paramlist is not []:
        lofl_all = lofl_all + paramtabmatrix
        tabsecs_all.append(tabularconvert(paramtabmatrix))

    if afterlofl is not None:
        lofl_all = lofl_all + after_lofl
        tabsecs_all.append(tabularconvert(afterlofl))

    # full listoflists
    if printtab is True:
        printlofl(lofl_all, maxcolsize = printmaxcolsize)

    # CONVERT ALL LISTS TO TABSECS
    tabular = mergetabsecs(tabsecs_all, colalign = colalign, hlines = hlines_tabsec, savename = savename)

    return(tabular)


def getsmresultstable_test():
    models = getmodelstest()

    coefflist = ['x2', 'x3']
    coeffnames = {'x2': 'whywhy'}
    coeffdecimal = 2
    colalign = 'lccc'
    paramdecimal = [0, 3]

    savename = __projectdir__ / Path('temp/resultstable_test.tex')

    getsmresultstable(
    # matrices arguments
    models, coefflist = coefflist, paramlist = ['nobs', 'ess'],
    # format options - coeff
    coeffnames = coeffnames, coeffdecimal = coeffdecimal, stardict = 'def',
    # format options - param
    paramnames = None, paramdecimal = paramdecimal,
    # format options - other
    ynames = None, colalign = colalign, hlines_tabsec = 'all',
    # additional list of lists before/between/after other matrices
    beforelofl = None, betweenlofl = None, afterlofl = None,
    # print options
    printtab = True, printmaxcolsize = None,
    # output options
    savename = savename,
    )

