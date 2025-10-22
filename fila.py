from collections import deque

CATEGORIAS = {"INTEIRA", "MEIA", "VIP"}


def criar_fila():
    return {
        "mode": "PADRAO",
        "fila_padrao": deque(),
        "filas_prioridade": {
            "VIP": deque(),
            "INTEIRA": deque(),
            "MEIA": deque(),
        }
    }


def set_mode(fila, mode):
    mode = mode.upper()
    if mode not in ["PADRAO", "PRIORIDADE"]:
        raise ValueError("Modo inválido. Use PADRAO ou PRIORIDADE.")
    
    if fila["mode"] == mode:
        return
    
    if fila["mode"] == "PADRAO" and mode == "PRIORIDADE":
        while fila["fila_padrao"]:
            fila["filas_prioridade"]["INTEIRA"].append(fila["fila_padrao"].popleft())
    
    elif fila["mode"] == "PRIORIDADE" and mode == "PADRAO":
        for cat in ["VIP", "INTEIRA", "MEIA"]:
            while fila["filas_prioridade"][cat]:
                fila["fila_padrao"].append(fila["filas_prioridade"][cat].popleft())
    
    fila["mode"] = mode


def enfileirar(fila, ingresso_id, categoria):
    if categoria not in CATEGORIAS:
        raise ValueError(f"Categoria inválida: {categoria}")
    
    if fila["mode"] == "PADRAO":
        fila["fila_padrao"].append(ingresso_id)
    else:
        fila["filas_prioridade"][categoria].append(ingresso_id)


def desenfileirar(fila):
    if fila["mode"] == "PADRAO":
        return fila["fila_padrao"].popleft() if fila["fila_padrao"] else None
    else:
        for cat in ["VIP", "INTEIRA", "MEIA"]:
            if fila["filas_prioridade"][cat]:
                return fila["filas_prioridade"][cat].popleft()
        return None


def frente(fila):
    if fila["mode"] == "PADRAO":
        return fila["fila_padrao"][0] if fila["fila_padrao"] else None
    else:
        for cat in ["VIP", "INTEIRA", "MEIA"]:
            if fila["filas_prioridade"][cat]:
                return fila["filas_prioridade"][cat][0]
        return None


def vazia(fila):
    if fila["mode"] == "PADRAO":
        return len(fila["fila_padrao"]) == 0
    else:
        return all(len(fila["filas_prioridade"][cat]) == 0 for cat in ["VIP", "INTEIRA", "MEIA"])


def cancelar(fila, ingresso_id):
    try:
        fila["fila_padrao"].remove(ingresso_id)
        return True
    except ValueError:
        pass
    
    for cat in fila["filas_prioridade"]:
        try:
            fila["filas_prioridade"][cat].remove(ingresso_id)
            return True
        except ValueError:
            pass
    return False


def listar_pendentes(fila):
    if fila["mode"] == "PADRAO":
        return list(fila["fila_padrao"])
    else:
        lst = []
        for cat in ["VIP", "INTEIRA", "MEIA"]:
            lst.extend(list(fila["filas_prioridade"][cat]))
        return lst


        
