import requests
import time
import re
import wikipedia
from googlesearch import search
from bs4 import BeautifulSoup

# Configurações do seu Firebase
BASE_URL = "https://aleatoria-4cd46-default-rtdb.firebaseio.com/"

def pesquisar_e_aprender(query):
    """A AntroAi busca em várias fontes e gera a própria síntese"""
    try:
        # Busca no Google (Pega Wikis, Fandoms, Raws)
        links = list(search(query, num_results=2))
        if not links: return "AntroAi: Sem dados na base global."

        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(links[0], headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Pega os parágrafos e limpa o texto
        texto = " ".join([p.get_text() for p in soup.find_all('p')[:2]])
        # Aqui a AntroAi "processa" (resumo simples para o exemplo)
        return f"🔍 [Analise AntroAi]: {texto[:400]}..."
    except:
        return "AntroAi: Erro ao processar fontes externas."

def processar_ia():
    print("🚀 AntroAi Core ONLINE e Vigiando...")
    
    while True:
        try:
            res = requests.get(f"{BASE_URL}queue.json")
            queue = res.json()

            if queue:
                for item_id, data in queue.items():
                    if data.get("status") == "pending":
                        msg_original = data['message'].lower().strip()
                        
                        # 1. Limpeza de saudações (Anti-Telemar)
                        msg = re.sub(r"^(oi|ola|olá|salve|ei)\s*", "", msg_original)

                        # 2. Lógica de Resposta
                        if not msg: # Se era só um "Oi"
                            resposta = "AntroAi online. Aguardando comandos ou links."
                        elif "quem é" in msg or "o que" in msg or "script" in msg:
                            resposta = pesquisar_e_aprender(msg)
                        else:
                            # Tenta aprender sobre qualquer coisa que você mandar
                            resposta = pesquisar_e_aprender(msg)

                        # 3. Posta no Chat Global e limpa a fila
                        requests.post(f"{BASE_URL}global_chat.json", json={
                            "user": "AntroAi",
                            "text": resposta,
                            "timestamp": {".sv": "timestamp"}
                        })
                        requests.delete(f"{BASE_URL}queue/{item_id}.json")
                        print(f"✅ Respondido: {msg[:20]}...")

        except Exception as e:
            print(f"Erro: {e}")
        
        time.sleep(2) # Delay para não ser banido pelo Firebase

if __name__ == "__main__":
    processar_ia()
