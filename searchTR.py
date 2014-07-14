# -*- coding: utf-8 -*-
import logging, suds
from bs4 import BeautifulSoup

def getSID():
    # run authentication to get session ID
    url = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
    client = suds.client.Client(url)
    SID = client.service.authenticate()
    return SID
    # print client.service.closeSession()

def getResult(year, SID):
    print year
    # below two lines are to check the info sent out and sent back with the server
    # logging.basicConfig(level=logging.INFO)
    # logging.getLogger('suds.client').setLevel(logging.DEBUG)

    # start the TR search server and send session ID in http header
    url = 'http://search.webofknowledge.com/esti/wokmws/ws/WokSearch?wsdl'
    client = suds.client.Client(url, headers={'Cookie': 'SID="' + SID + '"'})

    # print client
    retrievePara = dict()
    retrievePara['firstRecord'] = 1
    retrievePara['count'] = 100
    # result = client.service.retrieveById('WOS', ['WOS:000270372400005'], 'en', retrievePara)

    queryPara = dict()
    queryPara['databaseId'] = 'WOS'
    queryPara['userQuery'] = 'AU=SCHROCK, R'
    queryPara['editions'] = {'collection': 'WOS', 'edition': 'SCI'}
    queryPara['timeSpan'] = {'begin': year + '-01-01', 'end': year + '-12-31'}
    queryPara['queryLanguage'] = 'en'
    result = client.service.search(queryPara, retrievePara)
    soup = BeautifulSoup(result['records'].encode('raw_unicode_escape')) # soup first round of records

    queryID = result['queryId'] # queryID will be used in following retrieving
    numberFound = result['recordsFound'] # get total number of records 3422
    if numberFound % 100 == 0:
        runTimes = numberFound / 100 - 1
        lastrunCount = 0
    else:
        runTimes = numberFound / 100
        lastrunCount = numberFound % 100

    outputNames = []
    for i in range(runTimes):
        outputNames.append(year + '-' + str(i*100 + 1) + '-' + str((i+1)*100) + '.xml')
    if lastrunCount != 0:
        outputNames.append(year + '-' + str(runTimes*100 + 1) + '-' + str(runTimes*100 + lastrunCount) + '.xml')
    if len(outputNames) == 0:
        print 'Search did not find anything..'
    else:
        output = open(outputNames[0], 'wb') # out write the first search
        output.write(soup.prettify())
        output.close()

        # do the following run times
        if lastrunCount:
            for i in range(runTimes - 1):
                retrievePara['firstRecord'] = (i+1) * 100 + 1
                soup = BeautifulSoup(client.service.retrieve(queryID, retrievePara)['records'].encode('raw_unicode_escape'))
                output = open(outputNames[i + 1], 'wb')
                output.write(soup.prettify())
                output.close()
            retrievePara['firstRecord'] = runTimes * 100 + 1
            retrievePara['count'] = lastrunCount # reset the record count to the remaining counts
            soup = BeautifulSoup(client.service.retrieve(queryID, retrievePara)['records'].encode('raw_unicode_escape'))
            output = open(outputNames[-1], 'wb')
            output.write(soup.prettify())
            output.close()
        else:
            for i in range(runTimes - 1):
                retrievePara['firstRecord'] = (i+1) * 100 + 1
                soup = BeautifulSoup(client.service.retrieve(queryID, retrievePara)['records'].encode('raw_unicode_escape'))
                output = open(outputNames[i + 1], 'wb')
                output.write(soup.prettify())
                output.close()
            
if __name__ == '__main__':
    import time
    SID = getSID()
    for yr in range(1991, 1993):
        getResult(str(yr), SID)
        time.sleep(1)
