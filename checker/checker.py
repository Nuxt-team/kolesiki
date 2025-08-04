import requests
import sys
import json
import time
import random
import string

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def check_service(host, port):
    """Simple service availability check"""
    base_url = f"http://{host}:{port}"
    session = requests.Session()
    session.timeout = 2
    
    try:
        response = session.get(f"{base_url}/")
        if response.status_code != 200:
            return False
        return True
        
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False
    except requests.exceptions.RequestException:
        return False

def put_flag(host, port, flag):
    """Put flag into service by creating a product with secret field"""
    base_url = f"http://{host}:{port}"
    session = requests.Session()
    session.timeout = 3
    
    try:
        checker_data = {
            'username': 'checker',
            'password': '238074303089'
        }
        
        response = session.post(f"{base_url}/auth/login", data=checker_data)
        if response.status_code not in [200, 302]:
            return "corrupt"
        
        if "Неверное имя пользователя или пароль" in response.text:
            return "corrupt"
            
        product_data = {
            'name': f"CTF_{generate_random_string(3)}",
            'description': f"Test item",
            'price': 100,
            'secret': flag
        }
        
        response = session.post(f"{base_url}/products/add", data=product_data)
        if response.status_code not in [200, 302]:
            return "corrupt"
            
        return "ok"
        
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return "down"
    except requests.exceptions.RequestException:
        return "corrupt"

def get_flag(host, port, flag):
    """Get flag from service via admin panel"""
    base_url = f"http://{host}:{port}"
    session = requests.Session()
    session.timeout = 3
    
    try:
        checker_data = {
            'username': 'checker',
            'password': '238074303089'
        }
        
        response = session.post(f"{base_url}/auth/login", data=checker_data)
        if response.status_code not in [200, 302]:
            return "corrupt"
        
        if "Неверное имя пользователя или пароль" in response.text:
            return "corrupt"
            
        response = session.get(f"{base_url}/details")
        if response.status_code != 200:
            return "corrupt"
            
        if "Redirecting" in response.text:
            return "corrupt"
            
        if flag in response.text:
            return "ok"
        else:
            return "corrupt"
            
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return "down"
    except requests.exceptions.RequestException:
        return "corrupt"

def main():
    """Main entry point for ctf01d checker"""
    if len(sys.argv) < 3:
        sys.exit(104)
        
    host = sys.argv[1]
    command = sys.argv[2]
    f_id = sys.argv[3] if len(sys.argv) > 3 else None
    flag = sys.argv[4] if len(sys.argv) > 4 else None
    port = 5000  
    
    if command == "check":
        if check_service(host, port):
            sys.exit(101)
        else:
            sys.exit(104)
            
    elif command == "put":
        if not flag:
            sys.exit(104)
        result = put_flag(host, port, flag)
        if result == "ok":
            sys.exit(101)
        elif result == "down":
            sys.exit(104)
        else:
            sys.exit(102)
            
    elif command == "get":
        if not flag:
            sys.exit(104)
            
        result = get_flag(host, port, flag)
        if result == "ok":
            sys.exit(101)
        elif result == "down":
            sys.exit(104)
        else:
            sys.exit(102)
            
    else:
        sys.exit(104)

if __name__ == "__main__":
    main()