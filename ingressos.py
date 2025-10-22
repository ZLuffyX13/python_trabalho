import json

CATEGORIAS = {"INTEIRA", "MEIA", "VIP"}


def criar_ingresso(id_ingresso, nome, categoria, chegada_time):
    if categoria not in CATEGORIAS:
        raise ValueError(f"Categoria inválida: {categoria}. Use INTEIRA, MEIA ou VIP.")
    if not nome or not isinstance(nome, str):
        raise ValueError("Nome inválido.")
    
    return {
        "id": id_ingresso,
        "nome": nome,
        "categoria": categoria,
        "chegada_time": chegada_time,
        "atendido": False,
        "inicio_atendimento": None
    }


def estatisticas(state):
    if "ingressos" not in state:
        return {
            "pendentes": 0,
            "atendidos": 0,
            "por_categoria": {c: 0 for c in CATEGORIAS},
            "espera_media": 0.0,
        }
    
    ingressos = state["ingressos"]
    total_pend = 0
    total_atend = 0
    por_cat = {"VIP": 0, "INTEIRA": 0, "MEIA": 0}
    soma_espera = 0
    n_espera = 0

    for ing in ingressos.values():
        cat = ing["categoria"]
        if ing["atendido"]:
            total_atend += 1
            por_cat[cat] = por_cat.get(cat, 0) + 1
            if ing.get("inicio_atendimento") is not None and ing.get("chegada_time") is not None:
                soma_espera += (ing["inicio_atendimento"] - ing["chegada_time"])
                n_espera += 1
        else:
            total_pend += 1
            por_cat[cat] = por_cat.get(cat, 0) + 1
    
    espera_media = (soma_espera / n_espera) if n_espera > 0 else 0.0
    return {
        "pendentes": total_pend,
        "atendidos": total_atend,
        "por_categoria": por_cat,
        "espera_media": espera_media,
    }


def salvar(filename, state):
    if not filename:
        raise ValueError("Nome de arquivo vazio.")
    
    try:
        if filename.endswith('.csv'):
            with open(filename, "w", encoding="utf-8") as f:
                f.write("id,nome,categoria,chegada_time,atendido,inicio_atendimento\n")
                for ing in state.get("ingressos", {}).values():
                    f.write(f"{ing['id']},{ing['nome']},{ing['categoria']},{ing['chegada_time']},{ing['atendido']},{ing.get('inicio_atendimento', '')}\n")
        else:
            to_save = {
                "ingressos": state.get("ingressos", {}),
                "next_id": state.get("next_id", 1),
                "mode": state.get("mode", "PADRAO"),
                "logical_clock": state.get("logical_clock", 0),
                "fila_padrao": list(state.get("fila_padrao", [])),
                "filas_prioridade": {
                    "VIP": list(state.get("filas_prioridade", {}).get("VIP", [])),
                    "INTEIRA": list(state.get("filas_prioridade", {}).get("INTEIRA", [])),
                    "MEIA": list(state.get("filas_prioridade", {}).get("MEIA", [])),
                },
                "current_location": state.get("current_location", "/"),
                "voltar": list(state.get("voltar", [])),
                "avancar": list(state.get("avancar", [])),
            }
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(to_save, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        raise IOError(f"Erro ao salvar: {e}")


def carregar(filename):
    if not filename:
        raise ValueError("Nome de arquivo vazio.")
    
    try:
        if filename.endswith('.csv'):
            ingressos = {}
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()[1:]
                for line in lines:
                    parts = line.strip().split(',')
                    if len(parts) >= 5:
                        ing_id = int(parts[0])
                        ingressos[ing_id] = {
                            "id": ing_id,
                            "nome": parts[1],
                            "categoria": parts[2],
                            "chegada_time": int(parts[3]),
                            "atendido": parts[4].lower() == 'true',
                            "inicio_atendimento": int(parts[5]) if parts[5] else None
                        }
            return {"ingressos": ingressos, "next_id": max(ingressos.keys()) + 1 if ingressos else 1}
        else:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {
                "ingressos": data.get("ingressos", {}),
                "next_id": data.get("next_id", 1),
                "mode": data.get("mode", "PADRAO"),
                "logical_clock": data.get("logical_clock", 0),
                "fila_padrao": data.get("fila_padrao", []),
                "filas_prioridade": {
                    "VIP": data.get("filas_prioridade", {}).get("VIP", []),
                    "INTEIRA": data.get("filas_prioridade", {}).get("INTEIRA", []),
                    "MEIA": data.get("filas_prioridade", {}).get("MEIA", []),
                },
                "current_location": data.get("current_location", "/"),
                "voltar": data.get("voltar", []),
                "avancar": data.get("avancar", []),
            }
    except FileNotFoundError:
        raise FileNotFoundError(f"Arquivo não encontrado: {filename}")
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Erro ao ler arquivo: {e}")
