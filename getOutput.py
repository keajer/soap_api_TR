# this script get all the fully loaded json files into two files:
# one is the combined output as a json string for all the recordes
# the other file is the final output in the format below
# ID 151890433
# CI 0 
# SO JOURNAL OF THE AMERICAN CHEMICAL SOCIETY
# TI Ultrafast energy migration in chromophore shell-metal nanoparticle assemblies         
# BI 128 (34): 10988-10989 AUG 30 2006
# PY 2006
# AU RANASINGHE, M
#  BAUER, CA
# AF Univ Michigan
# CT Ann Arbor
# CO USA
# RF 125503306
# RF 123456789
# CA Chemistry, Multidisciplinary

import json, glob

# formalize the name to be "last name, first initials"
# def formalName(string):
#     intake = string.split(', ')
#     if len(intake) == 1:
#         name = intake[0]
#     else:
#         last = intake[0] + ', '
#         first = ''.join([f for f in intake[1] if f.isupper()])
#         name = last + first
#     return name

def writeOut(fileName, output):
    f = open(fileName, 'rU')
    records = json.loads(f.read())
    f.close()
    for key, val in records.iteritems():
        output.write('ID ' + key.split(':')[1] + '\n')
        output.write('CI ' + val[1] + '\n')
        output.write('SO ' + val[2] + '\n')
        output.write('TI ' + val[3] + '\n')
        output.write('BI ' + val[4] + '\n')
        output.write('PY ' + val[0] + '\n')
        output.write('AU ' + val[5][0] + '\n')
        for au in val[5][1:]:
            output.write('   ' + au + '\n')
        for co in val[6]:
            output.write('CO ' + co + '\n')
        for ref in val[10]:
            output.write('RF ' + ref.split(':')[1] + '\n')
        for sc in val[9]:
            output.write('CA ' + sc + '\n')
        output.write('\n')

def combine(fileName, recordDict):
    f = open(fileName, 'rU')
    records = json.loads(f.read())
    f.close()
    for key, val in records.iteritems():
        recordDict[key] = val
    return recordDict

if __name__ == '__main__':    
    fileNames = glob.glob('new_*.json')
    recordDict = dict()
    for name in fileNames:
        print name
        with open('output.txt', 'ab+') as output1:
            writeOut(name, output1)
        output1.close()
        combine(name, recordDict)
    with open('all_records.json', 'wb') as output2:
        json.dump(recordDict, output2, indent = 2)
    output2.close()

