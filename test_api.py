#!/usr/bin/env python3
"""
Script para testar a API CIMut localmente ou via tunnel
"""

import requests
import json
import sys

def test_api(base_url="http://localhost:8000"):
    """Testa os endpoints principais da API"""
    
    print(f"🧪 Testando API em: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check (se existir)
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint falhou: {e}")
    
    # Test 2: Find fault target
    try:
        test_payload = {
            "query": "quero causar falha na criação de instâncias"
        }
        
        response = requests.post(
            f"{base_url}/api/agents/test-agent/find-fault-target",
            json=test_payload,
            timeout=30
        )
        
        print(f"✅ Find fault target: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Find fault target falhou: {e}")
    
    # Test 3: Mutation endpoint
    try:
        test_payload = {
            "message": "Como causar timeout na API do Nova?"
        }
        
        response = requests.post(
            f"{base_url}/api/agents/mutation",
            json=test_payload,
            timeout=30
        )
        
        print(f"✅ Mutation endpoint: {response.status_code}")
        
        if response.status_code == 200:
            result = response.text
            print(f"🤖 Resposta LLM: {result[:200]}...")
        else:
            print(f"❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"❌ Mutation endpoint falhou: {e}")

    print("=" * 50)
    print("🏁 Teste concluído!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
        test_api(base_url)
    else:
        print("Uso:")
        print(f"  python {sys.argv[0]} http://localhost:8000")
        print(f"  python {sys.argv[0]} https://sua-url-do-ngrok.com")
        print()
        print("Testando localhost por padrão...")
        test_api()
