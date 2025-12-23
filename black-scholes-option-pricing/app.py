# Calculating options premium and greeks using Black-Scholes formula in Python

import numpy as np
from scipy.stats import norm
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from arch import arch_model
from flask import Flask, render_template, request
from flask import send_from_directory
import plotly.graph_objs as go

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def calculate_option():
    candlestick = None
    if request.method == 'POST':
        try:
            # Parse user input from the form
            ticker = request.form['ticker']
            spot_price = float(request.form['spot_price'])
            strike_price = float(request.form['strike_price'])
            time_to_expiry = float(request.form['time_to_expiry'])
            type = request.form['option_type']

            ################################################################################################
            
            # Fetch historical price data from Yahoo Finance for candlestick chart
            stock = yf.Ticker(ticker)
            history_data = stock.history(period="5y")

            # Create a candlestick chart
            candlestick = go.Figure(data=[go.Candlestick(
                x=history_data.index,
                open=history_data['Open'],
                high=history_data['High'],
                low=history_data['Low'],
                close=history_data['Close'],
                name="Candlestick"
            )])

            candlestick.update_layout(
                title=f'Candlestick Chart for {ticker}',
                xaxis_title='Date',
                yaxis_title='Price',
            )
            # Findiang Volatility using Garch Model #############################################################

            # Define the stock symbol and download historical data
            data = yf.download(ticker, period='252d', progress=False)

            # Calculate daily returns
            data["Returns"] = data["Close"].pct_change()*100

            # Drop rows with missing or infinite values
            data.dropna(subset=["Returns"], inplace=True)

            # Define the GARCH model
            model = arch_model(data["Returns"], vol='Garch', p=1, q=1)

            # Fit the model
            results = model.fit(disp="off")

            # Forecast volatility for the next period
            forecasted_volatility = round((results.forecast(horizon=1).variance.values[-1][0]),4)
            annualized_volatility = round(((forecasted_volatility ** 0.5) * (252 ** 0.5)), 4)

            ##################################################################################################

            #Getting risk free rate fron RBI website

            # URL of the RBI webpage
            url = 'https://www.rbi.org.in/Scripts/BS_NSDPDisplay.aspx?param=4'

            # HTTP GET request to the RBI webpage
            response = requests.get(url)

            # Checking if the request was successful (status code 200)
            if response.status_code == 200:
                # Parse the HTML content of the page
                soup = BeautifulSoup(response.text, 'html.parser')

                # Finding all tables on the page
                tables = soup.find_all('table')

                # Search for the table containing the required risk free rate
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        columns = row.find_all('td')
                        if len(columns) > 0 and columns[0].text.strip() == "91-Day Treasury Bill (Primary) Yield":
                            yield_value = round((float(columns[-1].text.strip())/100),4)
                            #print(f"91-Day Treasury Bill (Primary) Yield: {yield_value}")
                            break  # Stop searching once found
                    else:
                        continue  # Continue searching in other tables
                    break  # Stop searching once found
                else:
                    print("91-Day Treasury Bill (Primary) Yield not found on the page.")
            else:
                print(f"Error: Failed to fetch the RBI webpage (Status Code: {response.status_code})")

            #########################################################################################################

            # Define variables for blackscholes and greeks formula
            r = yield_value #risk free rate
            S = spot_price #spot price
            K = strike_price #strike price
            T = time_to_expiry/365 #time
            vol = annualized_volatility/100 #volatility
            option_type = type # Call or Put contract

            def blackScholes(r, S, K, T, vol, option_type="call"):
                "Calculate price of call/put"
                d1 = (np.log(S/K) + (r + vol**2/2)*T)/(vol*np.sqrt(T))
                d2 = d1 - vol*np.sqrt(T)
                try:
                    if option_type == "call":
                        price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
                    elif option_type == "put":
                        price = K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
                    return price
                except:
                    print("Please confirm option type, either 'c' for Call or 'p' for Put!")

            def delta(r, S, K, T, vol, option_type="call"):
                "Calculate delta of an option"
                d1 = (np.log(S/K) + (r + vol**2/2)*T)/(vol*np.sqrt(T))
                try:
                    if option_type == "call":
                        delta = (norm.cdf(d1)) 
                    elif option_type == "put":
                        delta = (-norm.cdf(-d1)) 
                    return delta * 100
                except:
                    print("Please confirm option type, either 'c' for Call or 'p' for Put!")

            def gamma(r, S, K, T, vol, option_type="call"):
                "Calculate gamma of a option"
                d1 = (np.log(S/K) + (r + vol**2/2)*T)/(vol*np.sqrt(T))
                d2 = d1 - vol*np.sqrt(T)
                try:
                    gamma = norm.pdf(d1)/(S*vol*np.sqrt(T))
                    return gamma
                except:
                    print("Please confirm option type, either 'c' for Call or 'p' for Put!")

            def vega(r, S, K, T, vol, option_type="call"):
                "Calculate vega of a option"
                d1 = (np.log(S/K) + (r + vol**2/2)*T)/(vol*np.sqrt(T))
                d2 = d1 - vol*np.sqrt(T)
                try:
                    vega = S*norm.pdf(d1)*np.sqrt(T)
                    return vega/100
                except:
                    print("Please confirm option type, either 'c' for Call or 'p' for Put!")

            def theta(r, S, K, T, vol, option_type="call"):
                "Calculate theta of a option"
                d1 = (np.log(S/K) + (r + vol**2/2)*T)/(vol*np.sqrt(T))
                d2 = d1 - vol*np.sqrt(T)
                try:
                    if option_type == "call":
                        theta = -((S*norm.pdf(d1)*vol)/(2*np.sqrt(T))) - r*K*np.exp(-r*T)*norm.cdf(d2)
                    elif option_type == "put":
                        theta = -((S*norm.pdf(d1)*vol)/(2*np.sqrt(T))) + r*K*np.exp(-r*T)*norm.cdf(-d2)
                    return theta / 365
                except:
                    print("Please confirm option type, either 'c' for Call or 'p' for Put!")

            def rho(r, S, K, T, vol, option_type="call"):
                "Calculate rho of a option"
                d1 = (np.log(S/K) + (r + vol**2/2)*T)/(vol*np.sqrt(T))
                d2 = d1 - vol*np.sqrt(T)
                try:
                    if option_type == "call":
                        rho = K*T*np.exp(-r*T)*norm.cdf(d2)
                    elif option_type == "put":
                        rho = -K*T*np.exp(-r*T)*norm.cdf(-d2)
                    return rho * 0.01
                except:
                    print("Please confirm option type, either 'c' for Call or 'p' for Put!")
        
            option_price = round(blackScholes(r, S, K, T, vol, option_type), 4)
            delta_value = round(delta(r, S, K, T, vol, option_type), 4) 
            gamma_value = round(gamma(r, S, K, T, vol, option_type), 4) 
            vega_value = round(vega(r, S, K, T, vol, option_type), 4)
            theta_value = round(theta(r, S, K, T, vol, option_type), 4)
            rho_value = round(rho(r, S, K, T, vol, option_type), 5)
            predicted_volatility = f"{annualized_volatility:.2f}%"

            return render_template('index.html', ticker=ticker, option_price=option_price,
                                   delta=delta_value, gamma=gamma_value, vega=vega_value,
                                   theta=theta_value, rho=rho_value,predicted_volatility=predicted_volatility, candlestick=candlestick.to_html())
         
        except Exception as e:
            error_message = str(e)
            return render_template('index.html', error=error_message)

    return render_template('index.html', error=None)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000 )