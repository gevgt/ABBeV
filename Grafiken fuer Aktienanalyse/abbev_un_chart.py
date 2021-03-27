import pandas as pd
from matplotlib import pyplot as plt
import pandas_datareader as pdr
import datetime
from benchmark import Benchmark


###############################################################################
###############################################################################

ticker = "JPM"
sektor = 0
pos1 = 2
pos2 = 1

###############################################################################
###############################################################################





sektoren = {
        0 : "Financials",
        1 : "Consumer Discretionary",
        2 : "Utilities",
        3 : "Communication Services",
        4 : "Health Care",
        5 : "Energy",
        6 : "Materials",
        7 : "Consumer Staples",
        8 : "Information Technology",
        9 : "Industrials",
        10 : "Real Estate"
    }










class Chart:
    
    def __init__(self, ticker, benchmark, pos1, pos2):
        """
        

        Parameters
        ----------
        ticker : Str
            Yahoo! Finance Ticker des Unternehmens. Z.B. "AAPL".
        benchmark : DataFrame
            Zeitreihe der Benchmark. Spaltennamen: Financials.
        pos1 : int
            Position des "Return"-Tags der oberen Grafik.
        pos2 : int
            Position des "Return"-Tags der unteren Grafik.

        Returns
        -------
        None.

        """
        self.ticker = ticker
        self.benchmark = benchmark
        self.daten = self.lade_daten()
        self.pos1 = pos1
        self.pos2 = pos2
        self.b = None
        
        
        
        
        
    def lade_daten(self):
        """
        

        Returns
        -------
        daten : DataFrame
            Spaltennamen: High, Low, Open, Close, Volume, Adj Close.

        """
        # Lädt die benötigten Daten von Yahoo! Finance herunter im Zeitraum
        # vor 6 Jahren bis heute.
        start = (datetime.datetime.now() - datetime.timedelta(days=6*365)).strftime('%Y-%m-%d')
        end = datetime.datetime.today().strftime('%Y-%m-%d')
        daten = pdr.DataReader(self.ticker, "yahoo", start, end)
        
        return daten
    
    
    
    
    
    def daten_fuer_chart(self, start_jahr):
        """
        

        Parameters
        ----------
        start_jahr : int
            Jahr, ab dem der Cahrt anfangen soll. Z.B. 2020.

        Returns
        -------
        adj_close : Series
            Series mit der "Adj Close" Spalte des Data DataFrame.
        volume : Series
            Series mit der "Volume" Spalte des Data DataFrame.
        relative_staerke : Series
            Relative Stärke Zeitreihe.

        """
        # Bestimmt den heutigen Monat und Kalendertag
        monat = datetime.datetime.today().month
        tag = datetime.datetime.today().day
        
        # Bestimmt den Index (0 bis n), ab dem die Zeitreihe benötigt wird.
        start = self.daten.index.searchsorted(datetime.datetime(start_jahr, monat, tag))
        
        # Kürze die Zeitreihe "daten".
        daten = self.daten.iloc[start:]
        
        # Bestimmt den Index (0 bis n), ab dem die Zeitreihe benötigt wird.
        start = self.benchmark.index.searchsorted(datetime.datetime(start_jahr, monat, tag))
        
        # Kürze die Zeitreihe "benchmark".
        benchmark = self.benchmark.iloc[start:][str(self.benchmark.columns[0])]
        
        # Wandle "adj_close" und "volume" in Series um.
        adj_close = daten["Adj Close"]
        volume = daten["Volume"]
        
        # Berechne die relative Stärke Zeitreihe mit der entsprechenden Funktion.
        relative_staerke = self.relative_staerke_sektor(adj_close, benchmark)
        
        return adj_close, volume, relative_staerke
    
    
    
    
    
    def relative_staerke_sektor(self, adj_close, benchmark):
        """
        

        Parameters
        ----------
        adj_close : Series
            Series mit der "Adj Close" Spalte des Data DataFrame.
        benchmark : Series
            Zeitreihe der Benchmark. Gleiche länge wie adj_close.

        Returns
        -------
        relative_staerke : Series
            Relative Stärke Zeitreihe.

        """
        # Diese Berechnet die Preisentwicklung des Unternehmens relativ zu einer
        # Benchmark. Die resultierende Zeitreihe wird auf 1 normiert.
        relative_staerke = adj_close / benchmark
        relative_staerke /= relative_staerke[0]
        
        return relative_staerke
    
    
    
    
    
    def return_text(self, preise, loc):
        """
        

        Parameters
        ----------
        preise : Series
            Zeitreihe mit den Kursdaten.
        loc : int
            Ort, wo das Tag mit dem Return hin soll.

        Returns
        -------
        text : str
            String mit dem Vorzeichen des Returns und dem % Zeichen.
        color : str
            Farbe des "Return" Schriftzugs. Grün für positiv, rot für negativ.
        y : float
            y-Koordinate des Schriftzugs.

        """
        # Berechne Return und wandle ihn in Prozent um.
        r = round((preise[-1]/preise[0] - 1)*100,2)
        
        # Wenn Return positiv ist, erstelle einen String und füge ein "+"  und 
        # ein "%" hinzu.
        if r >= 0:
            text = "+" + str(r) + "%"
            color = "green"
        # Wenn Return negativ ist, füge lediglich ein "%" hinzu
        else:
            text = str(r) + "%"
            color = "red"
        
        # Bestimme die y-Koordinate des "Return" Tags, abhängig von der Variable
        # loc.
        if loc == 0:
            y = 0.75
        elif loc == 1:
            y = 0.5
        else:
            y = 0.25
            
        return text, color, y
    
    
    
    
    
    def daily_to_monthly(self, preise):
        """
        

        Parameters
        ----------
        preise : Series
            Zeitreihe mit den Kursdaten auf täglicher Basis.

        Returns
        -------
        preise : Series
            Zeitreihe mit den Kursdaten auf monatlicher Basis.

        """
        # Diese Funktion wechselt die Frequenz der Daten.
        preise = pd.DataFrame({
        "Publish date" : preise.index,
        "Adj Close" : preise.values
        })
        preise = preise.groupby(pd.Grouper(key="Publish date", freq="1W")).mean()
        preise = preise["Adj Close"]
        return preise
    
    
    
    
    
    def zweihundert_tage_linie(self, preise):
        """
        

        Parameters
        ----------
        preise : Series
            Zeitreihe mit den Kursdaten.

        Returns
        -------
        p : Series
            Zeitreihe der 200 Tage Linie.

        """
        start = preise.index[0].date()
        start = datetime.datetime.combine(start, datetime.time(0,0))
        for i, index in enumerate(self.daten.index):
            if index > start:
                s =  i
                break    
        p = self.daten["Adj Close"].rolling(200).mean().iloc[s:]
        return p
    
    
    
    
    
    def plot(self, adj_close, volume, relative_staerke, adj_close_5, linie_200):
        """
        

        Parameters
        ----------
        adj_close : Series
            Zeitreihe mit den Kursdaten des letzten Jahres.
        volume : Series
            Zeitreihe mit dem Volumen des letzten Jahres.
        relative_staerke : Series
            Zeitreihe mit der Relativen stärke eines Unternehmens zur Benchmark.
        adj_close_5 : Series
            Zeitreihe mit den Kursdaten der letzten 5 Jahre.
        linie_200 : Series
            Zeitreihe der 200 Tage Linie.

        Returns
        -------
        None.

        """
        fig = plt.figure()
        
        
        # Wasserzeichen
        fig.text(0.63, 0.6375, 'ABBeV',
                 fontsize=30, color='gray',
                 ha='right', va='bottom', alpha=0.2)

        fig.text(0.63, 0.17575, 'ABBeV',
                 fontsize=30, color='gray',
                 ha='right', va='bottom', alpha=0.2)
        
        
        
        # Obere Grafik
        
        fig.set_facecolor("white")
        ax1 = fig.add_subplot(10, 1, (1, 5))
        ax1.set_facecolor("#E9E9F0")
        ax1.grid(color='white', linestyle='-', linewidth=0.75)
        ax1.set_ylabel("in $")
        ax1.tick_params(bottom=False, labelbottom=False)
        
        # Preisentwicklung 1 Jahr
        ax1.plot(adj_close, zorder=3, color="#1F508B")
        
        # Return
        text, color, y = self.return_text(adj_close, self.pos1)
        ax1.annotate(text,
                    xy=(0.975, y), xycoords='axes fraction',
                    xytext=(0, 0), textcoords='offset pixels',
                    horizontalalignment='right',
                    verticalalignment='bottom', color=color)
        
        # Relative Stärke
        ax2 = ax1.twinx()
        ax2.plot(relative_staerke, linewidth=0.5, color="#A8CD3F")
        ax2.legend(["Relativ zum GICS " + str(self.benchmark.columns[0])], fontsize="x-small", loc=0)
        
        
        
        # Mittlere Grafik
        
        # Volumen
        a = fig.add_subplot(10, 1, (6, 6))
        a.set_facecolor("#E9E9F0")
        a.grid(color='white', linestyle='-', linewidth=0.75)
        a.bar(volume.index, volume, zorder=3)
        plt.xticks(fontsize=8, rotation=10)
        a.tick_params(left=False, labelleft=False)
        
        
        
        # Untere Grafik: 5 Jahres Chart
        
        # Von Tagesdaten auf Monatsdaten
        adj_close = self.daily_to_monthly(adj_close_5)   

        # Set Up
        ax1 = fig.add_subplot(10, 1, (8, 10))
        plt.xticks(fontsize=8, rotation=10)
        ax1.set_facecolor("#E9E9F0")
        ax1.grid(color='white', linestyle='-', linewidth=0.75)
        ax1.set_ylabel("in $")
        
        # Preisentwicklung + 200 Tage Linie
        ax1.plot(adj_close, zorder=3, color="#1F508B", label='_nolegend_')
        ax1.plot(linie_200, zorder=3, linewidth=0.5, color="#A8CD3F")
        
        # Legende
        ax1.legend(["200-Tage Linie"], fontsize="x-small")
        
        # Return
        text, color, y = self.return_text(adj_close, self.pos2)
        ax1.annotate(text,
                    xy=(0.975, y), xycoords='axes fraction',
                    xytext=(0, 0), textcoords='offset pixels',
                    horizontalalignment='right',
                    verticalalignment='bottom', color=color)
        
        # Grafik anzeigen und abspeichern
        plt.show()
        name = self.ticker + "-" + datetime.datetime.today().strftime('%Y-%m-%d')
        fig.savefig(name + ".pdf", bbox_inches='tight')
        
        
        
        
        
    def main(self):
        # Lade die Zeitreihe des Unternehmens herunter.
        self.lade_daten()
        
        # Erstelle die Zeitreihen für die obere 1-Jahres Grafik.
        jahr = int(datetime.datetime.today().strftime('%Y'))-1
        adj_close, volume, relative_staerke = self.daten_fuer_chart(jahr)
        
        # Erstelle die Zeitreihen für die untere 5-Jahres Grafik.
        jahr = int(datetime.datetime.today().strftime('%Y'))-5
        adj_close_5, _, _ = self.daten_fuer_chart(jahr)
        linie_200 = self.zweihundert_tage_linie(adj_close_5)
        
        # Plotte beide Grafiken.
        self.plot(adj_close, volume, relative_staerke, adj_close_5, linie_200)
        
        
        







if __name__ == '__main__':
    benchmark = Benchmark(sektoren[sektor]).main()
    x = Chart(ticker, benchmark, pos1, pos2)
    x.main()
    daten=x.daten