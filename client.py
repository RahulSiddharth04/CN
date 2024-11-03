import streamlit as st
import socket
import json
from datetime import datetime


SERVER_HOST = '127.0.0.1' 
SERVER_PORT = 65432      

def send_request(base, target, amount):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))
            request = {
                'base_currency': base,
                'target_currency': target,
                'amount': amount
            }
            s.sendall(json.dumps(request).encode())
            data = s.recv(4096).decode()
            response = json.loads(data)
            return response
    except ConnectionRefusedError:
        return {'error': 'Could not connect to the server. Make sure the server is running.'}
    except Exception as e:
        return {'error': f"An error occurred: {e}"}

def main():
    st.title("💱 Currency Converter with TCP Connection")

    st.sidebar.header("Conversion Settings")

    amount = st.sidebar.number_input("Amount", min_value=0.0, value=1.0, step=0.1)

    currencies = ['USD', 'EUR', 'GBP', 'JPY','NZD','INR']
    base_currency = st.sidebar.selectbox("From", currencies, index=0)

    target_currency = st.sidebar.selectbox("To", currencies, index=1)

    if st.sidebar.button("Convert"):
        with st.spinner("Connecting to the server and fetching exchange rates..."):
            response = send_request(base_currency, target_currency, amount)
            if 'error' in response:
                st.error(response['error'])
            else:
                st.success(f"{response['original_amount']} {response['base_currency']} = {response['converted_amount']} {response['target_currency']}")
                st.write(f"**Exchange Rate:** 1 {response['base_currency']} = {response['exchange_rate']} {response['target_currency']}")
                st.write(f"**Last Updated:** {response['last_updated']}")

    if st.checkbox("Show All Exchange Rates"):
        with st.spinner("Fetching all exchange rates..."):
            response = send_request(base_currency, base_currency, 1)  
            if 'error' in response:
                st.error(response['error'])
            else:
                st.write(f"**Exchange Rates for {response['base_currency']}:**")
                rates = response.get('exchange_rate') or response.get('converted_amount')  
  
                st.write("Feature not implemented in server.")
                st.info("To view all exchange rates, extend the server to handle such requests.")

if __name__ == "__main__":
    main()
