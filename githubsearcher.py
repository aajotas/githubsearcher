import requests
from bs4 import BeautifulSoup
import re
import time
import logging

def construir_url_busca(localidade, linguagem, nome, pagina):
    base_url = "https://github.com/search"
    query = f"q=location%3A{localidade}+language%3A{linguagem}+fullname%3A{nome}&type=users&p={pagina}"
    return f"{base_url}?{query}"

def buscar_pagina(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        if 'X-RateLimit-Remaining' in response.headers:
            remaining = int(response.headers['X-RateLimit-Remaining'])
            if remaining == 0:
                reset_time = int(response.headers['X-RateLimit-Reset'])
                wait_time = reset_time - time.time() + 1
                logging.info(f"Limite de taxa excedido. Aguardando {wait_time} segundos.")
                time.sleep(wait_time)
        return response.text
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"Ocorreu um erro HTTP: {http_err}")
    except Exception as err:
        logging.error(f"Ocorreu um erro: {err}")
    return None

def extrair_total_paginas(html):
    try:
        data = BeautifulSoup(html, 'html.parser').get_text()
        page_count = re.findall(r'"page_count":(\d+)', data)
        return int(page_count[0]) if page_count else 1
    except Exception as e:
        logging.error(f"Erro ao extrair total de páginas: {e}")
        return 1

def extrair_logins_usuarios(html):
    try:
        data = BeautifulSoup(html, 'html.parser').get_text()
        logins = re.findall(r'"display_login":"(.*?)"', data)
        return logins
    except Exception as e:
        logging.error(f"Erro ao extrair logins de usuários: {e}")
        return []

def main(nome="", localidade="", linguagem="Python"):
    # Substituir espaços por "+"
    nome = nome.replace(" ", "+")
    localidade = localidade.replace(" ", "+")
    linguagem = "+".join([f"language%3A{lang}" for lang in linguagem.split(" ")])

    # URL de busca inicial
    url_inicial = construir_url_busca(localidade, linguagem, nome, 1)
    html_inicial = buscar_pagina(url_inicial)
    if not html_inicial:
        print("Falha ao buscar a página inicial.")
        return

    total_paginas = extrair_total_paginas(html_inicial)
    
    for pagina in range(1, total_paginas + 1):
        url_busca = construir_url_busca(localidade, linguagem, nome, pagina)
        html = buscar_pagina(url_busca)
        if not html:
            print(f"Pular a página {pagina} devido a erro na busca.")
            continue

        logins = extrair_logins_usuarios(html)
        for login in logins:
            print(f"https://github.com/{login}")

        print(f"Página {pagina}/{total_paginas} concluída: {url_busca}")
        time.sleep(1)  # Paciência para evitar limites de taxa

if __name__ == "__main__":
    # Parâmetros de exemplo para teste
    main(nome="John Doe", localidade="New York", linguagem="JavaScript")
