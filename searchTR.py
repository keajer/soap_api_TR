# -*- coding: utf-8 -*-
import logging, suds
from bs4 import BeautifulSoup

# below two lines are to check the info sent out and sent back with the server
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

# run authentication to get session ID
url = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
client = suds.client.Client(url)
SID = client.service.authenticate()
print SID
# print client.service.closeSession()

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
queryPara['userQuery'] = 'TS=(ocean* OR sea OR marine) AND TS=(acoustic* OR glider* OR observat* OR hydrothermal OR ridge OR chimn* OR tectonic plate* OR volcano* OR flange* OR moor* OR sensor* or therm* OR heat* OR air-sea OR climate OR tidal OR tide* OR circulat* OR surface OR salinity OR current* OR abyss* OR profiler) NOT TS=(biology OR biological OR paleobiolog* OR biochemical OR chemical OR chemistry OR organism* OR zooplankton OR phytoplankton OR turbines OR particle-tracking OR bacteri* OR vertebrate OR isotop* OR marine-invertebrates OR harvest*)  AND PY=(1991)'
queryPara['editions'] = {'collection': 'WOS', 'edition': 'SCI'}
queryPara['timeSpan'] = {'begin': '1991-01-01', 'end': '1991-12-31'}
queryPara['queryLanguage'] = 'en'
result = client.service.search(queryPara, retrievePara)
soup = BeautifulSoup(result['records']) # soup first round of records

queryID = result['queryId'] # queryID will be used in following retrieving
numberFound = result['recordsFound'] # get total number of records 3422
if numberFound % 100 == 0:
    runTimes = numberFound / 100 - 1
else:
    runTimes = numberFound / 100
    lastrunCount = numberFound % 100

outputNames = []
for i in range(runTimes):
    outputNames.append('1991-' + str(i*100 + 1) + '-' + str((i+1)*100) + '.xml')
if lastrunCount:
    outputNames.append('1991-' + str(runTimes*100 + 1) + '-' + str(runTimes*100 + lastrunCount) + '.xml')

output = open(outputNames[0], 'wb') # out write the first search
output.write(soup.prettify())
output.close()

# do the following run times
if lastrunCount:
    for i in range(runTimes - 1):
        retrievePara['firstRecord'] = (i+1) * 100 + 1
        soup = BeautifulSoup(client.service.retrieve(queryID, retrievePara)['records'])
        output = open(outputNames[i + 1], 'wb')
        output.write(soup.prettify())
        output.close()
    retrievePara['firstRecord'] = runTimes * 100 + 1
    retrievePara['count'] = lastrunCount # reset the record count to the remaining counts
    soup = BeautifulSoup(client.service.retrieve(queryID, retrievePara)['records'])
    output = open(outputNames[-1], 'wb')
    output.write(soup.prettify())
    output.close()
else:
    for i in range(runTimes):
        retrievePara['firstRecord'] = (i+1) * 100 + 1
        soup = BeautifulSoup(client.service.retrieve(queryID, retrievePara)['records'])
        output = open(outputNames[i + 1], 'wb')
        output.write(soup.prettify())
        output.close()
