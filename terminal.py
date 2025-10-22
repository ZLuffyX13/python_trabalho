import copy
from fila import criar_fila, enfileirar, desenfileirar, frente, cancelar, listar_pendentes, set_mode
from pilha import criar_pilhas_roteiro, criar_pilhas_undo, push_undo, desfazer, refazer
from roteiro import ir, voltar, avancar, onde
from ingressos import criar_ingresso, estatisticas, salvar, carregar


def criar_estado():
    return {
        'ingressos': {},
        'next_id': 1,
        'fila': criar_fila(),
        'logical_clock': 0,
        'roteiro': criar_pilhas_roteiro(),
        'undo_redo': criar_pilhas_undo(),
        'action_history': []
    }


def main():
    estado = criar_estado()
    push_undo(estado['undo_redo'], copy.deepcopy(estado))
    
    while True:
        try:
            linha = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nSaindo.')
            break
        
        if not linha:
            continue
        
        partes = linha.split(maxsplit=2)
        op = partes[0].upper()
        
        try:
            if op == 'AJUDA':
                print('Comandos: COMPRAR/ENTRAR/ESPIAR/CANCELAR/LISTAR/ESTATISTICAS/MODO/IR/VOLTAR/AVANCAR/ONDE/MAPA/DESFAZER/REFAZER/SALVAR/CARREGAR/AJUDA/SAIR')
            
            elif op == 'SAIR':
                break
            
            elif op == 'COMPRAR':
                if len(partes) < 3:
                    print('Uso: COMPRAR <nome> <categoria>')
                    continue
                categoria = partes[2].upper()
                if categoria not in {'INTEIRA', 'MEIA', 'VIP'}:
                    print('Erro: Categoria invalida')
                    continue
                
                ing_id = estado['next_id']
                push_undo(estado['undo_redo'], copy.deepcopy(estado))
                estado['action_history'].append(f'COMPRAR {partes[1]} {categoria} (ingresso {ing_id})')
                
                ing = criar_ingresso(ing_id, partes[1], categoria, estado['logical_clock'])
                estado['ingressos'][ing_id] = ing
                enfileirar(estado['fila'], ing_id, categoria)
                estado['next_id'] += 1
                print(f'OK: ingresso {ing_id}')
            
            elif op == 'ENTRAR':
                ing_id = frente(estado['fila'])
                if ing_id is None:
                    print('Fila vazia')
                else:
                    ing_info = estado['ingressos'][ing_id]
                    push_undo(estado['undo_redo'], copy.deepcopy(estado))
                    estado['action_history'].append(f"ENTRAR (ingresso {ing_id} retorna a fila {ing_info['categoria']})")
                    
                    desenfileirar(estado['fila'])
                    ing_info['atendido'] = True
                    ing_info['inicio_atendimento'] = estado['logical_clock']
                    estado['logical_clock'] += 1
                    print(f"Entrada: [{ing_id}] {ing_info['nome']} ({ing_info['categoria']})")
            
            elif op == 'ESPIAR':
                ing_id = frente(estado['fila'])
                if ing_id is None:
                    print('Fila vazia')
                else:
                    ing = estado['ingressos'][ing_id]
                    print(f"Proximo: [{ing_id}] {ing['nome']} ({ing['categoria']})")
            
            elif op == 'CANCELAR':
                if len(partes) < 2:
                    print('Uso: CANCELAR <id>')
                    continue
                ing_id = int(partes[1])
                if ing_id not in estado['ingressos']:
                    print('Erro: Ingresso inexistente')
                elif estado['ingressos'][ing_id]['atendido']:
                    print('Erro: Ingresso ja atendido')
                else:
                    push_undo(estado['undo_redo'], copy.deepcopy(estado))
                    estado['action_history'].append(f'CANCELAR {ing_id}')
                    if cancelar(estado['fila'], ing_id):
                        del estado['ingressos'][ing_id]
                        print(f'OK: ingresso {ing_id} cancelado')
                    else:
                        print(f'Ingresso {ing_id} nao encontrado')
            
            elif op == 'LISTAR':
                pendentes = listar_pendentes(estado['fila'])
                if not pendentes:
                    print('Nenhum pendente')
                else:
                    for i in pendentes:
                        if i in estado['ingressos']:
                            ing = estado['ingressos'][i]
                            print(f"[{i}] {ing['nome']} ({ing['categoria']})")
            
            elif op == 'ESTATISTICAS':
                st = estatisticas({
                    'ingressos': estado['ingressos'],
                    'fila_padrao': estado['fila']['fila_padrao'],
                    'filas_prioridade': estado['fila']['filas_prioridade']
                })
                print(f"pendentes={st['pendentes']}, atendidos={st['atendidos']}, por_categoria={st['por_categoria']}, espera_media={st['espera_media']}")
            
            elif op == 'MODO':
                if len(partes) < 2:
                    print('Uso: MODO PADRAO|PRIORIDADE')
                    continue
                push_undo(estado['undo_redo'], copy.deepcopy(estado))
                estado['action_history'].append(f'MODO {partes[1]}')
                set_mode(estado['fila'], partes[1])
                print('OK')
            
            elif op == 'IR':
                if len(partes) < 2:
                    print('Uso: IR <caminho>')
                    continue
                push_undo(estado['undo_redo'], copy.deepcopy(estado))
                estado['action_history'].append(f'IR {partes[1]}')
                dest = ir(estado['roteiro'], partes[1])
                print(f'OK: {dest}')
            
            elif op == 'VOLTAR':
                push_undo(estado['undo_redo'], copy.deepcopy(estado))
                estado['action_history'].append('VOLTAR')
                res = voltar(estado['roteiro'])
                if res is None:
                    print('Nada para voltar')
                else:
                    print(f'OK: {res}')
            
            elif op == 'AVANCAR':
                push_undo(estado['undo_redo'], copy.deepcopy(estado))
                estado['action_history'].append('AVANCAR')
                res = avancar(estado['roteiro'])
                if res is None:
                    print('Nada para avancar')
                else:
                    print(f'OK: {res}')
            
            elif op == 'ONDE':
                print(onde(estado['roteiro']))
            
            elif op == 'MAPA':
                r = estado['roteiro']
                print(f"Historico: {r['voltar']} -> [{r['current_location']}] -> {r['avancar']}")
            
            elif op == 'SALVAR':
                if len(partes) < 2:
                    print('Uso: SALVAR <arquivo>')
                    continue
                salvar(partes[1], {
                    'ingressos': estado['ingressos'],
                    'next_id': estado['next_id'],
                    'mode': estado['fila']['mode'],
                    'logical_clock': estado['logical_clock'],
                    'fila_padrao': list(estado['fila']['fila_padrao']),
                    'filas_prioridade': {k: list(v) for k, v in estado['fila']['filas_prioridade'].items()},
                    'current_location': estado['roteiro']['current_location'],
                    'voltar': estado['roteiro']['voltar'],
                    'avancar': estado['roteiro']['avancar']
                })
                print('OK')
            
            elif op == 'CARREGAR':
                if len(partes) < 2:
                    print('Uso: CARREGAR <arquivo>')
                    continue
                push_undo(estado['undo_redo'], copy.deepcopy(estado))
                estado['action_history'].append(f'CARREGAR {partes[1]}')
                loaded = carregar(partes[1])
                estado['ingressos'] = {int(k): v for k, v in loaded.get('ingressos', {}).items()}
                estado['next_id'] = loaded.get('next_id', 1)
                estado['fila']['mode'] = loaded.get('mode', 'PADRAO')
                estado['logical_clock'] = loaded.get('logical_clock', 0)
                from collections import deque
                estado['fila']['fila_padrao'] = deque(loaded.get('fila_padrao', []))
                fps = loaded.get('filas_prioridade', {})
                estado['fila']['filas_prioridade'] = {
                    'VIP': deque(fps.get('VIP', [])),
                    'INTEIRA': deque(fps.get('INTEIRA', [])),
                    'MEIA': deque(fps.get('MEIA', []))
                }
                estado['roteiro']['current_location'] = loaded.get('current_location', '/')
                estado['roteiro']['voltar'] = loaded.get('voltar', [])
                estado['roteiro']['avancar'] = loaded.get('avancar', [])
                print('OK')
            
            elif op == 'DESFAZER':
                prev = desfazer(estado['undo_redo'], copy.deepcopy(estado))
                if prev is None:
                    print('Nada para desfazer')
                else:
                    acao = estado['action_history'].pop() if estado['action_history'] else None
                    estado['ingressos'] = copy.deepcopy(prev['ingressos'])
                    estado['next_id'] = prev['next_id']
                    estado['fila'] = copy.deepcopy(prev['fila'])
                    estado['logical_clock'] = prev['logical_clock']
                    estado['roteiro'] = copy.deepcopy(prev['roteiro'])
                    if acao:
                        print(f'OK: desfaz {acao}')
                    else:
                        print('OK')
            
            elif op == 'REFAZER':
                prox = refazer(estado['undo_redo'], copy.deepcopy(estado))
                if prox is None:
                    print('Nada para refazer')
                else:
                    estado['ingressos'] = copy.deepcopy(prox['ingressos'])
                    estado['next_id'] = prox['next_id']
                    estado['fila'] = copy.deepcopy(prox['fila'])
                    estado['logical_clock'] = prox['logical_clock']
                    estado['roteiro'] = copy.deepcopy(prox['roteiro'])
                    print('OK')
            
            else:
                print(f'Comando desconhecido: {op}')
        
        except Exception as e:
            print(f'Erro: {e}')


main()
