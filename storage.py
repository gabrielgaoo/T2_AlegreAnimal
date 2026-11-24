import json
import os
import shutil
from datetime import datetime

# O arquivo fica na mesma pasta do código. Assim o sistema acha o mesmo
# dados.json mesmo que seja executado a partir de outra pasta do terminal.
PASTA = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = os.path.join(PASTA, "dados.json")


def dados_iniciais():
    # Função (e não uma variável global) para devolver sempre uma estrutura nova
    # e não compartilhar listas entre chamadas.
    return {
        "clientes": [],
        "animais": [],
        "servicos": [
            {"id": 1, "nome": "Banho", "preco": 40.0},
            {"id": 2, "nome": "Tosa", "preco": 55.0},
            {"id": 3, "nome": "Banho e tosa", "preco": 80.0},
            {"id": 4, "nome": "Consulta veterinária", "preco": 120.0},
        ],
        "agendamentos": [],
    }


def carregar():
    # Primeira execução: ainda não existe arquivo, então começa com os dados padrão
    if not os.path.exists(ARQUIVO):
        return dados_iniciais()

    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arq:
            dados = json.load(arq)
    except json.JSONDecodeError:
        # Arquivo corrompido (por exemplo, editado na mão com erro).
        # Guarda uma cópia para não perder o conteúdo e recomeça do zero.
        copia = ARQUIVO + "." + datetime.now().strftime("%Y%m%d_%H%M%S") + ".bak"
        shutil.copy(ARQUIVO, copia)
        print("Aviso: dados.json estava inválido. Uma cópia foi salva em:")
        print(copia)
        return dados_iniciais()

    # Garante que todas as listas existam, caso o arquivo seja de uma versão antiga
    padrao = dados_iniciais()
    for chave in padrao:
        if chave not in dados:
            dados[chave] = padrao[chave]
    return dados


def salvar(dados):
    # Grava primeiro em um arquivo temporário e só depois troca pelo definitivo.
    # Se o programa for interrompido no meio da gravação, o dados.json antigo continua inteiro.
    temporario = ARQUIVO + ".tmp"
    with open(temporario, "w", encoding="utf-8") as arq:
        json.dump(dados, arq, ensure_ascii=False, indent=4)
    os.replace(temporario, ARQUIVO)
