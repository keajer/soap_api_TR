# -*- coding: utf-8 -*-
# this script is to parse Thomson Reuters' XML records in a folder into a desided ouput below
# <uid> -> ID
# <pub_info [...] pubyear="1991"> -> PY
# <dynamic_data><citation_related><tc_list><silo_tc coll_id="WOS" local_count="5">-> CI
# <title type="source">TITLE -> SO
# <title type="item">TITLE</title> -> TI
#  <item xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="itemType_wos"> <bib_id> 38 (12): 1431-1438 DEC 1991 -> BI
# <name dais_id="2514916" role="author" seq_no="1"><full_name> SURNAME, XX -> AU
#  <addresses count="1"> <address_name> <address_spec addr_no="1"><country>INDIA -> CO
# <doctype>Article -> DT 
# <fullrecord_metadata> <abstracts count="1"> <abstract>  <abstract_text count="1"> <p> xyz -> AB
# <subject ascatype="traditional">Chemistry, Analytical -> SC

# output is in dictionary format and will be saved in json:
# {uid: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}
# 0: py
# 1: ci
# 2: so
# 3: ti
# 4: bi
# 5: au[]
# 6: co[]
# 7: dt[]
# 8: ab
# 9: sc[]
# 10: ref[] # ref list will be updated later after run through refRetriTR.py

# it also cuts data in pieces with 1000 publications each
def main(inputNames, outputName):
    records = dict()
    for f in inputNames:
        xml = open(f, 'rU')
        soup = BeautifulSoup(xml.read())
        xml.close()
        for rec in soup.findAll('rec'):
            if rec.find('full_name').text.strip() != '[Anonymous]':
                uid = rec.find('uid').text.strip()
                records[uid] = []
                py = rec.find('pub_info')['pubyear']
                ci = rec.find('silo_tc')['local_count']
                so = rec.find('title', {'type': 'source'}).text.strip()
                ti = rec.find('title', {'type': 'item'}).text.strip()
                bi = rec.find('bib_id').text.strip()
                aus = []
                for au in rec.findAll('names')[0].findAll('wos_standard'):
                    au = au.text.strip()
                    aus.append(au)
                cos = []
                for co in rec.find('addresses').findAll('country'):
                    cos.append(co.text.strip())
                dts = []
                for dt in rec.find('doctypes').findAll('doctype'):
                    dts.append(dt.text.strip())
                if rec.find('fullrecord_metadata').find('abstract_text'):
                    ab = '\n'.join([p.text.strip() for p in rec.find('fullrecord_metadata').find('abstract_text').findAll('p')])
                else:
                    ab = ''
                scs = []
                if rec.find('subjects'):
                    for sc in rec.find('subjects').findAll('subject'):
                        scs.append(sc.text.strip())

                records[uid] = [py, ci, so, ti, bi, aus, cos, dts, ab, scs]

                # filter out astronomy ariticles from total records
                subjects = rec.find('subjects')
                if subjects:
                    subjs = subjects.findAll('subject')
                traidSubjs = [subj.text.strip() for subj in subjs if subj['ascatype'] == 'traditional']
                if any('astronomy' in sub.lower() for sub in traidSubjs):
                    # print traidSubjs
                    records.pop(uid)
                else:
                    records[uid][5] = aus


    with open(outputName + '.json', 'wb') as output:
        json.dump(records, output, indent = 2)
    output.close()    

if __name__ == '__main__':
    import glob, json
    from bs4 import BeautifulSoup

    fileNames = glob.glob('*.xml')
    for i in range(len(fileNames) / 10 + 1):
        print i
        inputNames = fileNames[i*10:i*10+10]
        outputName = 'Record' + str(i)
        main(inputNames, outputName)
