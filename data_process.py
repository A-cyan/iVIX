import pandas as pd
import numpy as np
from datetime import datetime

data_ETF = pd.read_csv('ETF50_Time_Series_Data.csv', encoding='utf-8')
data_SHIBOR = pd.read_csv('MBK_SHIBORM.csv', encoding='utf-8',)
data_Option = pd.read_csv('Option_Time_Series_Data_Table.csv', encoding='utf-8')
data_OptionInf = pd.read_csv('Option_Basic_Information.csv', encoding='utf-8')

data_ETF = data_ETF[['日期', '收盘价']]
data_Option = data_Option[['日期', '期权代码', '行权价', '收盘价']]
data_OptionInf = data_OptionInf[['期权代码', '认购/认沽', '到期日']]

# 将期权交易数据与基本信息合并
data_Option = pd.merge(data_Option, data_OptionInf, how = 'outer')

# 改变SHIBOR数据结构，每个交易日的SHIBOR作为一行
data_Rate = pd.DataFrame(columns=['Date','1天','7天','14天','30天','90天','6个月','9个月','1年'])
date = sorted(list(set(list(data_SHIBOR['SgnDate']))))
data_Rate['Date'] = date
data_Rate.set_index('Date', inplace=True)
del(date)
for i in range(data_SHIBOR.shape[0]):
    date = data_SHIBOR.iloc[i, 0]
    term = data_SHIBOR.iloc[i, 1]
    Shibor = data_SHIBOR.iloc[i, 2]
    data_Rate.loc[date, term] = Shibor
a = 1

# 保存数据
data_ETF.to_csv('clean_data\\data_ETF.csv')
data_Option.to_csv('clean_data\\data_Option.csv')
data_OptionInf.to_csv('clean_data\\data_OptionInf.csv')
data_Rate.to_csv('clean_data\\data_Rate.csv')
# data_ETF['日期'] = pd.to_datetime(data_ETF['日期'])
# data_ETF['Year'] = data_ETF['日期'].map(lambda x:x.year)

