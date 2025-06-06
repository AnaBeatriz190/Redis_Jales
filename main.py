import redis
import uuid
import time

r = redis.Redis(
    host='redis-19444.c336.samerica-east1-1.gce.redns.redis-cloud.com',
    port=19444,
    decode_responses=True,
    username="default",
    password="Em1iQAulxiTFo9NvbzCiIsF4cfbtiVPO",
)

# Exercício 1 – Lista de Tarefas (usando list)
def adicionar_tarefa_lista(usuario, descricao):
    r.rpush(f"tarefas:{usuario}", descricao)

def listar_tarefas_lista(usuario):
    tarefas = r.lrange(f"tarefas:{usuario}", 0, -1)
    for i, tarefa in enumerate(tarefas, 1):
        print(f"{i}. {tarefa}")

def remover_tarefa_lista(usuario, indice):
    tarefas = r.lrange(f"tarefas:{usuario}", 0, -1)
    if 0 <= indice < len(tarefas):
        r.lrem(f"tarefas:{usuario}", 1, tarefas[indice])
        print("Tarefa removida.")
    else:
        print("Índice inválido.")

# Exercício 2 – Ranking com Sorted Set
def atualizar_pontuacao(jogador, pontuacao):
    r.zadd("ranking", {jogador: pontuacao})

def listar_top_5():
    top = r.zrevrange("ranking", 0, 4, withscores=True)
    for i, (jogador, score) in enumerate(top, 1):
        print(f"{i}. {jogador} - {int(score)}")

# Exercício 3 – Contador de Acessos
def registrar_acesso(pagina):
    return r.incr(f"acessos:{pagina}")

def mostrar_acessos(pagina):
    acessos = r.get(f"acessos:{pagina}") or 0
    print(f"Acessos à página '{pagina}': {acessos}")

# Exercício 4 – Sistema de Amigos Online
def usuario_online(usuario_id):
    r.sadd("usuarios_online", usuario_id)

def usuario_offline(usuario_id):
    r.srem("usuarios_online", usuario_id)

def listar_online():
    print("Usuários online:", list(r.smembers("usuarios_online")))

# Exercício 5 – Rate Limiting
def pode_fazer_requisicao(usuario_id, limite=5):
    chave = f"rate:{usuario_id}:{int(time.time() // 60)}"
    atual = r.incr(chave)
    r.expire(chave, 60)
    if atual > limite:
        print("Limite de requisições excedido.")
        return False
    print(f"Requisição {atual}/{limite} permitida.")
    return True

# Exercício 6 – Operações com Sets
def seguir(usuario, outro):
    r.sadd(f"seguindo:{usuario}", outro)
    r.sadd(f"seguidores:{outro}", usuario)

def deixar_de_seguir(usuario, outro):
    r.srem(f"seguindo:{usuario}", outro)
    r.srem(f"seguidores:{outro}", usuario)

def amigos_em_comum(usuario1, usuario2):
    return r.sinter(f"seguindo:{usuario1}", f"seguidores:{usuario1}", 
                    f"seguindo:{usuario2}", f"seguidores:{usuario2}")

def todos_os_contatos(usuario):
    return r.sunion(f"seguindo:{usuario}", f"seguidores:{usuario}")

def quem_nao_te_segue_de_volta(usuario):
    return r.sdiff(f"seguindo:{usuario}", f"seguidores:{usuario}")

# MENU PRINCIPAL
while True:
    print("\n======= MENU REDIS =======")
    print("1 - Lista de tarefas (list)")
    print("2 - Ranking de jogadores (sorted set)")
    print("3 - Contador de acessos (string)")
    print("4 - Amigos online (set)")
    print("5 - Rate limiting")
    print("6 - Seguidores e seguindo (set)")
    print("0 - Sair")
    print("==========================")
    opcao = input("Escolha uma opção: ")

    match opcao:
        case '1':
            usuario = input("Nome do usuário: ")
            print("a) Adicionar tarefa\nb) Listar tarefas\nc) Remover tarefa")
            acao = input("Escolha a ação: ").lower()
            if acao == 'a':
                desc = input("Descrição da tarefa: ")
                adicionar_tarefa_lista(usuario, desc)
            elif acao == 'b':
                listar_tarefas_lista(usuario)
            elif acao == 'c':
                listar_tarefas_lista(usuario)
                idx = int(input("Número da tarefa para remover (1...): ")) - 1
                remover_tarefa_lista(usuario, idx)
        case '2':
            print("a) Adicionar/Atualizar pontuação\nb) Ver top 5")
            acao = input("Escolha a ação: ").lower()
            if acao == 'a':
                jogador = input("Nome do jogador: ")
                pontos = int(input("Pontuação: "))
                atualizar_pontuacao(jogador, pontos)
            elif acao == 'b':
                listar_top_5()
        case '3':
            print("a) Registrar acesso\nb) Ver acessos")
            acao = input("Escolha a ação: ").lower()
            pagina = input("Nome da página: ")
            if acao == 'a':
                registrar_acesso(pagina)
            elif acao == 'b':
                mostrar_acessos(pagina)
        case '4':
            print("a) Entrar online\nb) Sair offline\nc) Listar online")
            acao = input("Escolha a ação: ").lower()
            if acao in ['a', 'b']:
                user_id = input("ID do usuário: ")
                if acao == 'a':
                    usuario_online(user_id)
                else:
                    usuario_offline(user_id)
            elif acao == 'c':
                listar_online()
        case '5':
            user_id = input("ID do usuário: ")
            pode_fazer_requisicao(user_id)
        case '6':
            usuario = input("Seu usuário: ")
            print("a) Seguir alguém\nb) Deixar de seguir\nc) Amigos em comum\nd) Todos os contatos\ne) Quem você segue que não te segue")
            acao = input("Escolha a ação: ").lower()
            if acao in ['a', 'b']:
                outro = input("Usuário alvo: ")
                if acao == 'a':
                    seguir(usuario, outro)
                else:
                    deixar_de_seguir(usuario, outro)
            elif acao == 'c':
                outro = input("Outro usuário: ")
                print("Amigos em comum:", list(amigos_em_comum(usuario, outro)))
            elif acao == 'd':
                print("Todos os contatos:", list(todos_os_contatos(usuario)))
            elif acao == 'e':
                print("Quem você segue que não te segue:", list(quem_nao_te_segue_de_volta(usuario)))
        case '0':
            print("Saindo...")
            break
        case _:
            print("Opção inválida!")
