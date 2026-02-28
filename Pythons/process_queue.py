import os
import requests
import wikipedia
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

# Puxa a URL do Key Secrets que você configurou
BASE_URL = os.environ.get("FB_URL")

def iniciar_ia():
    # Dataset para treinar o cérebro da AntropAi
    dados = [
        ("o que é", "wiki"), ("quem foi", "wiki"), ("pesquise sobre", "wiki"),
        ("me fale sobre", "wiki"), ("historia de", "wiki"),
        ("script lua", "script"), ("gerar exploit", "script"), ("fazer script", "script"),
        ("pornografia", "block"), ("sexo", "block"), ("masturbar", "block"), ("putaria", "block")
    ]
    x_treino, y_treino = zip(*dados)
    vectorizer = TfidfVectorizer()
    clf = LinearSVC()
    clf.fit(vectorizer.fit_transform(x_treino), y_treino)
    return vectorizer, clf

def processar():
    if not BASE_URL:
        print("ERRO: FIREBASE_URL não encontrada nos Secrets!")
        return

    # 1. Baixa a fila do Firebase
    try:
        res = requests.get(f"{BASE_URL}queue.json")
        queue = res.json()
    except:
        return

    if not queue:
        print("Fila vazia.")
        return

    vectorizer, clf = iniciar_ia()
    wikipedia.set_lang("pt")

    for item_id, data in queue.items():
        if data.get("status") == "pending":
            msg = data['message'].lower()
            print(f"Processando: {msg}")

            # Predição do ML
            intencao = clf.predict(vectorizer.transform([msg]))[0]

            if intencao == "block":
                resposta = "⛔ Conteúdo bloqueado: Violação das diretrizes da AntropAi."
            elif intencao == "wiki":
                try:
                    busca = re.sub(r"^(o que é|quem foi|pesquise sobre)\s+", "", msg)
                    resposta = wikipedia.summary(busca, sentences=2)
                except:
                    resposta = "Não encontrei informações sobre isso."
            elif intencao == "script":
                resposta = "-- AntropAi Engine\nprint('Script gerado com sucesso para seu exploit.')"
            else:
                resposta = "AntropAi ativa. Como posso ajudar?"

            # 2. Atualiza o Firebase com a resposta
            requests.patch(f"{BASE_URL}queue/{item_id}.json", json={
                "response": resposta,
                "status": "completed"
            })

if __name__ == "__main__":
    processar()
