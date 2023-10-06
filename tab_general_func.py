#!/usr/bin/env python3

import decimal
import os
from pathlib import Path
import sys

__projectdir__ = Path(os.path.dirname(os.path.realpath(__file__)) + '/')

# Defaults:{{{1
stardict_default = {0.1: '$^{+}$', 0.05: '*', 0.01: '**', 0.001: '***'}
stardict_default2 = {0.05: '*', 0.01: '**', 0.001: '***'}

# Print List of Lists:{{{1
def printlofl(listoflists, maxcolsize = None, numspaces = 1):
    """
    Every row and column must have same number of elements
    Skip multicolumns to avoid issues with that
    Won't work with multirows
    """

    # skip rows with multicolumn
    skiprows = []
    for i in range(len(listoflists)):
        for j in range(len(listoflists[i])):
            if isinstance(listoflists[i][j], str) and listoflists[i][j].startswith('\\multicolumn{'):
                skiprows.append(i)
    listoflists = [listoflists[i] for i in range(len(listoflists)) if i not in skiprows]

    numrow = len(listoflists)
    numcol = len(listoflists[0])

    # convert maxcolsize to list
    if not isinstance(maxcolsize, list):
        maxcolsize = [maxcolsize] * numcol
    if len(maxcolsize) != numcol:
        raise ValueError('maxcolsize has the wrong size.')

    # verify everything is a string
    for i in range(numrow):
        for j in range(numcol):
            listoflists[i][j] = str(listoflists[i][j])

    # number of characters of largest row in each column
    largestcolsize = [0] * numcol
    for i in range(numrow):
        for j in range(numcol):
            thislen = len(listoflists[i][j])

            if largestcolsize[j] < thislen:
                largestcolsize[j] = thislen

    # now get the maximum size column when printing
    for j in range(numcol):
        if maxcolsize[j] is None or largestcolsize[j] < maxcolsize[j]:
            maxcolsize[j] = largestcolsize[j]

    # now print out
    for i in range(len(listoflists)):
        thisrow = ''
        for j in range(len(listoflists[i])):
            thisrow = thisrow + listoflists[i][j][: maxcolsize[j]].ljust(maxcolsize[j])
            if j < len(listoflists[i]) - 1:
                thisrow = thisrow + ' ' * numspaces
        print(thisrow) # do not delete - should be here

    
    
def printlofl_test_basic():
    listoflists = [['hello', 'goodbye'], ['1', '2']]
    
    printlofl(listoflists, None)

    printlofl(listoflists, [10, 3])


# Basic Tabular Create:{{{1
def replaceunderscores(texttoreplace):
    """
    This goes through an element in tabular and replaces any underscores that are not in math
    """

    # replacing underscores
    adjusted = texttoreplace
    adjusted = adjusted.replace('\$', '00')
    adjusted = adjusted.replace('\_', '00')
    ignoreunderscore = False
    replacecharacters = []
    for i in range(0, len(adjusted)):
        if adjusted[i] == '$':
            if ignoreunderscore is True:
                ignoreunderscore = False
            else:
                ignoreunderscore = True
        if ignoreunderscore is False and adjusted[i] == '_':
            replacecharacters.append(i)
    for i in range(0, len(replacecharacters)):
        # need to add i since after first replacement, next underscore will be one character later.
        j = replacecharacters[i] + i
        texttoreplace = texttoreplace[0:j] + '\\' + texttoreplace[j:]
    return(texttoreplace)


def tabularconvert(listoflists, colalign = None, hlines = None, savename = None):
    """
    All this does is write out the body of a tabular table (or the full tabular if colalign specified)

    Need to specify full tabular as a list of lists.
    If colalign given, create full tabular
    hlines is something like [0, 1, -1]. 0 means there's an hline before the first line, 1 means there's an hline before the second line, -1 means there's an hline before the last line. Default: []

    Note that I can include \multicolumn{2}{c}{Multi-column} directly as an element in the lists
    """
    if hlines is None:
        hlines = []

    # adjust hlines - replace negative numbers with their equivalent positive numbers
    for i in range(len(hlines)):
        if hlines[i] < 0:
            # if table has 2 rows then hlines = [-1] corresponds to hlines = [-2]
            hlines[i] = len(listoflists) + 1 + hlines[i]

    # convert to string if not done already
    for i in range(len(listoflists)):
        for j in range(len(listoflists[i])):
            listoflists[i][j] = str(listoflists[i][j])
    
    tabular = ''
    for i in range(len(listoflists)):
        if i in hlines:
            tabular = tabular + '\\hline\n'
            
        for j in range(len(listoflists[i])):
            element = replaceunderscores(listoflists[i][j])

            if j < len(listoflists[i]) - 1:
                tabular = tabular + element + ' & '
            else:
                tabular = tabular + element + ' \\\\\n'

    # add final hline if necessary
    if len(listoflists) in hlines:
        tabular = tabular + '\\hline\n'

    if colalign is not None:
        tabular = '\\begin{tabular}{' + colalign + '}\n' + tabular + '\\end{tabular}\n'

    if savename is not None:
        with open(savename, 'w+') as f:
            f.write(tabular)

    return(tabular)


def tabularconvert_example_basic():
    tabular = tabularconvert([['Col1', 'Col2'], ['a', 'b'], ['1', '2']], colalign = '|l|r|', hlines = [0, 1, -1], savename = __projectdir__ / Path('temp/tabularconvert_example_basic.tex'))

    return(tabular)


def tabularconvert_example_multicol():
    listoflists = [['\\multicolumn{2}{|c|}{Cols. 1 and 2}', 'Col3'], ['Col1', 'Col2', 'Col3'], ['a', 'b', 'c'], ['1', '2', '3']]

    # verify printlofl works with multicolumns
    printlofl(listoflists)

    print(tabularconvert(listoflists, colalign = '|c|c|c|', hlines = [0, 1, 2, -1], savename = __projectdir__ / Path('temp/tabularconvert_example_multicol.tex')))


def tabularconvert_example_multirow():
    tabularconvert([['', 'Col1', 'Col2'], ['\\multirow{2}{*}{Letters}', 'a', 'b'], ['', 'A', 'B'], ['Numbers', '1', '2']], colalign = 'lcc', hlines = [0, 1, 3, -1], savename = __projectdir__ / Path('temp/tabularconvert_example_multirow.tex'))


# Merge Tabular Sections:{{{1
def mergetabsecs(tabsecslist, colalign = None, hlines = None, savename = None):
    """
    Merge together a list of tabsecs

    If colalign is specified, return this in tabular form

    The integers for hlines are defined relative to whether there should be hlines between each tabsec rather than between each line of the tabular
    """
    if hlines is None:
        hlines = []
    if hlines == 'all':
        hlines = list(range(len(tabsecslist) + 1))

    tabular = ''
    for i in range(len(tabsecslist)):
        if i in hlines:
            tabular = tabular + '\\hline\n'
        tabular = tabular + tabsecslist[i]
    if len(tabsecslist) in hlines:
        tabular = tabular + '\\hline\n'

    # return full tabular if specify colalign
    if colalign is not None:
        tabular = '\\begin{tabular}{' + colalign + '}\n' + tabular + '\\end{tabular}\n'

    if savename is not None:
        with open(savename, 'w+') as f:
            f.write(tabular)

    return(tabular)


def mergetabsecs_test():
    title_lofl = [['col1', 'col2']]
    tabsec1 = tabularconvert(title_lofl, hlines = None)
    elements_lofl = [[0, 1], [2, 3]]
    tabsec2 = tabularconvert(elements_lofl, hlines = [1])

    tabsecslist = [tabsec1, tabsec2]
    
    mergetabsecs(tabsecslist, colalign = '|c|c|', hlines = 'all', savename = __projectdir__ / Path('temp/example_mergetabsecs.tex'))

# Vcoeff LofL:{{{1
def getcoefftabmatrixgen(
    # matrix inputs
    coeffnames, betamatrix, pvalmatrix, sematrix,
    # format options
    stardict = 'def', coeffdecimal = 3,
    # print options
    printtab = False, printmaxcolsize = None,
    ):
    """
    Convert betas, pvals and ses into a listoflists
    I can then easily convert this into tabular

    Basic matrices:
    coeffnames: list of names I want to put in tabular
    betamatrix: matrix of betas
    pvalmatrix: matrix of pvalues
    sematrix: matrix of standard errors

    format options:
    stardict = 'def' then use {0.05: '*', 0.01: '**', 0.001: '***'}

    print options:
    printtab: print out the listoflists
    printmaxcolsize = None then just use actual length. If [None, 10] then no restriction on first column but second is shortened to 10 characters long
    """
    # include 0.1
    if stardict == 'def':
        stardict = stardict_default
    # do not include 0.1
    if stardict == 'def2':
        stardict = stardict_default2

    # verify coefftablenames same length as number of rows in betamatrix
    if len(coeffnames) != len(betamatrix):
        raise ValueError('coefftablenames is the wrong length')

    # get lengths of rows and columns
    numvars = len(betamatrix)
    # need to add 1 for the row index
    nummodels = len(betamatrix[0])
    numcol = nummodels + 1

    # create empty list
    coefftabmatrix = [None] * (numvars * 2 * numcol)
    # reshape as coefftabmatrix
    coefftabmatrix = [coefftabmatrix[i: i + numcol] for i in range(0, len(coefftabmatrix), numcol)]
    
    for i in range(numvars):
        # add first elements
        coefftabmatrix[i * 2][0] = coeffnames[i]
        coefftabmatrix[i * 2 + 1][0] = ''
        for j in range(nummodels):
            if betamatrix[i][j] is None:
                coefftabmatrix[i * 2][j + 1] = ''
                coefftabmatrix[i * 2 + 1][j + 1] = ''
            else:
                coeffstr = str(round(decimal.Decimal(betamatrix[i][j]), coeffdecimal))
                sdstr = str(round(decimal.Decimal(sematrix[i][j]), coeffdecimal))

                pval = pvalmatrix[i][j]
                # start with no symbol for the case where the pvalue is 1
                pvalstr = ''
                siglevelcurrent = 1
                for siglevel in stardict:
                    # replace if the degree of significance is lower than before and pvalue meets it
                    if pval < siglevel and siglevel < siglevelcurrent:
                        pvalstr = stardict[siglevel]

                coefftabmatrix[i * 2][j + 1] = coeffstr + pvalstr
                coefftabmatrix[i * 2 + 1][j + 1] = '(' + sdstr + ')'

    if printtab is True:
        printlofl(coefftabmatrix, maxcolsize = printmaxcolsize)

    return(coefftabmatrix)


    
def getvcoeff_lofl_test():
    betamatrix = [[0.03, 0.22398472], [None, 0.1]]
    pvalmatrix = [[0.03, 0.000222], [None, 0.9]]
    sematrix = [[0.05, 0.012], [None, 0.87629273]]
    coefflist = ['beta1', 'beta2']

    # decimals
    coeffdecimal = 5
    # coeffdecimal = None

    lofl = getcoefftabmatrixgen(coefflist, betamatrix, pvalmatrix, sematrix, coeffdecimal = coeffdecimal)
    printlofl(lofl)

# Other Basic Latex Create:{{{1
def convertformatnumericmatrix(matrix, decimalpoints = None):
    """
    Convert into a numeric matrix and add decimals.

    Can input in three forms:
        Integer (all elements in matrix have the number of decimals of the integer).
        List of length of number of rows (all elements in row have number of decimals of corresponding point in list)
        List of lists of same dimension as matrix.

    Can also specify that some elements ignored i.e. [None, 3]

    Note that decimalpoints = 0 gives integers.

    Give default argument of decimalpoints as None since easier to work with argparse.
    """
    import decimal

    # if decimalpoints is None:
    #     decimalpoints = coeffdecimal_default
    
    if not isinstance(decimalpoints, list):
        decimalpoints = [decimalpoints] * len(matrix)

    # for col in range(0, len(matrix[0])):
    #     if decimalpoints[col] is None:
    #         continue
    #     for row in range(0, len(matrix)):
    #         # ignore blank space since want option to be able to include nothing in row/column of matrix i.e. regression where don't include coefficient
    #         if matrix[row][col] != "":
    #             matrix[row][col] = round(decimal.Decimal(matrix[row][col]), decimalpoints[col])

    if not isinstance(decimalpoints[0], list):
        for i in range(len(decimalpoints)):
            decimalpoints[i] = [decimalpoints[i]] * len(matrix[i])

    for row in range(0, len(matrix)):
        for col in range(0, len(matrix[0])):
            # ignore blank space since want option to be able to include nothing in row/column of matrix i.e. regression where don't include coefficient
            if decimalpoints[row][col] is None or matrix[row][col] == "":
                continue
            matrix[row][col] = round(decimal.Decimal(matrix[row][col]), decimalpoints[row][col])

    return(matrix)
            
    
def genbasicmatrix(matrix, matrixname = 'pmatrix', decimalpoints = None):
    import numpy as np

    # convert a list to a list of lists
    # so a list is printed as a vector
    # don't think need nparray part
    # if isinstance(matrix[0], (str, float, int)) and not isinstance(matrix[0], np.ndarray):
    if isinstance(matrix[0], (str, float, int)):
        matrix = [[matrix[i]] for i in range(0, len(matrix))]

    # convert decimal points
    if decimalpoints is not None:
        matrix = convertformatnumericmatrix(matrix, decimalpoints = decimalpoints)
    output = '\\begin{' + matrixname + '}\n'
    for i in range(0, len(matrix)):
        for j in range(0, len(matrix[0])):
            output = output + str(matrix[i][j])

            if j != (len(matrix[0]) - 1):
                output = output + ' & '
        output = output + ' \\\\\n'

    output = output + '\\end{' + matrixname + '}\n'

    return(output)
            

