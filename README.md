# 指数计算思路
## 选择近月合约与次月合约
首先要选择近月期权的交易日与次月期权的交易日。针对上证50ETF期权交易日的实际情况，使用如下准则选择交易日：
给定当前日期，选择距现在最近的到期合约为近月合约，次近的到期合约为次月合约。需要注意的是，如果距现在最近的期权合约的剩余到期天数小于7天，则选择次近的到期合约作为近月合约，次次近的到期合约作为次月合约。
## 计算合约到期剩余期限 $T$
使用剩余到期天数/365计算得到
## 计算无风险利率 $R$
对SHIBOR数据使用三次样条插值，获取至到期日无风险利率。
## 计算远期价格水平 $F$
对于近月到期日和次月到期日，分别选择看涨、看跌价格差距的绝对值最小的期权合约的行权价，并使用如下公式计算 $F$。
$$F=StikePrice+e^{RT}\*(Call-Put)$$
## 确定 $K_0$
选择小于 $F$ 且最接近 $F$ 的行权价格作为 $K_0$ 。
## 计算期权价格
对于 $K_i$ 小于 $K_0$ 的期权，选择看跌期权价格；对于 $K_i$ 大于 $K_0$ 的期权，选择看涨期权价格；对于 $K_i$ 等于 $K_0$ 的期权，选择看涨期权价格与看跌期权价格的均值。
## 计算近月波动率与远月波动率
根据上述计算结果，利用如下公式计算波动率。
$$σ^2=\frac{2}{T}∑_i\frac{ΔK_i}{K_i^2} e^{RT} P(K_i )-\frac{1}{T} [\frac{F}{K_0} -1]^2$$
## 计算 $VIX$
使用近月波动率月波动率，利用如下公式计算 $VIX$ 。
$$VIX=100*\sqrt{({T_1 σ_1^2 [(NT_2-30)/(NT_2-NT_1 )]+T_2 σ_2^2 [(30-NT_1)/(NT_2-NT_1 )]}\*365/30)}$$
# 各文件功能介绍
## 文件夹
clean_data：保存清洗后的数据，仅包含计算VIX将使用的各项数据。  
iVIX: 保存上交所编制的iVIX指数数据，作为编制结果对比使用。  
result：保存计算得到的VIX指标表格，并生成曲线图。  
## python文件
- data_process.py：进行数据清洗与预处理，仅保存会使用到的数据，将清洗结果保存在clean_data文件夹下。  
- VIX_Compute.py：计算VIX指数，将计算结果保存为result\\vix.csv。  
  - def select_OptionTime(data_OptionInf, now_T):  
    筛选近月合约和次月合约到期日  
    :param data_OptionInf:期权基本信息  
    :param now_T: 当前时刻  
    :return: 近月合约到期日和次月合约到期日  
  - def Rate_Compute(now_T, data_Rate, T):  
    使用三次样条插值计算从现在起到到期时的无风险利率  
    :param now_T: 当下的日期  
    :param data_Rate: 用于插值的SHIBOR数据s  
    :param T: 期权合约到期日  
    :return: 无风险利率R  
  - def select_Option(Now_t, data_option, T):  
    筛选出当前日期，特定日期到期的期权合约信息，并做格式重构  
    :param Now_t: 当前日期  
    :param data_option: 期权合约信息  
    :param T: 到期日期  
    :return: 筛选后数据，包含行权价、看涨价格、看跌价格、价格差的绝对值  
  - def F_Compute(data_option, term, R):  
    计算远期指数水平F  
    :param data_option:筛选后的期权合约信息  
    :param term:距离期权到期剩余时间  
    :param R:无风险利率  
    :return:远期指数水平  
  - def K_Compute(data_option, F):  
    计算K0  
    :param dataoption: 筛选后的期权合约信息  
    :param F: 远期指数水平  
    :return: K0  
  - def sigma_Compute(Option, K, R, term, F):  
    计算期权波动性sigma  
    :param Option: 筛选后的期权信息  
    :param K: K0  
    :param R: 无风险利率  
    :param term: 到期期限  
    :param F: 远期指数水平  
    :return: 期权波动性sigma  
  - def VIX(sigma1, sigma2, term1, term2):  
    计算VIX指数  
    :param sigma1:近月期权波动性  
    :param sigma2:次月期权波动性  
    :param term1: 近月期权剩余期限  
    :param term2: 远月期权剩余期限  
    :return: VIX  
- test.py：比较上交所编制的iVIX和本报告计算的VIX指数，生成曲线图保存在result文件夹下。  
# 计算结果  
具体计算结果保存为result\\vix.csv。  

