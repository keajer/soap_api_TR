# -*- coding: utf-8 -*-
# this script contact Thomson Reuters' server again and retrieve reference info based on UIDs 
import logging, suds, json, time
from bs4 import BeautifulSoup

# first load the json file generated from search run XML fils into a dictionary
recJson = open('test.json', 'rU')
records = json.loads(recJson.read())
recJson.close()

# make all the UIDs from the dictionary into a list
UIDs = records.keys() 

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
# setup retrieve parameters, always do 100 counts of records and do hot key
# will assign firstRecord in for loop
retrievePara = dict()
retrievePara['count'] = 100
retrievePara['option'] = {'key': 'Hot', 'value': 'On'}

databaseId = 'WOS'
queryLanguage = 'en'


# uid = 'WOS:A1991GU68500018'
# result = client.service.citedReferences(databaseId, uid, queryLanguage, retrievePara)
# print result['recordsFound'] 

# run through all the uids and get reference id, also filter out non or single references
# append a list of the reference ids to the records dictionary at the end
for uid in UIDs:
    retrievePara['firstRecord'] = 1
    result = client.service.citedReferences(databaseId, uid, queryLanguage, retrievePara)
    if result['recordsFound'] < 2: # remove the single reference records
        records.pop(uid)
    elif result['recordsFound'] > 100: # use retrive function to get rest of the reference ids
        records[uid].append([ref['docid'] for ref in result['references']])
        queryID = result['queryId'] 
        if result['recordsFound'] % 100 == 0:
            runTimes = result['recordsFound'] / 100 - 1
        else:
            runTimes = result['recordsFound'] / 100
        for i in range(runTimes):
            retrievePara['firstRecord'] = (i+1) * 100 + 1
            result = client.service.citedReferencesRetrieve(queryID, retrievePara)
            records[uid][-1].append([ref['docid'] for ref in result])
            time.sleep(1)
    else:
        records[uid].append([ref['docid'] for ref in result['references']])
    time.sleep(1)

# output as a updated json file
with open('test2.json', 'wb') as output:
    json.dump(records, output, indent = 2)
output.close()    
