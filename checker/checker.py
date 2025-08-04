#!/usr/bin/env python3
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
    session.timeout = 10
    
    try:
        
        response = session.get(f"{base_url}/")
        if response.status_code != 200:
            print(f"Main page not accessible: {response.status_code}")
            return False
            
        
        response = session.get(f"{base_url}/auth/register-page")
        if response.status_code != 200:
            print(f"Register page not accessible: {response.status_code}")
            return False
            
        
        response = session.get(f"{base_url}/auth/login-page")
        if response.status_code != 200:
            print(f"Login page not accessible: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return False

def put_flag(host, port, flag):
    """Put flag into service by creating a product with secret field"""
    base_url = f"http://{host}:{port}"
    session = requests.Session()
    session.timeout = 15
    
    try:
        
        checker_data = {
            'username': 'checker',
            'password': '238074303089'
        }
        
        response = session.post(f"{base_url}/auth/login", data=checker_data)
        if response.status_code not in [200, 302]:
            print(f"Checker login failed: {response.status_code}")
            return False
        
        
        if "Неверное имя пользователя или пароль" in response.text:
            print("Checker login failed: Invalid credentials")
            return False
            
        
        product_data = {
            'name': f"🚩 CTF Product {generate_random_string(4)}",
            'description': f"Special CTF challenge item - {generate_random_string(8)}",
            'price': random.randint(50, 500),
            'secret': flag  # Flag stored in secret field
        }
        
        response = session.post(f"{base_url}/products/add", data=product_data)
        if response.status_code not in [200, 302]:
            print(f"Product creation failed: {response.status_code}")
            return False
            
        print(f"Flag {flag} successfully placed")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error putting flag: {e}")
        return False

def get_flag(host, port, flag):
    """Get flag from service via admin panel"""
    base_url = f"http://{host}:{port}"
    session = requests.Session()
    session.timeout = 15
    
    try:
        
        checker_data = {
            'username': 'checker',
            'password': '238074303089'
        }
        
        response = session.post(f"{base_url}/auth/login", data=checker_data)
        if response.status_code not in [200, 302]:
            print(f"Checker login failed: {response.status_code}")
            return False
        
        
        if "Неверное имя пользователя или пароль" in response.text:
            print("Checker login failed: Invalid credentials")
            return False
            
        
        response = session.get(f"{base_url}/details")
        if response.status_code != 200:
            print(f"Details panel not accessible: {response.status_code}")
            return False
            
        
        if "Redirecting" in response.text:
            print("Details panel access denied - redirected")
            return False
            
        
        if flag in response.text:
            print(f"Flag {flag} successfully retrieved")
            return True
        else:
            print(f"Flag {flag} not found in response")
            print(f"Response length: {len(response.text)} chars")
           
            if "Товары" in response.text:
                flag_count = response.text.count("text-warning bg-dark")
                print(f"Found {flag_count} products with flags on the page")
            else:
                print("No products with flags section found")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error getting flag: {e}")
        return False

def main():
    """Main entry point for ctf01d checker"""
    if len(sys.argv) < 3:
        print("Usage: checker.py <host> <action> [flag] [uuid]", file=sys.stderr)
        sys.exit(2)  
        
    host = sys.argv[1]
    action = sys.argv[2]
    port = 5000  
    flag = sys.argv[3] if len(sys.argv) > 3 else None
    
    if action == "check":
        
        if check_service(host, port):
            sys.exit(101) 
        else:
            sys.exit(104)  
            
    elif action == "put":
        if not flag:
            sys.exit(110)  
        if put_flag(host, port, flag):
            sys.exit(101)  
        else:
            sys.exit(103)  
            
    elif action == "get":
        if not flag:
            sys.exit(110)  
            
        if get_flag(host, port, flag):
            sys.exit(101)  
        else:
            sys.exit(103)  
            
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(2) 

if __name__ == "__main__":
    main()