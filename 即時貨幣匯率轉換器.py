# Importing necessary libraries
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import requests
import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
import yfinance as yf
import sys
import numpy as np
from sklearn.linear_model import LinearRegression

# Function to fetch the user's IP country
def get_user_ip_country():
    try:
        response = requests.get('https://ipinfo.io/json')  # Sending a GET request to retrieve IP information
        data = response.json()  # Parsing the JSON response
        return data['country']  # Extracting the country code from the response
    except Exception as e:
        print("Error fetching user's IP country:", e)
        return None
    
# Function to fetch the user's country currency
def get_user_country_currency():
    try:
        response = requests.get('https://ipinfo.io/json')  # Sending a GET request to retrieve IP information
        data = response.json()  # Parsing the JSON response
        country_code = data['country']  # Extracting the country code from the response
        country_currency = country_currency_mapping.get(country_code)  # Retrieving currency code based on country code
        return country_currency  # Returning the currency code
    except Exception as e:
        print("Error fetching user's country currency:", e)
        return None

# Function to get exchange rate between two currencies
def get_exchange_rate_with_time(base_currency, target_currency):
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"  # Constructing the API endpoint URL
    response = requests.get(url)  # Sending a GET request to fetch exchange rate data
    data = response.json()  # Parsing the JSON response
    if 'error' in data:  # Checking if the response contains an error
        raise Exception("無法獲取數據")  # Raising an exception if an error is present in the response
    try:
        exchange_rate = data['rates'][target_currency]  # Extracting the exchange rate for the target currency
        last_update = datetime.datetime.fromtimestamp(data['time_last_updated']).strftime('%Y-%m-%d %H:%M:%S')  # Formatting last update time
        return exchange_rate, last_update  # Returning the exchange rate and last update time
    except KeyError:
        raise Exception("請檢查貨幣代碼是否正確")  # Raising an exception if the target currency code is incorrect

# Function to update base currency selection in conversion tab
def set_base_currency_menu(event):
    base_currency_entry.delete(0, tk.END)  # Clearing the base currency entry field
    base_currency_entry.insert(0, event.widget.get())  # Inserting the selected currency into the entry field

# Function to update target currency selection in conversion tab
def set_target_currency_menu(event):
    target_currency_entry.delete(0, tk.END)  # Clearing the target currency entry field
    target_currency_entry.insert(0, event.widget.get())  # Inserting the selected currency into the entry field

# Function to update base currency selection in historical rates tab
def set_base_currency_history_menu(event):
    base_currency_entry_history.delete(0, tk.END)  # Clearing the base currency entry field
    base_currency_entry_history.insert(0, event.widget.get())  # Inserting the selected currency into the entry field

# Function to update target currency selection in historical rates tab
def set_target_currency_history_menu(event):
    target_currency_entry_history.delete(0, tk.END)  # Clearing the target currency entry field
    target_currency_entry_history.insert(0, event.widget.get())  # Inserting the selected currency into the entry field

# Function to convert currency
def convert_currency():
    base_currency = base_currency_entry.get().upper()  # Getting the base currency from the entry field and converting to uppercase
    target_currency = target_currency_entry.get().upper()  # Getting the target currency from the entry field and converting to uppercase
    amount_text = amount_entry.get()  # Getting the amount to convert from the entry field

    errors = []  # List to store validation errors

    # Validating base currency code
    if len(base_currency) != 3 or not base_currency.isalpha():
        errors.append("請輸入有效的三位貨幣代碼作為基準貨幣")

    # Validating target currency code
    if len(target_currency) != 3 or not target_currency.isalpha():
        errors.append("請輸入有效的三位貨幣代碼作為目標貨幣")

    try:
        amount = float(amount_text)  # Converting amount to float
        if amount <= 0:  # Checking if amount is positive
            errors.append("請輸入有效金額") 
    except ValueError:
        errors.append("請輸入有效金額")

    # Displaying validation errors if any
    if errors:
        error_message = "\n".join(errors)
        messagebox.showerror("錯誤", error_message)
    else:
        try:
            # Fetching exchange rate and last update time
            exchange_rate, last_update = get_exchange_rate_with_time(base_currency, target_currency)
            # Calculating converted amount
            converted_amount = amount * exchange_rate
            # Getting current time
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Constructing result message
            result_message = f"{amount} {base_currency} = {converted_amount} {target_currency}\n匯率更新時間: {last_update}\n現在時間: {current_time}"
            # Displaying result message
            messagebox.showinfo("轉換結果", result_message)
        except Exception as e:
            messagebox.showerror("錯誤", "無法獲取數據。請檢查貨幣代碼是否正確。")

# Function to open currency code page in web browser
def open_currency_code_page():
    webbrowser.open("https://www.cbc.gov.tw/public/attachment/210309373671.pdf")

# Function to query historical exchange rates
def query_history_rate():
    base_currency_history = base_currency_entry_history.get().upper()  # Getting base currency for historical rates
    target_currency_history = target_currency_entry_history.get().upper()  # Getting target currency for historical rates
    start_date_text = start_date_entry.get()  # Getting start date for historical rates
    end_date_text = end_date_entry.get()  # Getting end date for historical rates

    errors = []  # List to store validation errors

    # Validating base currency code
    if len(base_currency_history) != 3 or not base_currency_history.isalpha():
        errors.append("請輸入有效的三位貨幣代碼作為基準貨幣")

    # Validating target currency code
    if len(target_currency_history) != 3 or not target_currency_history.isalpha():
        errors.append("請輸入有效的三位貨幣代碼作為目標貨幣")

    try:
        start_date = datetime.datetime.strptime(start_date_text, '%Y-%m-%d')  # Parsing start date
        end_date = datetime.datetime.strptime(end_date_text, '%Y-%m-%d')  # Parsing end date
        start_date_text = start_date.strftime('%Y-%m-%d')  # Formatting start date
        end_date_text = end_date.strftime('%Y-%m-%d')  # Formatting end date
        if start_date > end_date:  # Checking if start date is after end date
            errors.append("起始日期不能晚於結束日期")
    except ValueError:
        errors.append("請輸入有效的日期，格式為YYYY-MM-DD")

    # Displaying validation errors if any
    if errors:
        error_message = "\n".join(errors)
        messagebox.showerror("錯誤", error_message)
    else:
        try:
            # Fetching historical exchange rate data
            data = yf.download(f"{base_currency_history}{target_currency_history}=X", start=start_date_text, end=end_date_text)

            # Calculate moving average
            data['Moving_Average'] = data['Close'].rolling(window=10).mean()

            # Linear Regression Model for prediction
            X = np.array(data.index.map(datetime.datetime.toordinal)).reshape(-1, 1)
            y = data['Close'].values
            model = LinearRegression()
            model.fit(X, y)

            # Predict future dates
            future_dates = np.arange(X[-1][0] + 1, X[-1][0] + 6).reshape(-1, 1)
            future_exchange_rates = model.predict(future_dates)

            # Plotting the rate with moving average and predicted future rates
            fig, ax = plt.subplots()
            ax.plot(data.index, data['Close'], label='Close', linestyle='-')
            ax.plot(data.index, data['Moving_Average'], label='Moving Average', linestyle='--')
            ax.set_title(f'Historical Exchange Rates ({base_currency_history} to {target_currency_history})')
            ax.set_xlabel('Date')
            ax.set_ylabel('Exchange Rate')           
            ax.grid(True)

            # Plot historical trend line in blue
            ax.plot(data.index, model.predict(X), label='Historical Trend', linestyle='-', color='blue')

            # Plot predicted future rates in red
            future_dates = [datetime.datetime.fromordinal(int(date)) for date in future_dates.flatten()]
            ax.plot(future_dates, future_exchange_rates, label='Predicted Exchange Rate', linestyle='-', color='red')

            # Formatting the time ticks on the x-axis to show only month and day with 5-day intervals
            ax.xaxis.set_major_locator(matplotlib.dates.AutoDateLocator())
            ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%m-%d'))
            ax.legend()
            # Show plot in Tkinter window
            fig_canvas = FigureCanvasTkAgg(fig, master=tab2)
            fig_canvas.draw()
            fig_canvas.get_tk_widget().grid(row=5, column=0, columnspan=3, padx=5, pady=5)

        except Exception as e:
            messagebox.showerror("錯誤", "無法獲取數據。請檢查輸入的資訊是否正確。")


def on_closing():
    # 清理工作
    root.destroy()
    sys.exit()

# Creating main Tkinter window
root = tk.Tk()
root.title("即時貨幣匯率轉換器")

# Setting window closing event
root.protocol("WM_DELETE_WINDOW", on_closing)

# Mapping of country codes to currency codes
country_currency_mapping = {
    'US': 'USD', # United States Dollar
    'JP': 'JPY', # Japanese Yen
    'HK': 'HKD', # Hong Kong Dollar
    'CN': 'CNY', # Chinese Yuan
    'TW': 'TWD', # Taiwan Dollar
    'KR': 'KRW', # South Korean Won
    # Add more country currency mappings as needed
}

# Get the user's country currency
initial_base_currency = get_user_country_currency()
ip_country = get_user_ip_country()

# Create a Notebook
notebook = ttk.Notebook(root)
notebook.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

# Create tabs
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

# Add tabs to Notebook
notebook.add(tab1, text='轉換貨幣')
notebook.add(tab2, text='歷史匯率')

# Base currency for conversion tab
base_currency_label = tk.Label(tab1, text="基準貨幣:")
base_currency_label.grid(row=0, column=0, padx=5, pady=5)
base_currency_entry = ttk.Entry(tab1)
base_currency_entry.grid(row=0, column=1, padx=5, pady=5)
base_currency_entry.insert(0, initial_base_currency)
base_currency_menu = ttk.Combobox(tab1, values=["USD", "EUR", "GBP", "JPY", "CNY"], state="readonly")
base_currency_menu.set("常用貨幣")
base_currency_menu.bind("<<ComboboxSelected>>", set_base_currency_menu)
base_currency_menu.grid(row=0, column=2, padx=5, pady=5)

# Target currency for conversion tab
target_currency_label = tk.Label(tab1, text="目標貨幣:")
target_currency_label.grid(row=1, column=0, padx=5, pady=5)
target_currency_entry = ttk.Entry(tab1)
target_currency_entry.grid(row=1, column=1, padx=5, pady=5)
target_currency_menu = ttk.Combobox(tab1, values=["USD", "EUR", "GBP", "JPY", "CNY"], state="readonly")
target_currency_menu.set("常用貨幣")
target_currency_menu.bind("<<ComboboxSelected>>", set_target_currency_menu)
target_currency_menu.grid(row=1, column=2, padx=5, pady=5)

# Amount for conversion tab
amount_label = tk.Label(tab1, text="金額:")
amount_label.grid(row=2, column=0, padx=5, pady=5)
amount_entry = ttk.Entry(tab1)
amount_entry.grid(row=2, column=1, padx=5, pady=5)

# Button to query currency code for conversion tab
currency_code_button = tk.Button(tab1, text="查詢貨幣代碼", command=open_currency_code_page)
currency_code_button.grid(row=2, column=2, padx=5, pady=5)

# Displaying detected IP country and default base currency
ip_country_label = tk.Label(tab1, text="檢測到當前IP地區為: {}, 以自動將基準貨幣默認為: {}".format(ip_country, initial_base_currency))
ip_country_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)

# Button to convert currency
convert_button = tk.Button(tab1, text="轉換貨幣價值", command=convert_currency)
convert_button.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

# Base currency for historical rates tab
base_currency_label_history = tk.Label(tab2, text="基準貨幣:")
base_currency_label_history.grid(row=0, column=0, padx=5, pady=5)
base_currency_entry_history = ttk.Entry(tab2)
base_currency_entry_history.grid(row=0, column=1, padx=5, pady=5)
base_currency_entry_history.insert(0, initial_base_currency)
base_currency_menu_history = ttk.Combobox(tab2, values=["USD", "EUR", "GBP", "JPY", "CNY"], state="readonly")
base_currency_menu_history.set("常用貨幣")
base_currency_menu_history.grid(row=0, column=2, padx=5, pady=5)
base_currency_menu_history.bind("<<ComboboxSelected>>", set_base_currency_history_menu)

# Target currency for historical rates tab
target_currency_label_history = tk.Label(tab2, text="目標貨幣:")
target_currency_label_history.grid(row=1, column=0, padx=5, pady=5)
target_currency_entry_history = ttk.Entry(tab2)
target_currency_entry_history.grid(row=1, column=1, padx=5, pady=5)
target_currency_menu_history = ttk.Combobox(tab2, values=["USD", "EUR", "GBP", "JPY", "CNY"], state="readonly")
target_currency_menu_history.set("常用貨幣")
target_currency_menu_history.grid(row=1, column=2, padx=5, pady=5)
target_currency_menu_history.bind("<<ComboboxSelected>>", set_target_currency_history_menu)

# Date entry for historical rates tab
start_date_label = tk.Label(tab2, text="起始日期:")
start_date_label.grid(row=2, column=0, padx=5, pady=5)
start_date_entry = ttk.Entry(tab2)
start_date_entry.grid(row=2, column=1, padx=5, pady=5)

end_date_label = tk.Label(tab2, text="結束日期:")
end_date_label.grid(row=3, column=0, padx=5, pady=5)
end_date_entry = ttk.Entry(tab2)
end_date_entry.grid(row=3, column=1, padx=5, pady=5)

# Button to query historical rates
history_button = tk.Button(tab2, text="查詢歷史匯率", command=query_history_rate)
history_button.grid(row=3, column=2, padx=5, pady=5)
ip_country_label = tk.Label(tab2, text="檢測到當前IP地區為: {}, 以自動將基準貨幣默認為: {}".format(ip_country, initial_base_currency))
ip_country_label.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

# Running the Tkinter event loop
root.mainloop()
