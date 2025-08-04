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
    base_url = f"http://{host}:{port}"
    session = requests.Session()
    session.timeout = 10
    
    try:
        # 1. Проверяем доступность главной страницы
        response = session.get(f"{base_url}/")
        if response.status_code != 200:
            print(f"Main page not accessible: {response.status_code}")
            return False
            
        # 2. Проверяем страницу регистрации
        response = session.get(f"{base_url}/auth/register-page")
        if response.status_code != 200:
            print(f"Register page not accessible: {response.status_code}")
            return False
            
        # 3. Проверяем страницу входа
        response = session.get(f"{base_url}/auth/login-page")
        if response.status_code != 200:
            print(f"Login page not accessible: {response.status_code}")
            return False
            
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return False

def put_flag(host, port, flag):
    base_url = f"http://{host}:{port}"
    session = requests.Session()
    session.timeout = 15
    
    try:
        # Создаем случайного пользователя
        username = f"user_{generate_random_string(6)}"
        password = generate_random_string(10)
        
        # Регистрируемся
        register_data = {
            'username': username,
            'password': password,
            'password_confirm': password
        }
        
        response = session.post(f"{base_url}/auth/register", data=register_data)
        if response.status_code not in [200, 302]:
            print(f"Registration failed: {response.status_code}")
            return False
            
        # Логинимся
        login_data = {
            'username': username,
            'password': password
        }
        
        response = session.post(f"{base_url}/auth/login", data=login_data)
        if response.status_code not in [200, 302]:
            print(f"Login failed: {response.status_code}")
            return False
            
        # Создаем товар с флагом
        product_data = {
            'name': f"Product_{generate_random_string(6)}",
            'description': f"Description for {generate_random_string(8)}",
            'price': random.randint(100, 1000),
            'secret': flag  # Флаг сохраняем в секретное поле
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
    base_url = f"http://{host}:{port}"
    session = requests.Session()
    session.timeout = 15
    
    try:
        # Проверяем доступность API товаров с флагами (только для админа)
        admin_data = {
            'username': 'admin',
            'password': '0121077111290936'
        }
        
        response = session.post(f"{base_url}/auth/login", data=admin_data)
        if response.status_code not in [200, 302]:
            print(f"Admin login failed: {response.status_code}")
            return False
            
        # Получаем товары с флагами через админ панель
        response = session.get(f"{base_url}/details")
        if response.status_code != 200:
            print(f"Admin panel not accessible: {response.status_code}")
            return False
            
        # Проверяем наличие флага в HTML или через API
        if flag in response.text:
            print(f"Flag {flag} successfully retrieved")
            return True
        else:
            print(f"Flag {flag} not found in response")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Error getting flag: {e}")
        return False

def main():
    if len(sys.argv) < 4:
        print("Usage: checker.py <action> <host> <port> [flag]")
        sys.exit(1)
        
    action = sys.argv[1]
    host = sys.argv[2]
    port = sys.argv[3]
    
    if action == "check":
        # Простая проверка доступности сервиса
        if check_service(host, port):
            print("Service is UP")
            sys.exit(0)  # OK
        else:
            print("Service is DOWN")
            sys.exit(1)  # DOWN
            
    elif action == "put":
        if len(sys.argv) < 5:
            print("Flag required for put action")
            sys.exit(1)
        flag = sys.argv[4]
        
        if put_flag(host, port, flag):
            print(f"Flag {flag} put successfully")
            sys.exit(0)  # OK
        else:
            print(f"Failed to put flag {flag}")
            sys.exit(1)  # CORRUPT
            
    elif action == "get":
        if len(sys.argv) < 5:
            print("Flag required for get action")
            sys.exit(1)
        flag = sys.argv[4]
        
        if get_flag(host, port, flag):
            print(f"Flag {flag} retrieved successfully")
            sys.exit(0)  # OK
        else:
            print(f"Failed to get flag {flag}")
            sys.exit(1)  # CORRUPT
            
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()