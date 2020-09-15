import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pytictoc import TicToc
import pandas_datareader as pdr



#Ticker
tickers = ["AMZN", "BRK-A", "AAPL", "GOOG", "IBM"]
ticker_name=["Amazon", "Berkshire Hathaway", "Apple", "Google", "IBM"]



#Lädt Daten
data = []

for x,y in zip(tickers, ticker_name):
    d = pdr.DataReader(x, "yahoo", "2010-01-01", "2020-01-01")["Adj Close"]
    d = d.rename(y, axis="columns")
    data.append(d)

df = pd.concat(data, axis=1).dropna()



#Zeitmesser
t = TicToc()
t.tic()



#Returns erstellen (auf tagesbasis)
returns = pd.DataFrame(df.values[1:]/df.values[0:-1]-1, columns=df.columns, 
                       index=df.index[1:])



#Durchschnittliche Returns und Varianz-Kovarianz-Matrix
meanReturns = pd.DataFrame(np.nanmean(returns.values, axis=0), 
                    index=df.columns, columns=["Mean Returns"])

kovarianzMatrix = pd.DataFrame( 
    np.matmul((returns.values-meanReturns.values.reshape(1,len(df.columns))).T,
    returns.values-meanReturns.values.reshape(1,len(df.columns))) / len(returns),
    columns=df.columns, index=df.columns)



#Produziert n zufällige Portfoliogewichte wobei summe(w)=1.
n = 100000
weights = np.random.randint(100, size=(n, len(df.columns)))
weights = np.round(weights/weights.sum(axis=1)[:,None],2)



#Gewichte die doppelt auftreten, werden gelöscht
weights = pd.DataFrame(weights).drop_duplicates()



#Portfolio- Returns, Standardabweichung und Sharpe Ratio
returnPF = np.matmul(meanReturns.values.T, weights.values.T).T * 250

varPF = []
for i in range(weights.shape[0]):
    var = np.matmul(np.matmul(weights.values[i], kovarianzMatrix.values), weights.values[i].T)
    varPF.append(var)
varPF = (np.array(varPF).reshape(len(varPF),1)**0.5) * (250**0.5)

srPF = returnPF / varPF



#Erstellung des "results" DataFrames
columns = np.array(["Sharpe Ratio", "PF Returns", "PF Std"])
columns = np.append(columns, df.columns)
results = pd.DataFrame(np.concatenate([srPF, returnPF, varPF, weights], axis=1), columns=columns)
r = results.values



#Index des "Maximum Sharpe Ratio"-Portfolios und des "Minimum Variance"-Portfolios
maxSR = np.argmax(r[:,0])
minV = np.argmin(r[:,2])



#Output Tabelle mit den Daten zum MSR-PF und MV-PF
output = pd.DataFrame(np.concatenate([np.round(r[maxSR],2).reshape(1,r.shape[1]), 
        np.round(r[minV],2).reshape(1,r.shape[1])], axis=0).T, index=columns, 
        columns=["Max. Sharpe Ratio", "Min. Volatility"])



#Zeitmesser Ende
t.toc()



### Grafik ###
f = plt.figure()


#Plottet die n verschiedenen Portfolios mit der Std auf der x- und den Returns
#auf der y-Achse
plt.scatter(r[:,2], r[:,1], c=r[:,0],cmap='YlGnBu', marker='o', s=10, alpha=0.3)



#Plottet das MSR-PF und das MV-PF
plt.scatter(r[maxSR,2], r[maxSR,1], marker='*',color='r',s=500)
plt.annotate('Maximum\nSharpe ratio', (r[maxSR,2], r[maxSR,1]),
                     textcoords="offset points", xytext=(-6,12), ha='center', 
                     fontsize=7, color="black", zorder=2)

plt.scatter(r[minV,2], r[minV,1], marker='^',color='g',s=250)
plt.annotate('Minimum\nvolatility', (r[minV,2], r[minV,1]),
                     textcoords="offset points", xytext=(-6,12), ha='center', 
                     fontsize=7, color="black", zorder=2)



#Feintunig der Grafik
plt.title('Simulated Portfolio Optimization\nbased on Efficient Frontier (n='+ 
        str(n)+")", fontweight="bold")
plt.xlabel('annualised volatility')
plt.ylabel('annualised returns')
plt.show()





#Printet die Output Tabelle die oben erstellt wurde
print(output)
