# Black–Scholes Option Pricing Web Application

This project is a Python based web application that prices European call and put
options using the Black–Scholes model. The application allows users to input
option parameters through a web interface and displays the option premium,
Greeks, and volatility-related metrics on the same page.

The project was built to understand option pricing theory and its practical
implementation using Python and a simple web interface.

---

## Features
- Black–Scholes pricing for European Call and Put options
- Calculation of option Greeks:
  - Delta
  - Gamma
  - Vega
  - Theta
  - Rho
- Implied Volatility
- Webbased interface using Flask and HTML
- End to end integration between frontend and Python backend

---

## How It Works
1. The user enters option parameters (spot price, strike price, time to expiry,
   and option type) in the web interface.
2. The HTML form sends these inputs to the Flask backend.
3. The Python backend processes the inputs and applies the Black–Scholes model.
4. Option price, Greeks, and volatility metrics are calculated.
5. The results are rendered and displayed on the same web page.

---

## Running the Application Locally

### Step 1: Install dependencies
Open a terminal in the project folder and run:

    pip install -r requirements.txt
This installs all required Python libraries.

### Step 2: Start the application
    python app.py
After running this command, the Flask server starts on your local machine.

### Step 3: Open the web app
Open a browser and go to:
        
    http://127.0.0.1:3000
This address refers to the application running locally on your computer.

## Important Notes

1. This application runs locally and is not deployed on the internet.
2. The Black–Scholes model is applicable only to European options.
3. The model assumes constant volatility and interest rates.


