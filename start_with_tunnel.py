#!/usr/bin/env python3
"""
Script para iniciar a API e criar tunnel automaticamente
"""

import subprocess
import time
import threading
import requests
import os
from pathlib import Path

def start_api():
    """Inicia a API FastAPI"""
    print("🚀 Iniciando API...")
    subprocess.run(["python", "main.py"], cwd=Path(__file__).parent)

def start_ngrok():
    """Inicia o ngrok"""
    print("🌐 Iniciando ngrok...")
    try:
        # Espera a API iniciar
        time.sleep(3)
        
        # Testa se a API está rodando
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:8000", timeout=2)
                print("✅ API está rodando!")
                break
            except:
                if i < max_retries - 1:
                    print(f"⏳ Aguardando API iniciar... ({i+1}/{max_retries})")
                    time.sleep(2)
                else:
                    print("❌ API não iniciou. Verifique se não há erros.")
                    return
        
        # Inicia ngrok
        print("🔗 Criando tunnel público...")
        subprocess.run(["ngrok", "http", "8000"])
        
    except KeyboardInterrupt:
        print("\n🛑 Parando ngrok...")
    except FileNotFoundError:
        print("❌ ngrok não encontrado. Instale primeiro:")
        print("   - Windows: choco install ngrok")
        print("   - Ou baixe de: https://ngrok.com/download")

def main():
    """Função principal"""
    print("🎯 CIMut API + ngrok")
    print("=" * 40)
    
    # Verifica se o ngrok está instalado
    try:
        subprocess.run(["ngrok", "version"], capture_output=True, check=True)
        print("✅ ngrok encontrado")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ngrok não encontrado. Instalando...")
        print("Por favor, instale o ngrok primeiro:")
        print("   - Windows: choco install ngrok")
        print("   - Ou baixe de: https://ngrok.com/download")
        return
    
    # Inicia API em thread separada
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Inicia ngrok (bloqueia até Ctrl+C)
    try:
        start_ngrok()
    except KeyboardInterrupt:
        print("\n🛑 Parando serviços...")

if __name__ == "__main__":
    main()
