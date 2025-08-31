from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from src.app.api.schemas.requests import (
    InjectionFaultRequest, 
    VerifyLineRequest
)
from src.app.services import agent_service_instance
import json

import os
from groq import Groq

from sentence_transformers import SentenceTransformer
import numpy as np



client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

#embedding_model = SentenceTransformer('microsoft/codebert-base')
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

router = APIRouter()
        
service = agent_service_instance

# Base de conhecimento OpenStack para embeddings
OPENSTACK_KNOWLEDGE_BASE = [
    {
        "file": "/opt/stack/nova/nova/compute/manager.py",
        "functions": ["_build_and_run_instance", "_spawn", "_allocate_network", "_shutdown_instance", "_init_instance", "_build_resources", "_cleanup_volumes", "_cleanup_allocated_networks", "_prep_block_device"],
        "description": "Nova Compute Manager - Núcleo do gerenciamento de instâncias. Controla todo o ciclo de vida das VMs incluindo criação, destruição e operações de runtime.",
        "fault_scenarios": "falha na criação de instâncias, erro de spawn, timeout de rede, falha na alocação de recursos, erro de boot, problema de cleanup"
    },
    {
        "file": "/opt/stack/nova/nova/api/openstack/compute/servers.py",
        "functions": ["create", "delete", "update", "rebuild", "resize", "_action_reboot", "_action_rebuild", "_start", "_stop", "show"],
        "description": "Nova API Servers - Interface REST para operações de servidor. Valida requisições e direciona para os serviços apropriados.",
        "fault_scenarios": "validação falhou, quota excedida, request inválido, timeout de API, erro de autenticação, request malformado"
    },
    {
        "file": "/opt/stack/nova/nova/scheduler/manager.py",
        "functions": ["select_destinations", "_schedule", "_get_sorted_hosts", "_get_all_host_states", "_consume_selected_host"],
        "description": "Nova Scheduler Manager - Responsável pela seleção de hosts para instâncias. Aplica filtros e pesos para determinar o melhor host.",
        "fault_scenarios": "nenhum host válido, recursos insuficientes, falha de filtros, host indisponível, erro de alocação, falha de agendamento, erro de placement"
    },
    {
        "file": "/opt/stack/nova/nova/virt/libvirt/driver.py",
        "functions": ["spawn", "destroy", "reboot", "power_off", "power_on", "_create_domain", "_get_guest", "_hard_reboot", "_create_image", "_get_guest_xml"],
        "description": "LibVirt Driver - Interface com hypervisor LibVirt. Executa operações de baixo nível nas VMs.",
        "fault_scenarios": "falha do libvirt, VM não responde, erro de domínio, falha de attach de dispositivo, erro de configuração XML, problema com imagem"
    },
    {
        "file": "/opt/stack/nova/nova/network/neutron.py",
        "functions": ["allocate_for_instance", "deallocate_for_instance", "setup_instance_network_on_host", "bind_ports", "_create_port", "_delete_port"],
        "description": "Neutron Network API - Interface com serviço Neutron para operações de rede. Gerencia ports, security groups e floating IPs.",
        "fault_scenarios": "falha de alocação de IP, erro de binding de porta, timeout do Neutron, security group falhou, rede indisponível, porta não pode ser criada"
    },
    {
        "file": "/opt/stack/nova/nova/volume/cinder.py",
        "functions": ["attach_volume", "create_volume", "detach_volume", "initialize_connection", "terminate_connection"],
        "description": "Cinder Integration - Gerencia volumes de armazenamento para instâncias.",
        "fault_scenarios": "falha no volume, storage não disponível, erro de attachment, conexão não estabelecida, detach falhou"
    },
    {
        "file": "/opt/stack/nova/nova/conductor/manager.py",
        "functions": ["build_instances", "schedule_and_build_instances", "rebuild_instance", "migrate_server", "live_migrate_instance", "_cold_migrate", "_reschedule"],
        "description": "Nova Conductor Manager - Orquestra operações complexas entre compute e scheduler. Gerencia migrações e rebuild de instâncias.",
        "fault_scenarios": "falha de scheduling, erro de migração, rebuild falhou, reschedule loop, timeout de operação, perda de comunicação, falha de orquestração"
    },
    {
        "file": "/opt/stack/nova/nova/compute/api.py",
        "functions": ["create", "delete", "rebuild", "resize", "shelve", "unshelve", "_check_requested_networks", "_validate_flavor", "_provision_instances"],
        "description": "Compute API - Interface de alto nível para operações compute. Validação e orquestração de operações complexas.",
        "fault_scenarios": "validação de flavor falhou, rede inválida, imagem não encontrada, quota excedida, estado inválido, flavor incompatível"
    },
    {
        "file": "/opt/stack/nova/nova/compute/resource_tracker.py",
        "functions": ["instance_claim", "rebuild_claim", "resize_claim", "update_available_resource", "_update_usage_from_instances", "_verify_resources"],
        "description": "Resource Tracker - Rastreia recursos disponíveis no compute node. Gerencia claims de CPU, memória e disco.",
        "fault_scenarios": "recursos insuficientes, claim falhou, inconsistência de recursos, overflow de memória, disco cheio, CPU/RAM indisponível"
    },
    {
        "file": "/opt/stack/nova/nova/objects/instance.py",
        "functions": ["save", "create", "destroy", "refresh", "get_by_uuid", "_from_db_object", "_save_flavor", "_save_info_cache"],
        "description": "Instance Object - Modelo de dados ORM para instâncias. Gerencia persistência e estado no banco de dados.",
        "fault_scenarios": "erro de banco de dados, inconsistência de estado, lock timeout, objeto não encontrado, erro de serialização"
    },
    {
        "file": "/opt/stack/nova/nova/compute/rpcapi.py",
        "functions": ["build_and_run_instance", "terminate_instance", "rebuild_instance", "resize_instance", "live_migration", "prep_resize"],
        "description": "Compute RPC API - Interface RPC para comunicação com compute nodes. Envia comandos assíncronos via message queue.",
        "fault_scenarios": "timeout RPC, mensagem perdida, compute node offline, versão incompatível, falha de cast"
    },
    {
        "file": "/opt/stack/nova/nova/scheduler/filter_scheduler.py",
        "functions": ["schedule", "_get_sorted_hosts", "_schedule", "_get_all_host_states", "_get_hosts_by_request_spec"],
        "description": "Filter Scheduler - Implementação do algoritmo de scheduling com filtros e pesos. Seleciona hosts baseado em critérios configuráveis.",
        "fault_scenarios": "todos hosts filtrados, peso inválido, falha de agregado, anti-affinity violado, sem hosts disponíveis"
    },
    {
        "file": "/opt/stack/nova/nova/virt/libvirt/guest.py",
        "functions": ["launch", "shutdown", "pause", "resume", "create_snapshot", "attach_device", "detach_device", "get_xml_desc"],
        "description": "LibVirt Guest - Abstração de domínio LibVirt. Gerencia operações diretas na VM guest.",
        "fault_scenarios": "guest não responde, operação timeout, device attach falhou, snapshot falhou, estado inconsistente"
    }
]

def create_embeddings_database():
    """Cria base de embeddings dos componentes OpenStack"""
    embeddings_db = []
    
    for component in OPENSTACK_KNOWLEDGE_BASE:
        # Texto completo para embedding
        text_for_embedding = f"""
        File: {component['file']}
        Functions: {', '.join(component['functions'])}
        Description: {component['description']}
        Fault scenarios: {component['fault_scenarios']}
        """
        
        # Gera embedding
        embedding = embedding_model.encode(text_for_embedding.strip())
        
        embeddings_db.append({
            'file': component['file'],
            'functions': component['functions'],
            'description': component['description'],
            'embedding': embedding,
            'text': text_for_embedding.strip()
        })
        
    return embeddings_db

# Cria a base na inicialização
embeddings_database = create_embeddings_database()

def cosine_similarity(a, b):
    """Calcula similaridade entre dois vetores"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def search_relevant_files(query: str, top_k: int = 3):
    """Busca arquivos mais relevantes para a query"""
    # Gera embedding da query
    query_embedding = embedding_model.encode(query)
    
    # Calcula similaridades
    similarities = []
    
    for item in embeddings_database:
        similarity = cosine_similarity(query_embedding, item['embedding'])
        similarities.append({
            'file': item['file'],
            'functions': item['functions'],
            'description': item['description'],
            'similarity': float(similarity)
        })
    
    # Ordena por similaridade
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    return similarities[:top_k]

@router.post("/agents/{agent_id}/find-fault-target")
async def find_fault_target(agent_id: str,request: dict):
    """Encontra arquivo alvo para injeção de falha baseado na pergunta do usuário"""
    try:
        user_query = request.get('query', '')
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Query é obrigatória")
        
        # Busca arquivos relevantes usando embeddings
        relevant_files = search_relevant_files(user_query, top_k=5)
        
        # Monta prompt para o LLM analisar e escolher o melhor arquivo
        analysis_prompt = f"""
        Usuário quer: "{user_query}"
        
        Arquivos OpenStack encontrados por similaridade semântica:
        
        {json.dumps(relevant_files, indent=2)}
        
        Analise qual arquivo é MAIS ADEQUADO para causar a falha solicitada.
        
        Responda APENAS com este formato JSON:
        {{
            "target_file": "caminho/do/arquivo.py",
            "target_function": "nome_da_funcao",
            "reason": "explicação de por que este arquivo/função",
        }}
        """
        
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
            import re
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                target_info = json.loads(json_match.group())
            else:
                # Fallback: usa o arquivo com maior similaridade
                target_info = {
                    "target_file": relevant_files[0]['file'],
                    "target_function": relevant_files[0]['functions'][0],
                    "reason": f"Maior similaridade semântica ({relevant_files[0]['similarity']:.3f})",
                    "fault_type": "exception",
                    "confidence": relevant_files[0]['similarity']
                }
        except:
            # Fallback caso o JSON seja inválido
            target_info = {
                "target_file": relevant_files[0]['file'],
                "target_function": relevant_files[0]['functions'][0], 
                "reason": "Análise por similaridade semântica",
                "fault_type": "exception",
                "confidence": relevant_files[0]['similarity']
            }
        
        command = {
            'action': 'read_full_file',
            'file_path': target_info['target_file'],
        }
        
        response = await service.send_command(agent_id, command)

        mutation_prompt = f"""
        Você é um especialista em mutation testing para sistemas críticos. Analise o código Python e introduza uma mutação sutil que cause o erro especificado.

        ARQUIVO: {target_info['target_file']}

        CÓDIGO A MUTAR:
        ```python
        {response['data']['content']}
        ```

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
        llm_response = chat_completion_teste.choices[0].message.content

        return llm_response
        
   
        
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

@router.post("/agents/mutation")
async def agent_mutation(request: dict):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": request['message'],
            }
        ],
        model="deepseek-r1-distill-llama-70b",
    )

    return chat_completion.choices[0].message.content