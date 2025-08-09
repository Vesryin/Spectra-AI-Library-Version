#!/usr/bin/env python3
"""Test script to verify AI providers are working"""

import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_openai():
    print("Testing OpenAI...")
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello! Just say 'OpenAI working' briefly."}],
            max_tokens=10
        )
        
        print(f"✅ OpenAI: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI Error: {e}")
        return False

async def test_anthropic():
    print("Testing Anthropic...")
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=10,
            messages=[{"role": "user", "content": "Hello! Just say 'Claude working' briefly."}]
        )
        
        print(f"✅ Anthropic: {response.content[0].text}")
        return True
    except Exception as e:
        print(f"❌ Anthropic Error: {e}")
        return False

async def main():
    print("🧪 Testing AI Providers for Spectra AI\n")
    
    openai_ok = await test_openai()
    anthropic_ok = await test_anthropic()
    
    print(f"\n📊 Results:")
    print(f"OpenAI: {'✅ Available' if openai_ok else '❌ Failed'}")
    print(f"Anthropic: {'✅ Available' if anthropic_ok else '❌ Failed'}")
    
    if openai_ok or anthropic_ok:
        print("\n🎉 At least one AI provider is working! Spectra AI is ready!")
    else:
        print("\n💥 No AI providers are working. Check API keys.")

if __name__ == "__main__":
    asyncio.run(main())
