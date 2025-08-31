#!/usr/bin/env python3
"""
Script para verificar se todos os requisitos estão instalados
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python_packages():
    """Verifica se os pacotes Python estão instalados"""
    print("📦 Verificando pacotes Python...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic', 
        'groq',
        'sentence_transformers',
        'numpy',
        'torch'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Pacotes faltando: {', '.join(missing_packages)}")
        print("💡 Execute: pip install -r requirements.txt")
        return False
    
    return True

def check_external_tools():
    """Verifica ferramentas externas"""
    print("\n🛠️  Verificando ferramentas externas...")
    
    tools = {
        'ngrok': 'choco install ngrok (ou baixe de https://ngrok.com)',
        'curl': 'Geralmente pré-instalado no Windows 10+',
        'git': 'Instale do https://git-scm.com'
    }
    
    available_tools = []
    
    for tool, install_hint in tools.items():
        try:
            subprocess.run([tool, '--version'], 
                         capture_output=True, 
                         check=True)
            print(f"  ✅ {tool}")
            available_tools.append(tool)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"  ❌ {tool} - {install_hint}")
    
    return available_tools

def check_environment_variables():
    """Verifica variáveis de ambiente necessárias"""
    print("\n🔐 Verificando variáveis de ambiente...")
    
    env_vars = {
        'GROQ_API_KEY': 'Necessária para usar o LLM (obtenha em https://console.groq.com)'
    }
    
    missing_vars = []
    
    for var, description in env_vars.items():
        if os.environ.get(var):
            print(f"  ✅ {var} (configurada)")
        else:
            print(f"  ❌ {var} - {description}")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def check_api_port():
    """Verifica se a porta 8000 está disponível"""
    print("\n🔌 Verificando porta 8000...")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print("  ⚠️  Porta 8000 está ocupada")
            return False
        else:
            print("  ✅ Porta 8000 disponível")
            return True
    except Exception as e:
        print(f"  ❓ Erro ao verificar porta: {e}")
        return True

def main():
    """Função principal"""
    print("🔍 Verificador de Requisitos - CIMut API")
    print("=" * 50)
    
    checks = [
        ("Pacotes Python", check_python_packages()),
        ("Ferramentas externas", len(check_external_tools()) > 0),
        ("Variáveis de ambiente", check_environment_variables()),
        ("Porta disponível", check_api_port())
    ]
    
    print("\n" + "=" * 50)
    print("📊 RESUMO:")
    
    all_good = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"  {status} {check_name}")
        if not result:
            all_good = False
    
    print("=" * 50)
    
    if all_good:
        print("🎉 Tudo pronto! Você pode iniciar a API:")
        print("   python main.py")
        print("\nOu usar o script automático:")
        print("   python start_with_tunnel.py")
    else:
        print("⚠️  Alguns requisitos não estão atendidos.")
        print("💡 Consulte o arquivo TESTING.md para mais detalhes.")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
