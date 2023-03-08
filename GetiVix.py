import json
import urllib3
import pandas as pd
import time

def get_data(url_temp,retries=3):
    try:
        f=urllib3.urlopen(url_temp,timeout = 1)
        data = f.read()
    except Exception as e:
        print (str(e),url_temp)
        if retries>0:
            time.sleep(0.5)
            return get_data(url_temp,retries-1)
        else:
            print ('GET Failed',url_temp)
            return -1
    return data

url = 'http://yunhq.sse.com.cn:32041/v1/csip/dayk/000188?callback=test&begin=1&end=-1&select=date%2Copen%2Chigh%2Clow%2Cclose&_=1492899476267'

return_str = get_data(url)
return_str = return_str.replace('test(','')[:-1]
json_obj =  json.loads( return_str )
print (pd.DataFrame(json_obj['kline'],columns=['date','open','high','low','close']))