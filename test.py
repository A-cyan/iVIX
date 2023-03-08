import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

mydata = pd.read_csv('result\\vix.csv', index_col=0)
mydata['Date'] = pd.to_datetime(mydata['Date'])
stdata = pd.read_csv('iVIX\\ivixx.csv')
stdata['date'] = pd.to_datetime(stdata['date'])
plt.figure(figsize=(10,3))
plt.plot(mydata['Date'], mydata['vix'])
plt.plot(stdata['date'], stdata['ivix'])
plt.show()

a = 1