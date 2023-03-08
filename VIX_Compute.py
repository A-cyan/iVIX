import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy.interpolate import interp1d
import warnings

warnings.filterwarnings("ignore")

class VixDataset:
    def __init__(self):
        self.zhr = None



def select_OptionTime(data_OptionInf, now_T):
    """
    筛选近月合约和次月合约到期日
    :param data_OptionInf:期权基本信息
    :param now_T: 当前时刻
    :return: 近月合约到期日和次月合约到期日
    """
    now_T = pd.to_datetime(now_T)
    all_T = sorted(list(set(list(pd.to_datetime(data_OptionInf['到期日'])))))
    T1 = [date for date in all_T if (date.year == now_T.year) and (date.month == now_T.month)]
    if len(T1) == 0:
        return [-1, -1]
    days = (T1[0] - now_T).days
    if ((days > 7) & (now_T.month < 12)):
        T2 = [date for date in all_T if (date.year == now_T.year) and (date.month == now_T.month + 1)]
    elif ((days > 7) & (now_T.month == 12)):
        T2 = [date for date in all_T if (date.year == now_T.year + 1) and (date.month == 1)]
    elif ((days <= 7) & (now_T.month < 11)):
        T1 = [date for date in all_T if (date.year == now_T.year) and (date.month == now_T.month + 1)]
        T2 = [date for date in all_T if (date.year == now_T.year) and (date.month == now_T.month + 2)]
    elif ((days <= 7) & (now_T.month == 11)):
        T1 = [date for date in all_T if (date.year == now_T.year) and (date.month == now_T.month + 1)]
        T2 = [date for date in all_T if (date.year == now_T.year + 1) and (date.month == 1)]
    elif ((days <= 7) & (now_T.month == 12)):
        T1 = [date for date in all_T if (date.year == now_T.year + 1) and (date.month == 1)]
        T2 = [date for date in all_T if (date.year == now_T.year + 1) and (date.month == 2)]
    a = 1
    return [T1[0], T2[0]]


def Rate_Compute(now_T, data_Rate, T):
    """
    使用三次样条插值计算从现在起到到期时的无风险利率
    :param now_T: 当下的日期
    :param data_Rate: 用于插值的SHIBOR数据s
    :param T: 期权合约到期日
    :return: 无风险利率R
    """
    data_Rate.index = pd.to_datetime(data_Rate.index)
    T_term = (T - now_T).days
    period = np.asarray([1.0, 7.0, 14.0, 30.0, 90.0, 180.0, 270.0, 365.0])
    value = np.asarray(data_Rate.loc[now_T, :])
    f = interp1d(period, value, kind='cubic')
    R = f(T_term)
    return float(R)/100
    a = 1


def select_Option(Now_t, data_option, T):
    """
    筛选出当前日期，特定日期到期的期权合约信息，并做格式重构
    :param Now_t: 当前日期
    :param data_option: 期权合约信息
    :param T: 到期日期
    :return: 筛选后数据，包含行权价、看涨价格、看跌价格、价格差的绝对值
    """
    data_option['到期日'] = pd.to_datetime(data_option['到期日'])
    data_option['日期'] = pd.to_datetime(data_option['日期'])
    data_call = data_option[(data_option['日期'] == Now_t) & (data_option['到期日'] == T) & (data_option['认购/认沽']=='认购')]
    data_put = data_option[(data_option['日期'] == Now_t) & (data_option['到期日'] == T) & (data_option['认购/认沽']=='认沽')]
    data = pd.merge(data_call, data_put, on='行权价')
    data_select = pd.DataFrame({'行权价': data['行权价'], 'Call':data['收盘价_x'], 'Put':data['收盘价_y'],
                                'Gap':np.abs(data['收盘价_x']-data['收盘价_y'])})
    data_select.sort_values(by = '行权价', inplace=True)
    data_select = data_select.reset_index(drop=True)
    return data_select
    a = 1


def F_Compute(data_option, term, R):
    """
    计算远期指数水平F
    :param data_option:筛选后的期权合约信息
    :param term:距离期权到期剩余时间
    :param R:无风险利率
    :return:远期指数水平
    """
    num = data_option['Gap'].idxmin()
    F = data_option.iloc[num, 0] + np.e ** (term*R) * (data_option.iloc[num, 1] - data_option.iloc[num, 2])
    a = 1
    return F


def K_Compute(data_option, F):
    """
    计算K0
    :param dataoption: 筛选后的期权合约信息
    :param F: 远期指数水平
    :return: K0
    """
    K = data_option.iloc[0, 0]
    for i in range(data_option.shape[0]):
        if (data_option.iloc[i, 0]<F):
            K = data_option.iloc[i, 0]
        else:
            break
    return K
    a = 1


def sigma_Compute(Option, K, R, term, F):
    """
    计算期权波动性sigma
    :param Option: 筛选后的期权信息
    :param K: K0
    :param R: 无风险利率
    :param term: 到期期限
    :param F: 远期指数水平
    :return: 期权波动性sigma
    """
    Option_Call = Option[Option['行权价']>K]
    Option_Put = Option[Option['行权价']<K]
    Option_Mix = Option[Option['行权价']==K]
    Option_Call = pd.DataFrame({'行权价': Option_Call['行权价'], '价格': Option_Call['Call']})
    Option_Put = pd.DataFrame({'行权价': Option_Put['行权价'], '价格': Option_Put['Put']})
    Option_Mix = pd.DataFrame({'行权价': Option_Mix['行权价'], '价格': (Option_Mix['Call']+Option_Mix['Put'])/2})
    Option_price = pd.concat([Option_Put, Option_Mix, Option_Call], axis=0)
    Option_price['deltaK'] = 0
    for i in range(Option_price.shape[0]):
        if (i == 0):
            Option_price.iloc[i, 2] = Option_price.iloc[i + 1, 0] - Option_price.iloc[i, 0]
        elif (i == Option_price.shape[0]-1):
            Option_price.iloc[i, 2] = Option_price.iloc[i, 0] - Option_price.iloc[i - 1, 0]
        else:
            Option_price.iloc[i, 2] = (Option_price.iloc[i + 1, 0] - Option_price.iloc[i - 1, 0])/2
    sigma = 0
    for i in range(Option_price.shape[0]):
        sigma = sigma + (Option_price.iloc[i, 2])/(Option_price.iloc[i, 0] ** 2) * np.e ** (R*term) * Option_price.iloc[i, 1]
    sigma = sigma * (2/term) - (1/term)*(F/K-1)**2
    a = 1
    return sigma


def VIX(sigma1, sigma2, term1, term2):
    """
    计算VIX指数
    :param sigma1:近月期权波动性
    :param sigma2:次月期权波动性
    :param term1: 近月期权剩余期限
    :param term2: 远月期权剩余期限
    :return: VIX
    """
    vix = 100 * np.sqrt((term1 * sigma1 * (term2 - 30/365)/(term2 - term1) + term2 * sigma2 * (30/365 - term1)/(term2 - term1)) * (365/30))
    return vix


if __name__ == '__main__':
    data_Option = pd.read_csv('clean_data\\data_Option.csv', index_col=0)
    data_OptionInf = pd.read_csv('clean_data\\data_OptionInf.csv', index_col=0)
    data_Rate = pd.read_csv('clean_data\\data_Rate.csv', index_col=0)
    data_ETF = pd.read_csv('clean_data\\data_ETF.csv', index_col=0)


    # 这里具体的日期选用仍然需要再考虑一下
    AllDate = sorted(list(set(list(data_Rate.index))))
    print('日期循环：\n')
    data_vix = pd.DataFrame(columns=['Date', 'vix'])
    for i in tqdm(range(len(AllDate))):
        # i = 2181
        Now_T = AllDate[i]
        # 筛选近月和次月期权的到期日
        [T1, T2] = select_OptionTime(data_OptionInf, Now_T)
        if T1 == -1:
            # 当前日期无法找到对应近月与次月合约
            continue
        Now_T = pd.to_datetime(Now_T)
        T1_term = (T1 - Now_T).days/365
        T2_term = (T2 - Now_T).days/365
        # 三次样条插值计算至到期日的无风险收益
        R1 = Rate_Compute(Now_T, data_Rate, T1)
        R2 = Rate_Compute(Now_T, data_Rate, T2)
        # 筛选符合条件的期权合约，获取信息
        Option1 = select_Option(Now_T, data_Option, T1)
        Option2 = select_Option(Now_T, data_Option, T2)
        if ((Option1.shape[0] == 0) | (Option2.shape[0] == 0)):
            continue
        # 确定远期指数水平F
        F1 = F_Compute(Option1, T1_term, R1)
        F2 = F_Compute(Option2, T2_term, R2)
        # 确定K0
        K01 = K_Compute(Option1, F1)
        K02 = K_Compute(Option2, F2)
        # 计算sigma
        sigma1 = sigma_Compute(Option1, K01, R1, T1_term, F1)
        sigma2 = sigma_Compute(Option2, K02, R2, T2_term, F2)
        # 计算VIX
        vix = VIX(sigma1, sigma2, T1_term, T2_term)
        data_vix = data_vix.append({'Date': Now_T, 'vix': vix}, ignore_index=True)
    data_vix.to_csv('result\\vix.csv')
    a = 1