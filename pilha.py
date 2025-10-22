def criar_pilha():
    return []

def vazia(p):
    return len(p) == 0

def push(p, x):
    p.append(x)

def pop(p):
    if vazia(p):
        return None
    return p.pop()

def top(p):
    if vazia(p):
        return None
    return p[-1]


def criar_pilhas_roteiro():
    return {
        "voltar": criar_pilha(),
        "avancar": criar_pilha(),
        "current_location": "/"
    }

def ir(pilhas, destino):
    if not destino or not isinstance(destino, str):
        raise ValueError("Destino inválido.")
    push(pilhas["voltar"], pilhas["current_location"])
    pilhas["current_location"] = destino
    pilhas["avancar"].clear()

def voltar(pilhas):
    topo = pop(pilhas["voltar"])
    if topo is None:
        return None
    push(pilhas["avancar"], pilhas["current_location"])
    pilhas["current_location"] = topo
    return topo

def avancar(pilhas):
    topo = pop(pilhas["avancar"])
    if topo is None:
        return None
    push(pilhas["voltar"], pilhas["current_location"])
    pilhas["current_location"] = topo
    return topo

def onde(pilhas):
    return pilhas["current_location"]


def criar_pilhas_undo():
    return {
        "undo": criar_pilha(),
        "redo": criar_pilha()
    }

def push_undo(pilhas, snapshot):
    if snapshot is None:
        raise ValueError("Snapshot não pode ser None.")
    push(pilhas["undo"], snapshot)
    pilhas["redo"].clear()

def desfazer(pilhas, current_snapshot):
    prev = pop(pilhas["undo"])
    if prev is None:
        return None
    push(pilhas["redo"], current_snapshot)
    return prev

def refazer(pilhas, current_snapshot):
    nxt = pop(pilhas["redo"])
    if nxt is None:
        return None
    push(pilhas["undo"], current_snapshot)
    return nxt
