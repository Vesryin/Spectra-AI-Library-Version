#!/usr/bin/env python3
"""
Deployment verification script for Spectra AI
Tests the deployed application endpoints
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, Any

async def test_deployment(base_url: str) -> Dict[str, Any]:
    """Test the deployed Spectra AI application"""
    
    results = {
        "base_url": base_url,
        "health_check": False,
        "status_endpoint": False,
        "chat_test": False,
        "providers": [],
        "errors": []
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test health check
            print(f"🔍 Testing health check at {base_url} ...")
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    results["health_check"] = True
                    print("✅ Health check passed")
                else:
                    results["errors"].append(f"Health check failed: {response.status}")
                    print(f"❌ Health check failed: {response.status}")
        
        except Exception as e:
            results["errors"].append(f"Health check error: {str(e)}")
            print(f"❌ Health check error: {e}")
        
        try:
            # Test status endpoint
            print(f"🔍 Testing status endpoint at {base_url}/api/status ...")
            async with session.get(f"{base_url}/api/status") as response:
                if response.status == 200:
                    results["status_endpoint"] = True
                    status_data = await response.json()
                    results["providers"] = status_data.get("ai_provider", "unknown")
                    print(f"✅ Status endpoint: {results['providers']}")
                else:
                    results["errors"].append(f"Status endpoint failed: {response.status}")
                    print(f"❌ Status endpoint failed: {response.status}")
        
        except Exception as e:
            results["errors"].append(f"Status endpoint error: {str(e)}")
            print(f"❌ Status endpoint error: {e}")
        
        try:
            # Test chat endpoint
            print(f"🔍 Testing chat endpoint at {base_url}/api/chat ...")
            chat_payload = {
                "message": "Hello! Quick deployment test - just say 'working' if you receive this."
            }
            
            async with session.post(
                f"{base_url}/api/chat",
                json=chat_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    results["chat_test"] = True
                    chat_data = await response.json()
                    print(f"✅ Chat test passed")
                    print(f"   Provider: {chat_data.get('provider', 'unknown')}")
                    print(f"   Response: {chat_data.get('response', 'no response')[:100]}...")
                else:
                    results["errors"].append(f"Chat test failed: {response.status}")
                    print(f"❌ Chat test failed: {response.status}")
        
        except Exception as e:
            results["errors"].append(f"Chat test error: {str(e)}")
            print(f"❌ Chat test error: {e}")
    
    return results

async def main():
    """Main verification function"""
    print("🧪 Spectra AI Deployment Verification")
    print("=" * 50)
    
    # Test local deployment
    local_url = "http://127.0.0.1:5000"
    print(f"\n📍 Testing LOCAL deployment: {local_url}")
    local_results = await test_deployment(local_url)
    
    # Test Railway deployment
    railway_url = "https://spectra-ai-library-version-production.up.railway.app"
    print(f"\n📍 Testing RAILWAY deployment: {railway_url}")
    railway_results = await test_deployment(railway_url)
    
    # Test Vercel deployment
    vercel_url = "https://spectraai-vercel.vercel.app"
    print(f"\n📍 Testing VERCEL deployment: {vercel_url}")
    vercel_results = await test_deployment(vercel_url)
    
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 50)
    
    print(f"\nLOCAL ({local_url}):")
    print(f"  Health: {'✅' if local_results['health_check'] else '❌'}")
    print(f"  Status: {'✅' if local_results['status_endpoint'] else '❌'}")
    print(f"  Chat: {'✅' if local_results['chat_test'] else '❌'}")
    
    print(f"\nRAILWAY ({railway_url}):")
    print(f"  Health: {'✅' if railway_results['health_check'] else '❌'}")
    print(f"  Status: {'✅' if railway_results['status_endpoint'] else '❌'}")
    print(f"  Chat: {'✅' if railway_results['chat_test'] else '❌'}")
    if railway_results['errors']:
        print(f"\n⚠️  Railway Errors:")
        for error in railway_results['errors']:
            print(f"    - {error}")
    
    print(f"\nVERCEL ({vercel_url}):")
    print(f"  Health: {'✅' if vercel_results['health_check'] else '❌'}")
    print(f"  Status: {'✅' if vercel_results['status_endpoint'] else '❌'}")
    print(f"  Chat: {'✅' if vercel_results['chat_test'] else '❌'}")
    if vercel_results['errors']:
        print(f"\n⚠️  Vercel Errors:")
        for error in vercel_results['errors']:
            print(f"    - {error}")
    
if __name__ == "__main__":
    asyncio.run(main())