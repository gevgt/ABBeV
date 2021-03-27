import pandas as pd
import numpy as np
import time
import datetime
import pandas_datareader as pdr
import wikipedia as wp



class Benchmark:

    def __init__(self, sector, jahre=1.2):
        self.sector = sector
        self.sector_const = None
        self.fehler = []
        self.data = None
        self.jahre = jahre
    
    
    
    
    
    def zusammenstellung_unternehmen(self):
        """
        

        Returns
        -------
        ticker : list
            Liste mit den Tickern der Unternehmen, die im S&P 500 sind und dem
            angegebenen Sektor zugehörig.

        """
        # Lade Liste mit den S&P 500 Constituents von Wikipedia
        html = wp.page("List_of_S%26P_500_companies").html().encode("UTF-8")
        df = pd.read_html(html)[0]
        
        # Ersetze "." mit "-"
        x = pd.concat([df["Security"], df["Symbol"], df["GICS Sector"]], axis=1).values
        x = np.array(x, dtype=str)
        x[:,1] = np.char.replace(x[:,1], ".", "-")
        x = pd.DataFrame(x, columns=["Security", "Symbol", "Sector"])
        
        # Filter die Unternehmen nach dem gewünschten Sektor
        self.sector_const = x.loc[x['Sector'] == self.sector].reset_index(drop=True)
        ticker = list(self.sector_const["Symbol"])
        
        return ticker

    



    def download_data(self, ticker):
        """
        

        Parameters
        ----------
        ticker : list
            Liste mit den Tickern der Unternehmen, die im S&P 500 sind und dem
            angegebenen Sektor zugehörig.

        Returns
        -------
        data : DataFrame
            DF mit den "Adj Close" Kursen aller Unternehmen aus der Ticker Liste.
            Spalten stehen für die Zeitreihen der einzelnen Unternehmen.

        """
        data = []
        start = (datetime.datetime.now() - datetime.timedelta(days=self.jahre*365)).strftime('%Y-%m-%d')
        end = datetime.datetime.today().strftime('%Y-%m-%d')
        
        for i, t in enumerate(ticker):
            
            # Nach 50 Downloads 60 Sekunden Pause, damit nicht zu viele Daten
            # pro Minute heruntergeladen werden und einen Fehler verursachen.
            if i%50 == 0 and i!=0:
                print("\n60 Sekunden Pause\n")
                time.sleep(60)
            
            # Probiere, ob die Zeitreihe heruntergeladen werden kann. Wenn nicht,
            # 60 Sekunden Pause und nocheinmal probieren. Wenn es immer noch
            # nicht klappt, füge den Ticker zur Liste "fehler" hinzu.
            try:
                d = pdr.DataReader(t, "yahoo", start, end)["Adj Close"]
            except:
                print("Fehler: 60 Sekunden Pause")
                time.sleep(60)
                try:
                    d = pdr.DataReader(t, "yahoo", start, end)["Adj Close"]
                except:
                    self.fehler.append(t)
                    
            # Ändere die Spaltenüberschrift von "Adj Close" in den Ticker des
            # Unternehmens.
            d = pd.DataFrame(d.values, columns=[t], index=d.index)
            
            # Füge das DataFrame zur Liste "Data" hinzu.
            data.append(d)
            
            # Printe, wie viel Prozent der Downloads schon geschafft wurden.
            print(t, str(int(i/len(ticker)*100)) + "%")
        
        # Konkatiniere die DataFrames aus der Liste.
        data = pd.concat(data, axis=1)
        self.data = data
        
        # Printe, wie viele Fehler aufgetreten sind.
        print("\n\nAnzahl der Fehler: " + str(len(self.fehler)))
        
        return data





    def geometrisch_verknuepfen(self, returns):
        """
        

        Parameters
        ----------
        returns : Array of float64
            Array mit Returns.

        Returns
        -------
        output : Array of float64
            Array mit den geometrisch verknüpften Returns.

        """
        output = [1] 
        for i in range(returns.shape[0]):
            output.append(output[-1] * (1 + returns[i]))
        output = (output/output[1])[1:]
        
        return output
    
    
    
   
    
    def main(self):
        """
        

        Returns
        -------
        time_series : DataFrame
            Zeitreihe der Benchmark. Spaltennamen: Financials.

        """
        ticker = self.zusammenstellung_unternehmen()
        data = self.download_data(ticker)
        returns = (data / data.shift(1) - 1).dropna()
        avg_return = np.nanmean(returns, axis=1)
        time_series = self.geometrisch_verknuepfen(avg_return)
        time_series = pd.DataFrame(time_series, columns=[str(self.sector)], index=returns.index)
        
        return time_series
        
        
   
    
   
    
   
    
   
    
if __name__ == '__main__':
    sector = "Real Estate"
    x = Benchmark(sector)
    time_series = x.main()