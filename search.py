import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

chrome_options = Options()
chrome_options.headless = True
#chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


def searchLine(myline, url="http://cti.voa.gov.uk/cti/inits.asp", chrome_options=chrome_options):
    myline = myline.replace('"','').split(',')
    print(myline)
    postcode = myline[3]#'SE1 0AJ'
    address = ' '.join(myline[7:10])
    print(address)
    try:
        driver = webdriver.Chrome("chromedriver", options=chrome_options)#, options=options)
        driver.get(url)
        txtPC = driver.find_element_by_name("txtPostCode")
        driver.execute_script('arguments[0].value = arguments[1]', txtPC, postcode)
        driver.find_element_by_id('frmInitSForm').submit()
        scl_complex = driver.find_element_by_class_name('scl_complex')
    except:# selenium.common.exceptions.TimeoutException:
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
        try:
            a = driver.execute_script("Next();")
            scl_complex = driver.find_element_by_class_name('scl_complex')
            oldtext = oldtext +'\n'+ scl_complex.text
        except selenium.common.exceptions.JavascriptException:
            break
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
        if ls[-2] == 'Yes': ##if present, ignore 'Improvement indicator' field
            ls.pop(-2)
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
    print('Line, Answer: %s, %s'%(myline,answer))        
    print()
    return answer


def wrapSearchLine(myline, url="http://cti.voa.gov.uk/cti/inits.asp", chrome_options=chrome_options, sleep=10, maxAttempts=2):
    attempt=1
    ret=''
    while attempt<=maxAttempts:
        if attempt>1:
            print( '[INFO] Search attempt n.%s'%(attempt))
        ret = searchLine(myline, url, chrome_options)
        if ret == 'err':
            attempt=attempt+1
            print('[ERROR] Connection problem. Waiting %ss before trying again.'%(sleep))
            time.sleep(30)
        else:
            break
    return ret
    
    
