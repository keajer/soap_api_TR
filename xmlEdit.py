import glob, json
from bs4 import BeautifulSoup

recordeFile = open('all_records.json', 'rU')
records = json.loads(recordeFile.read())
recordeFile.close()

fileNames = glob.glob('*.xml')
for f in fileNames:
    print f
    xml = open(f, 'rU')
    soup = BeautifulSoup(xml.read())
    xml.close()
    for rec in soup.findAll('rec'):
        if rec.find('full_name').text.strip() != '[Anonymous]':
            uid = rec.find('uid').text.strip()
            if uid in records:
                # change names to WOS standard
                aus = []
                for au in rec.findAll('names')[0].findAll('wos_standard'):
                    au = au.text.strip()
                    aus.append(au)

                # # only takes English primary recors into output
                # primLangs = []
                # langs = rec.find('languages').findAll('language')
                # for lang in langs:
                #     if lang['type'] == 'primary':
                #         primLangs.append(lang.text.strip())
                # if 'English' not in primLangs:
                #     records.pop(uid)
                # else:
                #     records[uid][5] = aus

                # filter out astronomy ariticles from total records
                subjects = rec.find('subjects')
                if subjects:
                    subjs = subjects.findAll('subject')
                traidSubjs = [subj.text.strip() for subj in subjs if subj['ascatype'] == 'traditional']
                if any('astronomy' in sub.lower() for sub in traidSubjs):
                    print traidSubjs
                    records.pop(uid)
                else:
                    records[uid][5] = aus

with open('all_recordes1.json', 'wb') as output:
    json.dump(records, output, indent = 2)
output.close()

