from fastapi import WebSocket, HTTPException
from typing import Dict
import json
import uuid
from datetime import datetime
import asyncio
from src.app.data import VectorRepository
from src.core import Factory

class AgentService: 
    def __init__(self):
        self.active_agents: Dict[str, WebSocket] = {}
        self.agent_info: Dict[str, dict] = {}
        self.pending_responses: Dict[str, asyncio.Future] = {}
        self.factory = Factory()
        self.repository = VectorRepository()
    
    async def register_agent(self, agent_id: str, websocket: WebSocket, info: dict):
        self.active_agents[agent_id] = websocket

        if agent_id in self.agent_info:
            self.agent_info[agent_id].update({
                **info,
                'connected_at': datetime.now().isoformat(),
                'status': 'online'
            })
        else:
            self.agent_info[agent_id] = {
                **info,
                'connected_at': datetime.now().isoformat(),
                'status': 'online'
            }

    async def unregister_agent(self, agent_id: str):
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
        if agent_id in self.agent_info:
            self.agent_info[agent_id]['status'] = 'offline'

        for command_id in list(self.pending_responses.keys()):
            if command_id.startswith(agent_id):
                future = self.pending_responses.pop(command_id, None)
                if future and not future.done():
                    future.cancel()
    
    async def handle_message(self, agent_id: str, message: str):
        try:
            data = json.loads(message)
            command_id = data.get('command_id')
            
            if command_id and command_id in self.pending_responses:
                future = self.pending_responses.pop(command_id)
                if not future.done():
                    future.set_result(data)
        
            
        except json.JSONDecodeError:
            pass 
    
    async def send_command(self, agent_id: str, command: dict) -> dict:
        if agent_id not in self.active_agents:
            raise HTTPException(status_code=404, detail="Agent not found or offline")
        
        websocket = self.active_agents[agent_id]
        command_id = str(uuid.uuid4())
        command['command_id'] = command_id

        future = asyncio.Future()
        self.pending_responses[command_id] = future

        try:
            await websocket.send_text(json.dumps(command))
            
            response = await asyncio.wait_for(future, timeout=10)
            return response
            
        except asyncio.TimeoutError:
            self.pending_responses.pop(command_id, None)
            raise HTTPException(status_code=408, detail="Agent response timeout")
        except Exception as e:
            self.pending_responses.pop(command_id, None)
            raise HTTPException(status_code=500, detail=str(e))
        
    
    async def llm_injection_fault(self, user_query: str, agent_id: str):
        try:
            relevant_knowledge = self.repository.search_relevant_knowledge(user_query, top_k=5)
            
            if not relevant_knowledge:
                return {"error": "Nenhum conhecimento relevante encontrado"}
            
            knowledge_context = "\n\n".join([
            f"CONHECIMENTO {idx + 1} (Similaridade: {item['similarity']:.3f}):\n{json.dumps(item['data'], indent=2, ensure_ascii=False)}"
            for idx, item in enumerate(relevant_knowledge)
            ])
            
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
            
            client = self.factory.get_llm_model()
            
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