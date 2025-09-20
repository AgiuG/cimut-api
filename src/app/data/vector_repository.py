import numpy as np
import requests
from src.core import Factory
import time
import json
import os

class VectorRepository:
    def __init__(self):
        self.factory = Factory()
        self.cache = []
        self.OPENSTACK_KNOWLEDGE_BASE = [
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

    def generate_embedding(self, text: str, max_retries: int = 3):
        payload = {
            "inputs": text[:512],
            "options": {
                "wait_for_model": True,
                "use_cache": True
            }
        }
        
        for attempt in range(max_retries):
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.factory.get_embedding_model()['token']}"
                }
                
                response = requests.post(
                    self.factory.get_embedding_model()["url"],
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    embedding = response.json()
                    if isinstance(embedding, list) and len(embedding) > 0:
                        if isinstance(embedding[0], list):
                            return np.mean(embedding, axis=0).tolist()
                        return embedding
                
                elif response.status_code == 503:
                    print(f"Modelo carregando... tentativa {attempt + 1}")
                    time.sleep(20)
                
                elif response.status_code == 401:
                    print(f"Erro 401 - API requer autenticação. Configure HUGGINGFACE_TOKEN")
                    return None
                
                else:
                    print(f"Erro API: {response.status_code}")
                    time.sleep(5)
                    
            except Exception as e:
                print(f"Erro na tentativa {attempt + 1}: {e}")
                time.sleep(10)
    
    def cosine_similarity(self, a, b) -> float:
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def search_relevant_knowledge(self, query: str, top_k: int = 5):
        if self.cache is None or len(self.cache) == 0:
            print("Cache de em'beddings não disponível. Tentando inicializar...")
            self.initialize_embeddings()
        
            if self.cache is None or len(self.cache) == 0:
                print("Falha ao inicializar cache de embeddings.")
                return []

        query_embedding = self.generate_embedding(query)
        
        if query_embedding is None:
            print("Falha ao gerar embedding para a consulta.")
            return []
        
        similarities = []
        
        for item in self.cache:
            if item.get("embedding"):
                try:
                    sim = self.cosine_similarity(query_embedding, item['embedding'])
                    
                    similarities.append({
                        'id': item['id'],
                        'data': item['original_data'],
                        'text_preview': item['text_embedded'],
                        'similarity': float(sim)
                    })
                
                except Exception as e:
                    print(f"Erro ao calcular similaridade para item {item['id']}: {e}")
                    continue
        
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]
    
    def initialize_embeddings(self):
        
        embeddings_file = 'openstack_knowledge_embeddings.json'

        if os.path.exists(embeddings_file):
            with open(embeddings_file, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
                print(f"Cache de embeddings carregado com {len(self.cache)} itens.")
                return
        
        knowledge_embeddings = []
        
        for idx, item in enumerate(self.OPENSTACK_KNOWLEDGE_BASE):
            try:
                text_to_embed = ""
                
                if 'file' in item:
                    text_to_embed += f"File: {item['file']} "
                if 'functions' in item:
                    text_to_embed += f"Functions: {' '.join(item['functions'])} "
                if 'description' in item:
                    text_to_embed += f"Description: {item['description']} "
                if 'fault_scenarios' in item:
                    text_to_embed += f"Scenarios: {item['fault_scenarios']} "

                embedding = self.generate_embedding(text_to_embed)

                if embedding is not None:
                    knowledge_embeddings.append({
                        'id': idx,
                        'original_data': item,
                        'text_embedded': text_to_embed[:200],
                        'embedding': embedding
                    })

                time.sleep(2)
                
            except Exception as e:
                print(f"Erro processando item {idx}: {e}")
                raise e
        
        with open(embeddings_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_embeddings, f, indent=2, ensure_ascii=False)

        self.cache = knowledge_embeddings
        print(f"Cache de embeddings inicializado com {len(self.cache)} itens.")