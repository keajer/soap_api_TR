# -*- coding: utf-8 -*-
# this script contact Thomson Reuters' server again and retrieve reference info based on UIDs 

# first load the json file generated from search run XML fils into a dictionary
def opener(jsonFile):
    recJson = open(jsonFile, 'rU')
    records = json.loads(recJson.read())
    recJson.close()
    return records

# this functon is to conver docid to uid with another search operation
def convertID(query, client):
    retriPara = dict()
    retriPara['option'] = {'key': 'RecordIDs', 'value': 'On'}
    retriPara['firstRecord'] = 1
    retriPara['count'] = 100
    queryPara = dict()
    queryPara['databaseId'] = 'WOS'
    queryPara['userQuery'] = query
    queryPara['queryLanguage'] = 'en'
    result = client.service.search(queryPara, retriPara)
    if result['recordsFound'] != 0:
        uid = result['optionValue'][0]['value']
        return uid

def main(records):
    # make all the UIDs from the dictionary into a list
    UIDs = records.keys() 

    # create a dictionary to store the reference retrieve result with respect to each UID
    refBank = dict()

    # below two lines are to check the info sent out and sent back with the SOAP server in terminal
    # logging.basicConfig(level=logging.INFO)
    # logging.getLogger('suds.client').setLevel(logging.DEBUG)

    # run authentication to get session ID
    url = 'http://search.webofknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'
    client = suds.client.Client(url)
    SID = client.service.authenticate()

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

    # run through all the uids and get reference id, also filter out non or single references
    # append a list of the reference ids to the records dictionary at the end
    for uid in UIDs:
        retrievePara['firstRecord'] = 1
        result = client.service.citedReferences(databaseId, uid, queryLanguage, retrievePara)
        time.sleep(1)
        if result['recordsFound'] != 0:
            refBank[uid] = [dict(rec) for rec in result['references']] # store the reference results as a list into the refBank
        else:
            refBank[uid] = []
        if result['recordsFound'] < 2: # remove the single reference records
            records.pop(uid)
            continue
        elif result['recordsFound'] > 100: # use retrive function to get rest of the reference ids
            docIDs = [ref['docid'] for ref in result['references'] if ref['hot'] == 'yes']
            if docIDs != []:
                query = 'DOCID=(' + ' or '.join(docIDs) + ')'
                uIDs = convertID(query, client)
            else:
                uIDs = []
            queryID = result['queryId'] 
            if result['recordsFound'] % 100 == 0:
                runTimes = result['recordsFound'] / 100 - 1
            else:
                runTimes = result['recordsFound'] / 100
            for i in range(runTimes):
                retrievePara['firstRecord'] = (i+1) * 100 + 1
                result = client.service.citedReferencesRetrieve(queryID, retrievePara)
                time.sleep(1)
                refBank[uid] += [dict(rec) for rec in result] # extend reference results into refBank
                docIDs = [ref['docid'] for ref in result if ref['hot'] == 'yes']
                if docIDs != []:
                    query = 'DOCID=(' + ' or '.join(docIDs) + ')'
                    iterUIDs = convertID(query, client)
                    if uIDs:
                        if iterUIDs:
                            uIDs += iterUIDs
                    else:
                        if iterUIDs:
                            uIDs = iterUIDs
        else:
            docIDs = [ref['docid'] for ref in result['references'] if ref['hot'] == 'yes']
            if docIDs != []:
                # print uid, docIDs
                query = 'DOCID=(' + ' or '.join(docIDs) + ')'
                uIDs = convertID(query, client)
            else:
                uIDs = []
        if uIDs:
            records[uid].append(uIDs)
        else:
            records[uid].append([])

    return (records, refBank)

if __name__ == '__main__':
    import logging, suds, json, time, glob
    from bs4 import BeautifulSoup
    fileNames = glob.glob('*.json')
   
    # running the retrieving process
    for f in fileNames:
        print f
        # track the time
        start = time.time()

        records = opener(f)
        newRec, refBank = main(records)

        # output new recodes as a updated json file
        with open('new_'+f, 'wb') as output:
            json.dump(newRec, output, indent = 2)
        output.close()

        # append reference_bank with json strings each string contains refs for one UID
        with open('reference_bank.json', 'ab+') as refOut:
            for uid, refs in refBank.iteritems():
                json.dump({uid: refs}, refOut)
                refOut.write('\n')
        refOut.close()
        print 'It took', time.time() - start, 'seconds.'
