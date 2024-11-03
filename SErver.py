import socket
import threading
import requests
import json
from datetime import datetime


HOST = '127.0.0.1'  
PORT = 65432        

API_KEY = '1d4627002635f4b7795814ca'  
API_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/'

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    with conn:
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break  
                print(f"[RECEIVED] From {addr}: {data}")
                
                request = json.loads(data)
                base = request.get('base_currency')
                target = request.get('target_currency')
                amount = request.get('amount')

                if not base or not target or amount is None:
                    response = {'error': 'Invalid request format.'}
                else:
                  
                    response = get_conversion(base, target, amount)

        
                conn.sendall(json.dumps(response).encode())
            except json.JSONDecodeError:
                response = {'error': 'Invalid JSON format.'}
                conn.sendall(json.dumps(response).encode())
            except Exception as e:
                response = {'error': str(e)}
                conn.sendall(json.dumps(response).encode())
    print(f"[DISCONNECTED] {addr} disconnected.")

def get_conversion(base, target, amount):
    try:
        api_response = requests.get(f"{API_URL}{base}", timeout=10)
        api_response.raise_for_status()
        data = api_response.json()

        if data['result'] != 'success':
            return {'error': 'Failed to fetch exchange rates.'}

        rates = data['conversion_rates']
        rate = rates.get(target)
        if rate is None:
            return {'error': f"Target currency '{target}' not found."}

        converted_amount = amount * rate
        last_updated = datetime.fromtimestamp(data['time_last_update_unix']).strftime('%Y-%m-%d %H:%M:%S')

        return {
            'base_currency': base,
            'target_currency': target,
            'original_amount': amount,
            'converted_amount': round(converted_amount, 2),
            'exchange_rate': rate,
            'last_updated': last_updated
        }
    except requests.exceptions.RequestException as e:
        return {'error': f"API request failed: {e}"}

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[LISTENING] Server is listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    print("[STARTING] Server is starting...")
    start_server()
