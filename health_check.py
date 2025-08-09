#!/usr/bin/env python3
"""
Health check script for Spectra AI services
"""
import requests
import sys
import json
from datetime import datetime

def check_service(name, url, timeout=5):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: OK")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: {str(e)}")
        return False

def main():
    """Run health checks on all services"""
    print(f"🏥 Spectra AI Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    services = [
        ("Backend API", "http://localhost:5000/health"),
        ("Frontend", "http://localhost:3000"),
        ("Ollama API", "http://localhost:11434/api/tags"),
    ]
    
    all_healthy = True
    for name, url in services:
        if not check_service(name, url):
            all_healthy = False
    
    print("=" * 50)
    if all_healthy:
        print("🎉 All services are healthy!")
        sys.exit(0)
    else:
        print("⚠️  Some services are not responding")
        sys.exit(1)

if __name__ == "__main__":
    main()
