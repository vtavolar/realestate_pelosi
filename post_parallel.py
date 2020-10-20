import urllib
import selenium
from selenium import webdriver
import argparse
import sys
import os
import time
import multiprocessing

parser = argparse.ArgumentParser()
parser.add_argument("infile", type=str,
                    help="input xlsx file")
parser.add_argument("--firstRow", type=int, 
                    help="first row to be considered in the input file", default=1)
parser.add_argument("--lastRow", type=int, 
                    help="last row to be considered in the input file", default=11)
args = parser.parse_args()

from .search import searchLine

url = "http://cti.voa.gov.uk/cti/inits.asp"
fin_name = args.infile
inlines = []
with open(fin_name, 'r') as fin:
    inlines = fin.readlines()

nlines = len(inlines[args.firstRow:args.lastRow])

result=[]
startT = time.time()
pool = multiprocessing.Pool(4)
result  = pool.map(searchLine, inlines[args.firstRow:args.lastRow])
#for il,myline in enumerate(inlines[args.firstRow:args.lastRow]):

    
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
