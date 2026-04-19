# utils.py
import requests
import json
from config import HEROSMS_API_URL, HEROSMS_API_KEY, COUNTRIES, SERVICES

def make_api_request(action, params=None):
    """Make request to HeroSMS API"""
    url = f"{HEROSMS_API_URL}?action={action}&api_key={HEROSMS_API_KEY}"
    if params:
        for key, value in params.items():
            url += f"&{key}={value}"
    
    try:
        response = requests.get(url, timeout=30)
        return response.text
    except Exception as e:
        return f"ERROR: {str(e)}"

def parse_balance_response(response):
    """Parse balance response"""
    if response.startswith("ACCESS_BALANCE:"):
        return float(response.split(":")[1])
    return None

def parse_number_v2_response(response):
    """Parse V2 number response (JSON)"""
    try:
        data = json.loads(response)
        if "activationId" in data:
            return data
    except:
        pass
    return None

def get_country_name(country_id):
    """Get country name from ID"""
    return COUNTRIES.get(int(country_id), f"ID: {country_id}")

def get_service_name(service_code):
    """Get service name from code"""
    return SERVICES.get(service_code.lower(), service_code.upper())

def format_phone_number(phone):
    """Format phone number for display"""
    if len(phone) == 11:
        return f"+{phone[0]} {phone[1:4]} {phone[4:7]} {phone[7:]}"
    elif len(phone) == 10:
        return f"+{phone[0]} {phone[1:4]} {phone[4:7]} {phone[7:]}"
    return phone