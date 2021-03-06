import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

browser_options = Options()
browser_options.headless = True
browser_options.add_argument('--no-sandbox')
browser_options.add_argument('--disable-dev-shm-usage')


def searchLine(myline, url="http://cti.voa.gov.uk/cti/inits.asp", browser_options=browser_options):
    myline = myline.replace('"','').split(',')
    if len(myline)!=16:
        print('[FATAL] Wrong format of input data, cannot perform research.')
        return 'fatalErr'
    postcode = myline[3]
    address = ' '.join(myline[7:10])
    try:
        driver = webdriver.Firefox(options=browser_options, firefox_binary="/kaggle/working/firefox/firefox/firefox")
        driver.get(url)
        txtPC = driver.find_element_by_name("txtPostCode")
        driver.execute_script('arguments[0].value = arguments[1]', txtPC, postcode)
        driver.find_element_by_id('frmInitSForm').submit()
        time.sleep(1.5)
        scl_complex = driver.find_element_by_class_name('scl_complex')
    except:
        print('[ERROR] Something went wrong with this search, a connection error was returned')
        if 'driver' in locals():
            driver.quit()
        return 'err'
    oldtext = scl_complex.text if 'scl_complex' in locals() else ''
    if oldtext == '':
        answer='err'
        print('Line, Answer: %s, %s'%(myline,answer))
        print()
        return answer
    while True:
        a=''
        try:
            driver.execute_script("Next();")
            time.sleep(2)
        except selenium.common.exceptions.JavascriptException:
            break
        try:
            scl_complex = driver.find_element_by_class_name('scl_complex')
            oldtext = oldtext +'\n'+ scl_complex.text
        except:
            print('[ERROR] Something went wrong with this search, a connection error was returned')
            if 'driver' in locals():
                driver.quit()
            return 'err'
    driver.quit()
    oldtext = oldtext.replace('Address Council Tax band Improvement indicator Local authority reference number\n','')
    while '  ' in oldtext:
        oldtext = oldtext.replace('  ',' ')
    lines = oldtext.split('\n')
    res=[]
    if 'Local authority name' in oldtext:
        answer='notFound'
        print('Line, Answer: %s, %s'%(myline,answer))        
        print()   
        return answer
    for line in lines:
        ls = line.split(' ')
        if len(ls)<2: continue #protection against empty lines in server answer
        if ls[-2] == 'Yes': ##if present, ignore 'Improvement indicator' field
            ls.pop(-2)
        t = (' '.join(ls[:-2]), ls[-2], ls[-1])
        res.append(t)
	
    answer='notFound'
    for t in res:
        #compare to PAON
        if t[0].split(',')[0] == myline[7]:
            answer=t[1]
            break
    if answer=='notFound':
        for t in res:
            #if still not found, compare to SAON
            if t[0].split(',')[0] == myline[8]:
                answer=t[1]
                break
    if answer=='notFound':
        for t in res:
            #if still again not found, allow partial match to SAON
            if t[0].split(',')[0] in myline[8].split():
                answer=t[1]
                break        
    print('Line, Answer: %s, %s'%(myline,answer))        
    print()
    return answer


def wrapSearchLine(myline, url="http://cti.voa.gov.uk/cti/inits.asp", browser_options=browser_options, sleep=10, maxAttempts=2):
    attempt=1
    ret=''
    while attempt<=maxAttempts:
        if attempt>1:
            print( '[INFO] Search attempt n.%s'%(attempt))
        ret = searchLine(myline, url, browser_options)
        if ret == 'err':
            attempt=attempt+1
            print('[ERROR] Connection problem. Waiting %ss before trying again.'%(sleep))
            time.sleep(sleep)
        else:
            break
    return ret
    
    
