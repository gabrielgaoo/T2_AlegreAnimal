from datetime import datetime

from storage import carregar, salvar

# Todos os dados do sistema ficam neste dicionário enquanto o programa roda.
# Ele é lido do dados.json ao iniciar e regravado a cada alteração.
DADOS = carregar()

# Horários de atendimento da AlegreAnimal (um atendimento por horário)
HORARIOS = ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00", "15:00", "16:00", "17:00"]


# ---------------------------------------------------------------------------
# Funções auxiliares (entrada de dados e buscas)
# ---------------------------------------------------------------------------

def pausar():
    input("\nPressione ENTER para continuar...")


def proximo_id(lista):
    # Usa o maior id existente + 1. Contar o tamanho da lista não serve,
    # porque depois de uma exclusão o id poderia se repetir.
    return max([item["id"] for item in lista], default=0) + 1


def buscar_por_id(lista, id_procurado):
    for item in lista:
        if item["id"] == id_procurado:
            return item
    return None


def ler_inteiro(mensagem):
    # Repete até o usuário digitar um número; devolve None se deixar vazio (cancela)
    while True:
        texto = input(mensagem).strip()
        if texto == "":
            return None
        try:
            return int(texto)
        except ValueError:
            print("Digite apenas números (ou ENTER para cancelar).")


def ler_data(mensagem):
    # Converte o texto para data só para validar; o que é salvo continua sendo texto dd/mm/aaaa
    while True:
        texto = input(mensagem).strip()
        if texto == "":
            return None
        try:
            data = datetime.strptime(texto, "%d/%m/%Y")
        except ValueError:
            print("Data inválida. Use o formato dd/mm/aaaa, por exemplo 25/12/2026.")
            continue
        if data.date() < datetime.now().date():
            print("Não é possível agendar em uma data que já passou.")
            continue
        return data.strftime("%d/%m/%Y")


def confirmar(pergunta):
    resposta = input(pergunta + " (s/n): ").strip().lower()
    return resposta == "s"


# ---------------------------------------------------------------------------
# Clientes
# ---------------------------------------------------------------------------

def cadastrar_cliente():
    print("\n--- CADASTRO DE CLIENTE ---")
    nome = input("Nome: ").strip()
    telefone = input("Telefone: ").strip()
    email = input("E-mail: ").strip()

    if nome == "":
        print("Cliente não cadastrado: o nome é obrigatório.")
        return
    if telefone == "":
        print("Cliente não cadastrado: o telefone é obrigatório.")
        return

    # Evita cadastrar duas vezes a mesma pessoa (compara sem diferenciar maiúsculas)
    for c in DADOS["clientes"]:
        if c["nome"].lower() == nome.lower() and c["telefone"] == telefone:
            print("Cliente não cadastrado: já existe um cliente com esse nome e telefone.")
            return

    cliente = {
        "id": proximo_id(DADOS["clientes"]),
        "nome": nome,
        "telefone": telefone,
        "email": email,
    }
    DADOS["clientes"].append(cliente)
    salvar(DADOS)
    print(f"Cliente cadastrado com sucesso! (código {cliente['id']})")


def mostrar_cliente(c):
    email = c["email"] if c["email"] else "-"
    print(f'  [{c["id"]}] {c["nome"]} | Tel: {c["telefone"]} | E-mail: {email}')


def listar_clientes():
    print("\n--- CLIENTES ---")
    if not DADOS["clientes"]:
        print("Nenhum cliente cadastrado.")
        return False
    for c in DADOS["clientes"]:
        mostrar_cliente(c)
    return True


def pesquisar_clientes():
    # Funcionalidade extra: busca por parte do nome
    print("\n--- PESQUISAR CLIENTE ---")
    termo = input("Parte do nome: ").strip().lower()
    if termo == "":
        return

    encontrados = [c for c in DADOS["clientes"] if termo in c["nome"].lower()]
    if not encontrados:
        print("Nenhum cliente encontrado.")
        return

    print(f"{len(encontrados)} cliente(s) encontrado(s):")
    for c in encontrados:
        mostrar_cliente(c)
        # Mostra também os animais do cliente encontrado
        for a in DADOS["animais"]:
            if a["cliente_id"] == c["id"]:
                print(f'      - {a["nome"]} ({a["especie"]})')


def excluir_cliente():
    if not listar_clientes():
        return
    cliente_id = ler_inteiro("\nCódigo do cliente a excluir (ENTER cancela): ")
    if cliente_id is None:
        return

    cliente = buscar_por_id(DADOS["clientes"], cliente_id)
    if cliente is None:
        print("Cliente não encontrado.")
        return

    # Se o cliente ainda tem agendamento marcado, a exclusão deixaria o
    # agendamento sem dono. Por isso é preciso cancelar antes.
    for ag in DADOS["agendamentos"]:
        if ag["cliente_id"] == cliente_id:
            print("Este cliente possui agendamentos. Cancele os agendamentos antes de excluí-lo.")
            return

    animais_do_cliente = [a for a in DADOS["animais"] if a["cliente_id"] == cliente_id]
    aviso = f"Excluir {cliente['nome']}"
    if animais_do_cliente:
        aviso += f" e seus {len(animais_do_cliente)} animal(is)"
    if not confirmar(aviso + "?"):
        print("Exclusão cancelada.")
        return

    # Os animais pertencem ao cliente, então saem junto com ele
    DADOS["animais"] = [a for a in DADOS["animais"] if a["cliente_id"] != cliente_id]
    DADOS["clientes"].remove(cliente)
    salvar(DADOS)
    print("Cliente excluído com sucesso.")


# ---------------------------------------------------------------------------
# Animais
# ---------------------------------------------------------------------------

def cadastrar_animal():
    print("\n--- CADASTRO DE ANIMAL ---")
    if not listar_clientes():
        print("Cadastre um cliente antes de cadastrar um animal.")
        return

    cliente_id = ler_inteiro("\nCódigo do dono (ENTER cancela): ")
    if cliente_id is None:
        return
    if buscar_por_id(DADOS["clientes"], cliente_id) is None:
        print("Cliente não encontrado.")
        return

    nome = input("Nome do animal: ").strip()
    especie = input("Espécie (cão, gato...): ").strip()
    if nome == "" or especie == "":
        print("Animal não cadastrado: nome e espécie são obrigatórios.")
        return

    animal = {
        "id": proximo_id(DADOS["animais"]),
        "cliente_id": cliente_id,
        "nome": nome,
        "especie": especie,
    }
    DADOS["animais"].append(animal)
    salvar(DADOS)
    print(f"Animal cadastrado com sucesso! (código {animal['id']})")


def listar_animais():
    print("\n--- ANIMAIS ---")
    if not DADOS["animais"]:
        print("Nenhum animal cadastrado.")
        return False
    for a in DADOS["animais"]:
        dono = buscar_por_id(DADOS["clientes"], a["cliente_id"])
        nome_dono = dono["nome"] if dono else "?"
        print(f'  [{a["id"]}] {a["nome"]} ({a["especie"]}) - dono: {nome_dono}')
    return True


def excluir_animal():
    if not listar_animais():
        return
    animal_id = ler_inteiro("\nCódigo do animal a excluir (ENTER cancela): ")
    if animal_id is None:
        return

    animal = buscar_por_id(DADOS["animais"], animal_id)
    if animal is None:
        print("Animal não encontrado.")
        return

    for ag in DADOS["agendamentos"]:
        if ag["animal_id"] == animal_id:
            print("Este animal possui agendamentos. Cancele os agendamentos antes de excluí-lo.")
            return

    DADOS["animais"].remove(animal)
    salvar(DADOS)
    print("Animal excluído com sucesso.")


# ---------------------------------------------------------------------------
# Serviços
# ---------------------------------------------------------------------------

def cadastrar_servico():
    print("\n--- CADASTRO DE SERVIÇO ---")
    nome = input("Nome do serviço: ").strip()
    if nome == "":
        print("Serviço não cadastrado: o nome é obrigatório.")
        return

    for s in DADOS["servicos"]:
        if s["nome"].lower() == nome.lower():
            print("Serviço não cadastrado: já existe um serviço com esse nome.")
            return

    # O usuário pode digitar 40,50 ou 40.50, então troca a vírgula pelo ponto antes de converter
    texto_preco = input("Preço (R$): ").strip().replace(",", ".")
    try:
        preco = float(texto_preco)
    except ValueError:
        print("Serviço não cadastrado: preço inválido.")
        return
    if preco <= 0:
        print("Serviço não cadastrado: o preço deve ser maior que zero.")
        return

    servico = {"id": proximo_id(DADOS["servicos"]), "nome": nome, "preco": preco}
    DADOS["servicos"].append(servico)
    salvar(DADOS)
    print(f"Serviço cadastrado com sucesso! (código {servico['id']})")


def listar_servicos():
    print("\n--- SERVIÇOS ---")
    if not DADOS["servicos"]:
        print("Nenhum serviço cadastrado.")
        return False
    for s in DADOS["servicos"]:
        print(f'  [{s["id"]}] {s["nome"]} | R$ {s["preco"]:.2f}')
    return True


def excluir_servico():
    if not listar_servicos():
        return
    servico_id = ler_inteiro("\nCódigo do serviço a excluir (ENTER cancela): ")
    if servico_id is None:
        return

    servico = buscar_por_id(DADOS["servicos"], servico_id)
    if servico is None:
        print("Serviço não encontrado.")
        return

    for ag in DADOS["agendamentos"]:
        if ag["servico_id"] == servico_id:
            print("Este serviço está em agendamentos existentes. Cancele-os antes de excluir o serviço.")
            return

    DADOS["servicos"].remove(servico)
    salvar(DADOS)
    print("Serviço excluído com sucesso.")


# ---------------------------------------------------------------------------
# Agendamentos
# ---------------------------------------------------------------------------

def horarios_livres(data):
    # Horário ocupado = já existe agendamento naquela data com aquele horário
    ocupados = [ag["horario"] for ag in DADOS["agendamentos"] if ag["data"] == data]
    return [h for h in HORARIOS if h not in ocupados]


def realizar_agendamento():
    print("\n--- NOVO AGENDAMENTO ---")
    if not DADOS["clientes"]:
        print("Cadastre um cliente primeiro.")
        return
    if not DADOS["servicos"]:
        print("Cadastre um serviço primeiro.")
        return

    # 1) cliente
    listar_clientes()
    cliente_id = ler_inteiro("\nCódigo do cliente (ENTER cancela): ")
    if cliente_id is None:
        return
    cliente = buscar_por_id(DADOS["clientes"], cliente_id)
    if cliente is None:
        print("Cliente não encontrado.")
        return

    # 2) animal (só os animais desse cliente)
    animais = [a for a in DADOS["animais"] if a["cliente_id"] == cliente_id]
    if not animais:
        print(f"{cliente['nome']} ainda não tem animal cadastrado. Use a opção de cadastro de animais.")
        return
    print("\nAnimais do cliente:")
    for a in animais:
        print(f'  [{a["id"]}] {a["nome"]} ({a["especie"]})')
    animal_id = ler_inteiro("\nCódigo do animal (ENTER cancela): ")
    if animal_id is None:
        return
    animal = buscar_por_id(animais, animal_id)
    if animal is None:
        print("Animal não encontrado para este cliente.")
        return

    # 3) serviço
    listar_servicos()
    servico_id = ler_inteiro("\nCódigo do serviço (ENTER cancela): ")
    if servico_id is None:
        return
    servico = buscar_por_id(DADOS["servicos"], servico_id)
    if servico is None:
        print("Serviço não encontrado.")
        return

    # 4) data e horário, mostrando só o que ainda está livre
    data = ler_data("\nData (dd/mm/aaaa, ENTER cancela): ")
    if data is None:
        return
    livres = horarios_livres(data)
    if not livres:
        print("Não há horários livres nessa data.")
        return
    print("Horários livres:", ", ".join(livres))

    while True:
        horario = input("Horário (hh:mm, ENTER cancela): ").strip()
        if horario == "":
            return
        # Aceita "9:00" e converte para "09:00" para bater com a lista de horários
        if len(horario) == 4 and horario[1] == ":":
            horario = "0" + horario
        if horario in livres:
            break
        print("Horário indisponível. Escolha um da lista de horários livres.")

    agendamento = {
        "id": proximo_id(DADOS["agendamentos"]),
        "cliente_id": cliente_id,
        "animal_id": animal_id,
        "servico_id": servico_id,
        "data": data,
        "horario": horario,
    }
    DADOS["agendamentos"].append(agendamento)
    salvar(DADOS)
    print(f"\nAgendamento confirmado! (código {agendamento['id']})")
    print(f"{animal['nome']} - {servico['nome']} em {data} às {horario}, R$ {servico['preco']:.2f}")


def mostrar_agendamento(ag):
    cliente = buscar_por_id(DADOS["clientes"], ag["cliente_id"])
    animal = buscar_por_id(DADOS["animais"], ag["animal_id"])
    servico = buscar_por_id(DADOS["servicos"], ag["servico_id"])
    nome_cliente = cliente["nome"] if cliente else "(removido)"
    nome_animal = animal["nome"] if animal else "(removido)"
    nome_servico = servico["nome"] if servico else "(removido)"
    print(f'  [{ag["id"]}] {ag["data"]} {ag["horario"]} | {nome_animal} ({nome_cliente}) | {nome_servico}')


def consultar_agendamentos():
    print("\n--- AGENDAMENTOS ---")
    if not DADOS["agendamentos"]:
        print("Nenhum agendamento cadastrado.")
        return False

    # Ordena pela data real; ordenar o texto "dd/mm/aaaa" colocaria 02/01 antes de 15/12
    ordenados = sorted(
        DADOS["agendamentos"],
        key=lambda ag: (datetime.strptime(ag["data"], "%d/%m/%Y"), ag["horario"]),
    )
    for ag in ordenados:
        mostrar_agendamento(ag)
    return True


def filtrar_agendamentos_por_data():
    # Funcionalidade extra: lista só os agendamentos de um dia e o total previsto
    print("\n--- AGENDAMENTOS POR DATA ---")
    texto = input("Data (dd/mm/aaaa): ").strip()
    try:
        data = datetime.strptime(texto, "%d/%m/%Y").strftime("%d/%m/%Y")
    except ValueError:
        print("Data inválida.")
        return

    do_dia = [ag for ag in DADOS["agendamentos"] if ag["data"] == data]
    if not do_dia:
        print("Nenhum agendamento nessa data.")
        return

    total = 0.0
    for ag in sorted(do_dia, key=lambda x: x["horario"]):
        mostrar_agendamento(ag)
        servico = buscar_por_id(DADOS["servicos"], ag["servico_id"])
        if servico:
            total += servico["preco"]
    print(f"Total de atendimentos: {len(do_dia)} | Faturamento previsto: R$ {total:.2f}")


def cancelar_agendamento():
    if not consultar_agendamentos():
        return
    ag_id = ler_inteiro("\nCódigo do agendamento a cancelar (ENTER cancela): ")
    if ag_id is None:
        return

    agendamento = buscar_por_id(DADOS["agendamentos"], ag_id)
    if agendamento is None:
        print("Agendamento não encontrado.")
        return

    if not confirmar("Confirma o cancelamento?"):
        print("Cancelamento desfeito.")
        return

    DADOS["agendamentos"].remove(agendamento)
    salvar(DADOS)
    print("Agendamento cancelado com sucesso. O horário voltou a ficar livre.")


# ---------------------------------------------------------------------------
# Menus
# ---------------------------------------------------------------------------

def executar(funcao):
    funcao()
    pausar()


def menu_clientes():
    opcoes = {
        "1": cadastrar_cliente,
        "2": listar_clientes,
        "3": pesquisar_clientes,
        "4": excluir_cliente,
    }
    while True:
        print("\n--- CLIENTES ---")
        print("[1] Cadastrar cliente")
        print("[2] Listar clientes")
        print("[3] Pesquisar cliente por nome")
        print("[4] Excluir cliente")
        print("[0] Voltar")
        opcao = input("Opção: ").strip()
        if opcao == "0":
            return
        if opcao in opcoes:
            executar(opcoes[opcao])
        else:
            print("Opção inválida.")


def menu_animais():
    opcoes = {"1": cadastrar_animal, "2": listar_animais, "3": excluir_animal}
    while True:
        print("\n--- ANIMAIS ---")
        print("[1] Cadastrar animal")
        print("[2] Listar animais")
        print("[3] Excluir animal")
        print("[0] Voltar")
        opcao = input("Opção: ").strip()
        if opcao == "0":
            return
        if opcao in opcoes:
            executar(opcoes[opcao])
        else:
            print("Opção inválida.")


def menu_servicos():
    opcoes = {"1": cadastrar_servico, "2": listar_servicos, "3": excluir_servico}
    while True:
        print("\n--- SERVIÇOS ---")
        print("[1] Cadastrar serviço")
        print("[2] Listar serviços")
        print("[3] Excluir serviço")
        print("[0] Voltar")
        opcao = input("Opção: ").strip()
        if opcao == "0":
            return
        if opcao in opcoes:
            executar(opcoes[opcao])
        else:
            print("Opção inválida.")


def menu_agendamentos():
    opcoes = {
        "1": realizar_agendamento,
        "2": consultar_agendamentos,
        "3": filtrar_agendamentos_por_data,
        "4": cancelar_agendamento,
    }
    while True:
        print("\n--- AGENDAMENTOS ---")
        print("[1] Realizar agendamento")
        print("[2] Consultar agendamentos")
        print("[3] Consultar por data")
        print("[4] Cancelar agendamento")
        print("[0] Voltar")
        opcao = input("Opção: ").strip()
        if opcao == "0":
            return
        if opcao in opcoes:
            executar(opcoes[opcao])
        else:
            print("Opção inválida.")


def menu_principal():
    while True:
        print("\n==================================")
        print("   AlegreAnimal - Agendamentos")
        print("==================================")
        print("[1] Clientes")
        print("[2] Animais")
        print("[3] Serviços")
        print("[4] Agendamentos")
        print("[0] Sair")
        opcao = input("Opção: ").strip()

        if opcao == "1":
            menu_clientes()
        elif opcao == "2":
            menu_animais()
        elif opcao == "3":
            menu_servicos()
        elif opcao == "4":
            menu_agendamentos()
        elif opcao == "0":
            print("Até logo!")
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu_principal()
