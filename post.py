import urllib
import selenium
from selenium import webdriver
import argparse
import sys
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument("infile", type=str,
                    help="input xlsx file")
parser.add_argument("--firstRow", type=int, 
                    help="first row to be considered in the input file", default=1)
parser.add_argument("--lastRow", type=int, 
                    help="last row to be considered in the input file", default=11)
args = parser.parse_args()
url = "http://cti.voa.gov.uk/cti/inits.asp"
fin_name = args.infile
inlines = []
with open(fin_name, 'r') as fin:
    inlines = fin.readlines()

nlines = len(inlines[args.firstRow:args.lastRow])

result=[]
startT = time.time()
for il,myline in enumerate(inlines[args.firstRow:args.lastRow]):
    #print progress bar
    os.system("clear")
    progress = float(il+1)/float(nlines)*100
    sys.stdout.write('\r')
    sys.stdout.write("[%-20s] %.2f%%, %i/%i, %is elapsed." % ('='*int((il+1)*20/(nlines)), progress, il+1, nlines, time.time()-startT))
    sys.stdout.flush()
    print()  
    myline = myline.replace('"','').split(',')
    print(myline)
    postcode = myline[3]#'SE1 0AJ'
    address = ' '.join(myline[7:10])
    print(address)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    try:
        driver = webdriver.Chrome("chromedriver", chrome_options=chrome_options)#, options=options)
        driver.get(url)
        txtPC = driver.find_element_by_name("txtPostCode")
        driver.execute_script('arguments[0].value = arguments[1]', txtPC, postcode)
        driver.find_element_by_id('frmInitSForm').submit()
        scl_complex = driver.find_element_by_class_name('scl_complex')
    except:# selenium.common.exceptions.TimeoutException:
        print('[ERROR] Something went wrong with this research. No response obtained for this entry, moving to the next one...')
        if 'driver' in locals():
            driver.close()
        continue
    oldtext = scl_complex.text if 'scl_complex' in locals() else ''
    if oldtext == '':
        answer='notFound'
        result.append(answer)
        print('Line, Answer: %s, %s'%(myline,answer))
        print()
        continue
    while True:
        try:
            a = driver.execute_script("Next();")
            scl_complex = driver.find_element_by_class_name('scl_complex')
            oldtext = oldtext +'\n'+ scl_complex.text
        except selenium.common.exceptions.JavascriptException:
            break
    driver.quit()
    oldtext = oldtext.replace('Address Council Tax band Improvement indicator Local authority reference number\n','')
    while '  ' in oldtext:
        oldtext = oldtext.replace('  ',' ')
    lines = oldtext.split('\n')
    res=[]
    if 'Local authority name' in oldtext:
      answer='notFound'
      result.append(answer)
      print('Line, Answer: %s, %s'%(myline,answer))        
      print()   
      continue  
    for line in lines:
        ls = line.split(' ')
        t = (' '.join(ls[:-2]), ls[-2], ls[-1])
        res.append(t)
	
    answer='notFound'
    for t in res:
        #compare to PAON
        if t[0].split(',')[0] == myline[7]:
            print(t[0])
            print(myline[7])
            answer=t[1]
            break
    if answer=='notFound':
        for t in res:
            #if still not found, compare to SAON
            if t[0].split(',')[0] == myline[8]:
                print(t[0])
                print(myline[8])
                answer=t[1]
                break
    if answer=='notFound':
        for t in res:
            #if still again not found, allow partial match to SAON
            if t[0].split(',')[0] in myline[8].split():
                print(t[0])
                print(myline[8])
                answer=t[1]
                break        
    result.append(answer)
    print('Line, Answer: %s, %s'%(myline,answer))        
    print()
    
with open('search_lines%sto%s.csv'%(str(args.firstRow),str(args.lastRow)), 'w') as fout:
    fout.write('%s,"CouncilTaxBandFromCrawler"\n'%(inlines[0].replace('\n','')))
    for l,t in zip(inlines[args.firstRow:args.lastRow],result):
        fout.write('%s,%s\n'%(l.replace('\n',''),t))




#s = requests.Session()
#page = s.get("http://cti.voa.gov.uk/cti/inits.asp")
##soup = BeautifulSoup(page.content)
##url = "http://cti.voa.gov.uk/cti/inits.asp"
#payload = {'txtPostCode':'SE1 0AJ'}
#r = s.post('http://cti.voa.gov.uk/cti/inits.asp', payload)
#print(r.json())
#with open("requests_results.html", "w") as f:
#    l = '"""'+str(r.content)+'"""'
#    f.write(l)
