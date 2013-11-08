# used the core author information and run through the field-related xml files to get 
# output file and author information
#to parse xml file into field data
import glob
import cPickle as pickle
from bs4 import BeautifulSoup

fileNames = glob.glob('*.xml')
output = open('output.txt', 'wb')
auFile = open('auid.pck', 'rU').read()
auid_set = pickle.loads(auFile)

ArAuDic = {}
auSet = set()
#both below are for summary of publications between 1991 and 2010
pub_counter = 0
au_counter = 0
ref_list = [] #a list with the number of references for each publication
ref_percent_list = []# a list with the percentages of references with ids

summary = open('summary.txt', 'wb')

for f in fileNames:
    xml = open(f, 'rU').read()
    soup = BeautifulSoup(xml)
    for ar in soup.findAll('article_rec'):
        auid_list = []
        Aus =  ar.findAll('au')
        ref_counter = 0
        for au in Aus:
            if au.find('person_id'):
                auid_list.append(au.find('person_id').text)
        if any((au in auid_set) for au in auid_list):
            year = ar.find('article_publication_date').text[-4:]
            if year != '':
                if 1991 <= int(year) <= 2010:
                    output.write('ID ' + ar.find('article_id').text + '\n')
                    output.write('CI 0' + '\n')
                    if soup.find('series_title'):
                        output.write('SO ' + soup.find('series_title').text + '\n')
                    else:
                        output.write('SO ' + soup.find('proc_title').text + '\n')
                    output.write('TI ' + ar.find('title').text + '\n')
                    if ar.find('page_from') and ar.find('page_to'):
                        output.write('BI ' + soup.find('proc_desc').text + ': ' + ar.find('page_from').text + '-' + ar.find('page_to').text + ' ' + ar.find('article_publication_date').text + '\n')
                    else:
                        output.write('BI ' + soup.find('proc_desc').text + ': ' + ar.find('article_publication_date').text + '\n')    
                    Aus =  ar.findAll('au')
                    aus = []
                    for au in Aus:
                        if au.find('person_id'):
                            auSet.add(au.find('person_id').text)
                            aus.append([au.find('last_name').text + ', ' + au.find('first_name').text, au.find('person_id').text])
                    ArAuDic[ar.find('article_id').text] = aus
                    if len(Aus) > 1:
                        output.write('AU ' + Aus[0].find('last_name').text + ', ' + Aus[0].find('first_name').text[0] + '\n')
                        for au in Aus[1:]:
                            output.write(' ' + au.find('last_name').text + ', ' + au.find('first_name').text[0] + '\n')
                    else:
                        output.write('AU ' + Aus[0].find('last_name').text + ', ' + Aus[0].find('first_name').text[0] + '\n')
                    for au in Aus:
                        if au.find('affiliation'):
                            output.write('AF ' + au.find('affiliation').text + '\n')
                    Ref = ar.findAll('ref')
                    ref_list.append(len(Ref))
                    for ref in Ref:
                        if ref.find('ref_obj_id'):
                            ref_counter += 1
                            output.write('RF ' + ref.find('ref_obj_id').text + '\n')        
                    if len(Ref) != 0:
                        ref_percent_list.append(ref_counter / float(len(Ref)))
                    else:
                        ref_percent_list.append(0)
                    Cat = ar.findAll('cat_node')
                    for cat in Cat:
                        output.write('CA ' + cat.text + '\n')

                    pub_counter += 1
                    au_counter += len(Aus)
                    output.write('\n')
output.close()

summary.write('Number of Publications: ' + str(pub_counter) + '\n' + 'Number of Authors: ' + str(au_counter) + '\n')
summary.write('Number of Unique Authors: ' + str(len(auSet)) + '\n' + '\n' + '\n')
summary.write('The list of number of references: ' + '\n')
for i in ref_list:
    summary.write(str(i) + '\t')

summary.write('\n' + '\n' + 'The list of percentages of references with ids: ' + '\n')
for i in ref_percent_list:
    summary.write(str(i) + '\t')

summary.close()

with open('author-identities.pck', 'wb') as auid:
    pickle.dump(ArAuDic, auid)
