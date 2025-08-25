FROM python:3.12.8-slim

WORKDIR /app

# Atualizar pacotes e instalar dependências do sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq5 && \
    rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY ./main.py . 
COPY ./src /app/src

# Expor a porta
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]