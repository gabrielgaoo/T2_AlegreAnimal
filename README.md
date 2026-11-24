SISTEMA DE AGENDAMENTO ALEGREANIMAL - T2 - LINGUAGENS DE PROGRAMACAO

Integrantes: Bia Gabriela, Marlon Domingos, Gabriel Guimaraes,
             William Alves de Santana
Linguagem:   Python 3

Arquivos
- main.py     : menus e todas as funcionalidades (clientes, animais,
                servicos e agendamentos).
- storage.py  : leitura e gravacao do arquivo dados.json.
- dados.json  : criado automaticamente na primeira execucao, na mesma
                pasta do codigo.

Como executar
1. Abra esta pasta no terminal (ou no VS Code).
2. Execute:
       python main.py
Nao e necessario instalar nenhuma biblioteca: o sistema usa apenas
modulos que ja vem com o Python (json, os, shutil, datetime).

Funcionalidades
- Clientes: cadastrar, listar, pesquisar por nome, excluir.
- Animais: cadastrar (ligados a um cliente), listar, excluir.
- Servicos: cadastrar, listar, excluir (4 servicos ja vem cadastrados).
- Agendamentos: realizar (cliente, animal, servico, data e horario livre),
  consultar, consultar por data, cancelar.
- Persistencia: todos os dados sao gravados em dados.json a cada alteracao.

Regras do sistema
- Um unico atendimento por horario. Horarios de 08:00 as 17:00, sem 12:00.
- Nao e possivel agendar em data que ja passou.
- Cliente, animal ou servico que ainda aparecem em agendamentos nao podem
  ser excluidos; cancele os agendamentos primeiro.
- Ao excluir um cliente, os animais dele sao excluidos junto (com
  confirmacao).
- Em qualquer pergunta de codigo ou data, ENTER vazio cancela a operacao.

Para recomecar do zero, apague o arquivo dados.json.
