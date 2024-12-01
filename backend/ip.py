import requests

def get_public_ip():
    try:
        # Use an external service to get public IP address
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()  # Raise an exception for HTTP errors
        ip_info = response.json()
        return ip_info['ip']
    except requests.RequestException as e:
        print(f"Error getting public IP: {e}")
        return None

# Example usage
public_ip = get_public_ip()
if public_ip:
    print(f"Your public IP address is: {public_ip}")
else:
    print("Could not retrieve public IP address.")
