import urllib
#import urllib2
#import requests
#from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
#from .firefox.webdriver import WebDriver as Firefox
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("infile", type=str,
                    help="input xlsx file")
#parser.add_argument("--nqueries", type=int, 
#                    help="number of lines to be read from input file", default=10)
parser.add_argument("--firstRow", type=int, 
                    help="first row to be considered in the input file", default=1)
parser.add_argument("--lastRow", type=int, 
                    help="last row to be considered in the input file", default=11)

url = "http://cti.voa.gov.uk/cti/inits.asp"
fin_name = 'PricePaidVittorio.csv'
inlines = []
with open(fin_name, 'r') as fin:
    inlines = fin.readlines()

result=[]
for myline in inlines[1:]:
    myline = myline.replace('"','').split(',')
    print(myline)
    postcode = myline[3]#'SE1 0AJ'
    address = ' '.join(myline[7:10])
    print(address)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    #options = webdriver.ChromeOptions()
    #options.add_argument("--remote-debugging-port=9222")
    #options.headless = True
    driver = webdriver.Chrome("chromedriver", chrome_options=chrome_options)#, options=options)
    driver.get(url)
    txtPC = driver.find_element_by_name("txtPostCode")
    driver.execute_script('arguments[0].value = arguments[1]', txtPC, postcode)
    driver.find_element_by_id('frmInitSForm').submit()
    scl_complex = driver.find_element_by_class_name('scl_complex')
    oldtext = scl_complex.text
    #print(oldtext)
    newtext = ""
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
    for line in lines:
        ls = line.split(' ')
        t = (' '.join(ls[:-2]), ls[-2], ls[-1])
        res.append(t)
	
    answer='notFound'
    for t in res:
        if t[0].split(',')[0] == myline[7]:
            print(t[0])
            print(myline[7])
            answer=t[1]
            break
    print('Line, Answer: %s, %s'%(myline,answer))        
	#with open('search_%s.csv'%postcode, 'w') as fout:
	#    for t in res:
	#        fout.write('%s,%s,%s\n'%(t[0].replace(',',''),t[1],t[2]))




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
