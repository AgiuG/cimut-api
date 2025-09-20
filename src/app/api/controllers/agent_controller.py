from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from src.app.api.schemas.requests import (
    InjectionFaultRequest, 
    VerifyLineRequest
)
from src.app.services import agent_service_instance
from src.app.data import VectorRepository
from src.core import Factory
import json

import re


router = APIRouter()
        
service = agent_service_instance

repository = VectorRepository()

factory = Factory()

# Base de conhecimento OpenStack para embeddings

# def initialize_embeddings():
#     """Inicializa os embeddings na inicialização da API"""
#     global KNOWLEDGE_EMBEDDINGS_CACHE
    
#     embeddings_file = 'openstack_knowledge_embeddings.json'
    
#     # Verifica se já existe arquivo salvo
#     if os.path.exists(embeddings_file):
#         print("Carregando embeddings existentes da base de conhecimento...")
#         with open(embeddings_file, 'r', encoding='utf-8') as f:
#             KNOWLEDGE_EMBEDDINGS_CACHE = json.load(f)
#         print(f"Embeddings carregados: {len(KNOWLEDGE_EMBEDDINGS_CACHE)} itens")
#         return
    
#     print("Criando embeddings da base de conhecimento OpenStack...")
#     knowledge_embeddings = []
    
#     for idx, item in enumerate(OPENSTACK_KNOWLEDGE_BASE):
#         try:
#             # Combina diferentes campos para criar texto para embedding
#             text_to_embed = ""
            
#             if 'file' in item:
#                 text_to_embed += f"File: {item['file']} "
#             if 'functions' in item:
#                 text_to_embed += f"Functions: {' '.join(item['functions'])} "
#             if 'description' in item:
#                 text_to_embed += f"Description: {item['description']} "
#             if 'fault_scenarios' in item:
#                 text_to_embed += f"Scenarios: {item['fault_scenarios']} "
            
#             # Gera embedding
#             print(f"Processando item {idx + 1}/{len(OPENSTACK_KNOWLEDGE_BASE)}")
#             embedding = get_embedding_codebert(text_to_embed)
            
#             if embedding is not None:
#                 knowledge_embeddings.append({
#                     'id': idx,
#                     'original_data': item,
#                     'text_embedded': text_to_embed[:200],
#                     'embedding': embedding
#                 })
            
#             # Rate limiting para API gratuita
#             time.sleep(2)
            
#         except Exception as e:
#             print(f"Erro processando item {idx}: {e}")
#             continue
    
#     # Salva embeddings para próximas inicializações
#     with open(embeddings_file, 'w', encoding='utf-8') as f:
#         json.dump(knowledge_embeddings, f, indent=2, ensure_ascii=False)
    
#     KNOWLEDGE_EMBEDDINGS_CACHE = knowledge_embeddings
#     print(f"Embeddings criados e cached: {len(knowledge_embeddings)} itens")

# def get_embedding_codebert(text: str, max_retries: int = 3):
#     """Gera embedding usando CodeBERT via HuggingFace API"""
#     url = "https://api-inference.huggingface.co/models/microsoft/codebert-base"
    
#     # Token opcional (se disponível)
#     hf_token = os.environ.get("HUGGINGFACE_TOKEN")
#     headers = {"Content-Type": "application/json"}
#     if hf_token:
#         headers["Authorization"] = f"Bearer {hf_token}"
    
#     payload = {
#         "inputs": text[:512],  # CodeBERT limite de 512 tokens
#         "options": {
#             "wait_for_model": True,
#             "use_cache": True
#         }
#     }
    
#     for attempt in range(max_retries):
#         try:
#             response = requests.post(url, headers=headers, json=payload, timeout=60)
            
#             if response.status_code == 200:
#                 embedding = response.json()
#                 if isinstance(embedding, list) and len(embedding) > 0:
#                     if isinstance(embedding[0], list):
#                         return np.mean(embedding, axis=0).tolist()
#                     return embedding
#                 return None
                
#             elif response.status_code == 503:
#                 print(f"Modelo carregando... tentativa {attempt + 1}")
#                 time.sleep(20)
#             elif response.status_code == 401:
#                 print(f"Erro 401 - API requer autenticação. Configure HUGGINGFACE_TOKEN")
#                 return None
#             else:
#                 print(f"Erro API: {response.status_code}")
#                 time.sleep(5)
                
#         except Exception as e:
#             print(f"Erro na tentativa {attempt + 1}: {e}")
#             time.sleep(10)
    
#     return None

# def cosine_similarity(a, b):
#     """Calcula similaridade entre dois vetores"""
#     return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# def search_relevant_knowledge(query: str, top_k: int = 5):
#     """Busca conhecimento relevante na base OpenStack usando cache"""
#     global KNOWLEDGE_EMBEDDINGS_CACHE
    
#     # Verifica se o cache está disponível
#     if KNOWLEDGE_EMBEDDINGS_CACHE is None or len(KNOWLEDGE_EMBEDDINGS_CACHE) == 0:
#         print("Cache de embeddings não disponível. Tentando inicializar...")
#         initialize_embeddings()
        
#         # Verifica novamente após tentar inicializar
#         if KNOWLEDGE_EMBEDDINGS_CACHE is None or len(KNOWLEDGE_EMBEDDINGS_CACHE) == 0:
#             print("Falha ao inicializar embeddings")
#             return []
    
#     # Gera embedding apenas da query
#     print("Gerando embedding da consulta...")
#     query_embedding = get_embedding_codebert(query)
    
#     if query_embedding is None:
#         print("Erro ao gerar embedding da query")
#         return []
    
#     # Calcula similaridades usando o cache
#     similarities = []
    
#     for item in KNOWLEDGE_EMBEDDINGS_CACHE:
#         if item.get('embedding'):
#             try:
#                 # Calcula similaridade cosseno
#                 sim = cosine_similarity(query_embedding, item['embedding'])
                
#                 similarities.append({
#                     'id': item['id'],
#                     'data': item['original_data'],
#                     'text_preview': item['text_embedded'],
#                     'similarity': float(sim)
#                 })
                
#             except Exception as e:
#                 print(f"Erro calculando similaridade: {e}")
#                 continue
    
#     # Ordena por similaridade
#     similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
#     print(f"Encontrados {len(similarities)} itens relevantes")
#     return similarities[:top_k]

@router.post("/agents/{agent_id}/find-fault-target")
async def find_fault_target(agent_id: str,request: dict):
    """Encontra arquivo alvo para injeção de falha baseado na pergunta do usuário"""
    try:
        user_query = request.get('query', '')
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Query é obrigatória")
        
        # Busca arquivos relevantes usando embeddings
        relevant_knowledge = repository.search_relevant_knowledge(user_query, top_k=5)
        
        if not relevant_knowledge:
            return {"error": "Nenhum conhecimento relevante encontrado"}
        
        knowledge_context = "\n\n".join([
            f"CONHECIMENTO {idx + 1} (Similaridade: {item['similarity']:.3f}):\n{json.dumps(item['data'], indent=2, ensure_ascii=False)}"
            for idx, item in enumerate(relevant_knowledge)
        ])
        
        # Monta prompt para o LLM analisar e escolher o melhor arquivo
        analysis_prompt = f"""
        Usuário quer: "{user_query}"
        
        CONHECIMENTO RELEVANTE ENCONTRADO:
        {knowledge_context}
        
        Com base neste conhecimento, identifique:
        1. O arquivo mais provável onde está o problema
        2. A função específica relacionada ao erro
        3. O tipo de mutação que pode causar este erro
        
        Retorne JSON:
        {{
            "target_file": "caminho/do/arquivo",
            "target_function": "nome_da_funcao",
            "reasoning": "explicação baseada no conhecimento encontrado",
            "knowledge_used": ["ids dos conhecimentos mais relevantes"]
        }}
        """
        client = factory.get_llm_model()
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em OpenStack. Analise e retorne APENAS o JSON solicitado."
                },
                {
                    "role": "user",
                    "content": analysis_prompt,
                }
            ],
            model="deepseek-r1-distill-llama-70b",
        )
        
        # Parse da resposta do LLM
        llm_response = chat_completion.choices[0].message.content
        
        try:
            # Tenta extrair JSON da resposta
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                target_info = json.loads(json_match.group())
            else:
                # Fallback: usa o arquivo com maior similaridade
                target_info = {
                    "target_file": relevant_knowledge[0]['data']['file'],
                    "target_function": relevant_knowledge[0]['data']['functions'][0],
                    "reasoning": f"Maior similaridade semântica ({relevant_knowledge[0]['similarity']:.3f})",
                    "knowledge_used": [relevant_knowledge[0]['id']]
                }
        except:
            # Fallback caso o JSON seja inválido
            target_info = {
                "target_file": relevant_knowledge[0]['data']['file'],
                "target_function": relevant_knowledge[0]['data']['functions'][0], 
                "reasoning": "Análise por similaridade semântica",
                "knowledge_used": [relevant_knowledge[0]['id']]
            }
        
        command = {
            'action': 'read_full_file',
            'file_path': target_info['target_file'],
            'functions': target_info['target_function']
        }
        
        response = await service.send_command(agent_id, command)

        mutation_prompt = f"""
        Você é um especialista em mutation testing para sistemas críticos. Analise o código Python e introduza uma mutação sutil que cause o erro especificado.

        ARQUIVO: {target_info['target_file']}

        CÓDIGO A MUTAR:
        ```python
        {response['data']['content']}
        ```

        CÒDIGO POR LINHA:
        {response['data']['lines']}

        ERRO ALVO: {user_query}

        REGRAS DE MUTAÇÃO:
        1. Faça UMA modificação por vez na linha mais crítica
        2. Mantenha o código sintaticamente válido
        3. Prefira mutações sutis: troque operadores, altere condições, modifique valores
        4. Evite mudanças óbvias que seriam facilmente detectadas
        5. Foque em lógica de negócio, validações ou fluxo de controle

        TIPOS DE MUTAÇÃO EFETIVOS:
        - Operadores: == → !=, < → <=, and → or
        - Condições: if condition → if not condition
        - Valores: True → False, números, strings
        - Chamadas: método() → método_errado()

        FORMATO DE RESPOSTA (JSON puro, sem markdown):
        {{
            "modifications": [
                {{
                    "line_number": 123,
                    "new_content": "código completo da linha modificada",
                    "reason": "tipo de mutação aplicada"
                }}
            ]
        }}"""
        
        chat_completion_teste = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Você é um especialista em OpenStack. Analise e retorne APENAS o JSON solicitado."
                },
                {
                    "role": "user",
                    "content": mutation_prompt,
                }
            ],
            model="deepseek-r1-distill-llama-70b",
        )
        
        # Parse da resposta do LLM
        llm_response_1 = chat_completion_teste.choices[0].message.content
        
        json_match = re.search(r'\{.*\}', llm_response_1, re.DOTALL)
        if json_match:
            mutation_info = json.loads(json_match.group())

        for mod in mutation_info['modifications']:
            command = {
                'action': 'modify_file',
                'file_path': target_info['target_file'],
                'line_number': mod['line_number'],
                'new_content': mod['new_content']
            }
     
            response = await service.send_command(agent_id, command)
        
        return {
            'target_file': target_info['target_file'],
            'target_function': target_info['target_function'],
            'mutation_suggestion': mutation_info,
            'mutation_info': response['data'],
            'llm_analysis': llm_response_1,
        }
             
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/agent/connect")
async def agent_websocket(websocket: WebSocket):
    await websocket.accept()
    agent_id = None

    try:
        registration = await websocket.receive_text()
        reg_data = json.loads(registration)

        agent_id = reg_data.get('agent_id')
        if not agent_id:
            await websocket.send_text(json.dumps({
                'error': 'agent_id required'
            }))
            return
        
        await service.register_agent(agent_id, websocket, reg_data)
        await websocket.send_text(json.dumps({
            'status': 'registered',
            'agent_id': agent_id
        }))

        while True:
            try:
                message = await websocket.receive_text()
                await service.handle_message(agent_id, message)
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    finally:
        if agent_id:
            await service.unregister_agent(agent_id)

@router.get("/agents")
async def list_agents():
    return {
        'agents': service.agent_info,
        'total': len(service.agent_info)
    }

@router.post("/agents/{agent_id}/fault")
async def agent_injection_fault(agent_id: str, request: InjectionFaultRequest): 
    command = {
        'action': 'modify_file',
        'file_path': request.file_path,
        'line_number': request.line_number,
        'new_content': request.new_content
    }

    try: 
        response = await service.send_command(agent_id, command)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/agents/{agent_id}/verify")
async def agent_verify_line(agent_id: str, request: VerifyLineRequest):
    command = {
        'action': 'read_file',
        'file_path': request.file_path,
        'line_number': request.line_number
    }

    try: 
        response = await service.send_command(agent_id, command)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))