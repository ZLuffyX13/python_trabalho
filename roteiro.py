from pilha import ir as pilha_ir, voltar as pilha_voltar, avancar as pilha_avancar, onde as pilha_onde


def ir(pilhas, caminho):
    if not caminho:
        raise ValueError("Caminho vazio")
    destino = caminho if caminho.startswith("/") else f"/{caminho}"
    pilha_ir(pilhas, destino)
    return destino


def voltar(pilhas):
    return pilha_voltar(pilhas)


def avancar(pilhas):
    return pilha_avancar(pilhas)


def onde(pilhas):
    return pilha_onde(pilhas)
