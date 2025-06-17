import requests
import json
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
from prettytable import PrettyTable

class StockPortfolio:
    def __init__(self, api_key, data_file='portfolio_data.json'):
        self.api_key = api_key
        self.data_file = data_file
        self.portfolio = self.load_portfolio()

    def add_stock(self, symbol, shares):
        symbol = symbol.upper()
        if symbol in self.portfolio:
            self.portfolio[symbol] += shares
        else:
            self.portfolio[symbol] = shares
        self.save_portfolio()
        return f"Added {shares} shares of {symbol}."

    def remove_stock(self, symbol, shares):
        symbol = symbol.upper()
        if symbol in self.portfolio:
            if self.portfolio[symbol] > shares:
                self.portfolio[symbol] -= shares
                msg = f"Removed {shares} shares of {symbol}."
            elif self.portfolio[symbol] == shares:
                del self.portfolio[symbol]
                msg = f"Removed all shares of {symbol}."
            else:
                msg = f"Not enough shares to remove. You have {self.portfolio[symbol]} shares."
            self.save_portfolio()
            return msg
        return f"{symbol} not found in portfolio."

    def get_stock_price(self, symbol):
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={self.api_key}'
        try:
            response = requests.get(url)
            data = response.json()
            if "Time Series (1min)" in data:
                latest_time = list(data["Time Series (1min)"])[0]
                return float(data["Time Series (1min)"][latest_time]["1. open"])
            elif "Error Message" in data:
                return None
            elif "Note" in data:
                return "API limit reached"
        except:
            return None
        return None

    def display_portfolio(self):
        table = PrettyTable()
        table.field_names = ["Symbol", "Shares", "Current Price", "Total Value"]
        total_value = 0
        for symbol, shares in self.portfolio.items():
            price = self.get_stock_price(symbol)
            if isinstance(price, float):
                value = shares * price
                total_value += value
                table.add_row([symbol, shares, f"${price:.2f}", f"${value:.2f}"])
            else:
                table.add_row([symbol, shares, "N/A", "N/A"])
        table_str = str(table)
        return f"{table_str}\nTotal Portfolio Value: ${total_value:.2f}"

    def display_all_stock_prices(self):
        popular_stocks = ["AAPL", "GOOGL", "AMZN", "TSLA", "MSFT", "NFLX", "META", "NVDA", "V"]
        table = PrettyTable()
        table.field_names = ["Symbol", "Current Price"]
        for symbol in popular_stocks:
            price = self.get_stock_price(symbol)
            table.add_row([symbol, f"${price:.2f}" if isinstance(price, float) else "N/A"])
        return str(table)

    def save_portfolio(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.portfolio, f)

    def load_portfolio(self):
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

# ---------------- GUI ----------------
class PortfolioApp:
    def __init__(self, root, portfolio):
        self.portfolio = portfolio
        self.root = root
        self.root.title("Stock Portfolio Manager")

        tk.Label(root, text="Stock Symbol:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(root, text="Shares:").grid(row=1, column=0, padx=5, pady=5)

        self.symbol_entry = tk.Entry(root)
        self.symbol_entry.grid(row=0, column=1, padx=5, pady=5)

        self.shares_entry = tk.Entry(root)
        self.shares_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(root, text="Add Stock", command=self.add_stock).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(root, text="Remove Stock", command=self.remove_stock).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(root, text="View Portfolio", command=self.view_portfolio).grid(row=2, column=0, columnspan=1, padx=5, pady=5)
        tk.Button(root, text="View Popular Stock Prices", command=self.view_popular).grid(row=2, column=1, columnspan=2, padx=5, pady=5)

        self.output = scrolledtext.ScrolledText(root, width=80, height=20)
        self.output.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

    def log(self, message):
        self.output.delete('1.0', tk.END)
        self.output.insert(tk.END, message)

    def add_stock(self):
        symbol = self.symbol_entry.get()
        try:
            shares = int(self.shares_entry.get())
            msg = self.portfolio.add_stock(symbol, shares)
        except ValueError:
            msg = "Invalid number of shares."
        self.log(msg)

    def remove_stock(self):
        symbol = self.symbol_entry.get()
        try:
            shares = int(self.shares_entry.get())
            msg = self.portfolio.remove_stock(symbol, shares)
        except ValueError:
            msg = "Invalid number of shares."
        self.log(msg)

    def view_portfolio(self):
        output = self.portfolio.display_portfolio()
        self.log(output)

    def view_popular(self):
        output = self.portfolio.display_all_stock_prices()
        self.log(output)

# ---------------- Main Execution ----------------
if __name__ == "__main__":
    api_key = "751|7DvtnRaNvLuN7loRKePhSkTF0xYugafmHLgxLbzu"  # Your provided API key
    portfolio = StockPortfolio(api_key)

    root = tk.Tk()
    app = PortfolioApp(root, portfolio)
    root.mainloop()

