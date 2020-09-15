import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import xlwings as xw
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

df = pd.concat(data, axis=1)

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



#Zeitmesser
t = TicToc()
t.tic()



#############################
### Black-Litterman-Model ###
#############################

#Views: in unserem Fall die historischen Returns

#Wir gewichten alle Assets gleich
wmarket = np.ones((len(meanReturns),1))/len(meanReturns)

#Durchschnittliche Portfolio Performance
pfmean = np.matmul(wmarket.T, meanReturns.values)

#Portfolio Varianz
pfvar = np.matmul(wmarket.T, np.matmul(kovarianzMatrix.values, wmarket))

#Risk aversion coefficient: damit werden dei implied equilibrium returns skaliert
#Wie viel Risiko ist der Investor bereit einzugehen für eine Einheit mehr return?
lamb = pfmean/pfvar



#Implied equilibrium returns: Die Returns, die die Assets haben müssen, damit das
#Portfolio, dass nach wmarket gewichtet ist, jenes ist, welches auf der Efficient
#Frontier liegt und das höchste Sharpe Ratio hat. Normalerweise ist wmarket der
#Prozentuale Anteil der Marktkapitalisierung der Assets im PF.
pi = lamb * np.matmul(kovarianzMatrix.values,wmarket)



#Q: Der Vektor mit unseren Views
#Es gibt 3 verschiedene Arten von Views: relative, absolute und relativ mit mehreren
#Assets. In diesem Fall
N = len(meanReturns)
diff = meanReturns.values - pi



#Mein Beitrag zur Literatur :D
#Ich verwende hier absolute Views. Dazu nehme ich zunächst einmal den Mittelwert
#der historischen Returns. Jedoch sind die views meistens zu verschieden von pi,
#weshalb ich trotz allem komische PFs bekomme. Daher nehme ich die Unterschiedlich-
#keit heraus, indem meine angepassten Views pi plus einen Bruchteil der Differenz
#zwischen den historischen Returns und pi.
Q = pi + 0.5 * diff



#P: Matrix in dem die Assets, die in einem View vertreten vermerkt werden.
#Da ich ausschließlich absolute Views verwende reicht eine Identity Matrix.
K = N
P = np.identity(K)



#Omega: K x K Matrix mit der Unsicherheit der Views
Omega = np.array([])	

#Skaliert die Varianz der Fehlerterme
teta = 1	

for i in range(0, K):							
	for j in range(0, K):
		if i == j:
			Omega = np.append(Omega, np.matmul(P[i,:], 
                        np.matmul(kovarianzMatrix.values, 
                        np.transpose(P[i,:]))) * teta)
		else:
			Omega = np.append(Omega, 0)
Omega = Omega.reshape(K,K)



#Black-Litterman Formula
part1 = np.linalg.inv( np.linalg.inv(teta*kovarianzMatrix.values) + 
            np.matmul(np.transpose(P), np.matmul(np.linalg.inv(Omega),P)) )

part2 = (np.matmul(np.linalg.inv(teta*kovarianzMatrix.values), pi) + 
            np.matmul(np.transpose(P), np.matmul(np.linalg.inv(Omega), Q)))
newexp = np.matmul(part1, part2)



#New optimal Weights
neww = np.around(np.matmul(np.linalg.inv(lamb*kovarianzMatrix.values), newexp),4)
optimaleGewichte = pd.DataFrame(np.round(neww/np.sum(neww),2), index=meanReturns.index, 
                                columns=["Opt. PF Gewichte"])


#Returns, Standardabweichung und Sharpe Ratio mit den neuen returns
returnsOpt = np.matmul(optimaleGewichte.values.T, meanReturns.values) * 250
stdOpt = (np.matmul(optimaleGewichte.values.T, np.matmul(kovarianzMatrix.values, 
            optimaleGewichte.values)) ** 0.5) * (250**0.5)
sharpeOpt = returnsOpt/stdOpt

kf = np.round(np.concatenate([returnsOpt, stdOpt, sharpeOpt], axis=0), 2)
keyFigures = pd.DataFrame(kf, index=["Returns", "Std", "Sharpe Ratio"], 
                          columns=["Key Figures"])



t.toc()



print(optimaleGewichte)
print()
print(keyFigures)