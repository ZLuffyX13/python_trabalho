# Sistema de Gerenciamento de Festival

Sistema de terminal para gestão de bilheteria e navegação de roteiro em festival universitário.

## Autores

João André Fagundes Pinto - 2025001852  
Tulio Andrade Franciscon - 2025008503

---

## Como Executar

```bash
python main.py
```

O sistema iniciará um prompt interativo onde você pode digitar comandos.

---

## Estrutura do Projeto

```
/projeto
  ├─ main.py          # Programa principal (loop de comandos)
  ├─ fila.py          # Gerenciamento de filas (PADRAO e PRIORIDADE)
  ├─ pilha.py         # Operações genéricas de pilha + navegação + undo/redo
  ├─ roteiro.py       # Navegação de diretórios (IR/VOLTAR/AVANCAR/ONDE)
  ├─ ingressos.py     # Modelagem de ingressos e persistência
  └─ README.md        # Este arquivo
```

---

## Exemplos de Uso

### Exemplo 1: Compra e Atendimento Básico

```
> COMPRAR Joao VIP
OK: ingresso 1

> COMPRAR Tulio INTEIRA
OK: ingresso 2

> COMPRAR Leticia MEIA
OK: ingresso 3

> LISTAR
[1] Joao (VIP)
[2] Tulio (INTEIRA)
[3] Leticia (MEIA)

> ENTRAR
Entrada: [1] Joao (VIP)

> ENTRAR
Entrada: [2] Tulio (INTEIRA)

> ESPIAR
Proximo: [3] Leticia (MEIA)

> ESTATISTICAS
pendentes=1, atendidos=2, por_categoria={'VIP': 1, 'INTEIRA': 1, 'MEIA': 1}, espera_media=0.0
```

### Exemplo 2: Sistema de Prioridade

```
> COMPRAR Pedro MEIA
OK: ingresso 1

> COMPRAR Andre VIP
OK: ingresso 2

> COMPRAR Alice INTEIRA
OK: ingresso 3

> MODO PRIORIDADE
OK

> LISTAR
[2] Andre (VIP)
[3] Alice (INTEIRA)
[1] Pedro (MEIA)

> ENTRAR
Entrada: [2] Andre (VIP)

> ENTRAR
Entrada: [3] Alice (INTEIRA)

> ENTRAR
Entrada: [1] Pedro (MEIA)
```

### Exemplo 3: Navegação de Roteiro

```
> ONDE
/

> IR /Palco
OK: /Palco

> IR Principal
OK: /Principal

> IR /IA/Visao
OK: /IA/Visao

> VOLTAR
OK: /Principal

> VOLTAR
OK: /Palco

> AVANCAR
OK: /Principal

> MAPA
Historico: ['/Palco'] -> [/Principal] -> ['/IA/Visao']
```

### Exemplo 4: Desfazer e Refazer

```
> COMPRAR Maria VIP
OK: ingresso 1

> ENTRAR
Entrada: [1] Maria (VIP)

> DESFAZER
OK: desfaz ENTRAR (ingresso 1 retorna a fila VIP)

> LISTAR
[1] Maria (VIP)

> REFAZER
OK

> LISTAR
Nenhum pendente
```

### Exemplo 5: Persistência

```
> COMPRAR João VIP
OK: ingresso 1

> COMPRAR Ana INTEIRA
OK: ingresso 2

> SALVAR estado.json
OK

> CANCELAR 1
OK: ingresso 1 cancelado

> CARREGAR estado.json
OK

> LISTAR
[1] João (VIP)
[2] Ana (INTEIRA)
```

---

## Principais Decisões de Implementação

### 1. Estruturas de Dados

#### Filas (`fila.py`)
- **Implementação**: `collections.deque` para operações eficientes (O(1))
- **Dois modos de operação**:
  - **PADRAO**: Fila única FIFO (First In, First Out)
  - **PRIORIDADE**: 3 filas separadas com ordem de atendimento VIP → INTEIRA → MEIA
- **Transição entre modos**: Ao mudar de PADRAO para PRIORIDADE, todos os elementos vão para a fila INTEIRA
- **Operações**: `enfileirar()`, `desenfileirar()`, `frente()`, `cancelar()`, `listar_pendentes()`

#### Pilhas (`pilha.py`)
- **Implementação**: Listas nativas do Python (`append()` para push, `pop()` para desempilhar)
- **Funções genéricas**: `criar_pilha()`, `vazia()`, `push()`, `pop()`, `top()`
- **Duas aplicações específicas**:
  1. **Navegação de roteiro**: Pilhas `voltar` e `avancar` para histórico de navegação
  2. **Undo/Redo**: Pilhas de snapshots completos do estado do sistema

#### Modelagem de Dados (`ingressos.py`)
- **Ingressos**: Dicionários Python com campos `id`, `nome`, `categoria`, `chegada_time`, `atendido`, `inicio_atendimento`
- **Categorias válidas**: `VIP`, `INTEIRA`, `MEIA`
- **Estado global**: Dicionário único contendo ingressos, filas, pilhas de navegação e undo/redo

### 2. Relógio Lógico

- **Propósito**: Medir tempo de espera na fila
- **Funcionamento**:
  - Inicializa em 0
  - `COMPRAR`: Registra `chegada_time = logical_clock` atual
  - `ENTRAR`: Incrementa `logical_clock++` e registra `inicio_atendimento`
  - **Tempo de espera** = `inicio_atendimento - chegada_time`
- **Cálculo de espera média**: Soma de todas as esperas dividida pelo número de atendidos

### 3. Sistema de Desfazer/Refazer

- **Estratégia**: Deep copy do estado completo antes de cada operação mutante
- **Operações que geram snapshot**:
  - `COMPRAR`, `ENTRAR`, `CANCELAR`, `MODO`, `IR`, `VOLTAR`, `AVANCAR`, `CARREGAR`
- **Operações que NÃO geram snapshot** (apenas consulta):
  - `ESPIAR`, `LISTAR`, `ONDE`, `MAPA`, `ESTATISTICAS`, `AJUDA`
- **Funcionamento**:
  - `DESFAZER`: Move estado atual para pilha `redo` e restaura topo de `undo`
  - `REFAZER`: Move estado atual para pilha `undo` e restaura topo de `redo`
  - Qualquer nova ação limpa a pilha `redo`

### 4. Navegação de Roteiro

- **Conceito**: Simulação de navegação em diretórios
- **Caminhos**:
  - Absolutos: começam com `/` (ex: `/Palco`, `/IA/Visao`)
  - Relativos: sem `/` inicial (ex: `Palco`, `Principal`) → convertidos automaticamente para absolutos
- **Histórico bidirecional**:
  - `IR <caminho>`: Salva localização atual em `voltar`, vai para novo local, limpa `avancar`
  - `VOLTAR`: Move de `voltar` para localização atual, salva atual em `avancar`
  - `AVANCAR`: Move de `avancar` para localização atual, salva atual em `voltar`

### 5. Persistência de Dados

- **Formato JSON** (padrão):
  - Salva estado completo: ingressos, filas, modo, relógio lógico, posição no roteiro
  - Restauração total do sistema
  - Usado para backups completos
  
- **Formato CSV** (simplificado):
  - Salva apenas lista de ingressos
  - Formato: `id,nome,categoria,chegada_time,atendido,inicio_atendimento`
  - Usado para exportação de dados tabulares

### 6. Tratamento de Erros

- Validações em cada módulo:
  - `fila.py`: Verifica categorias válidas
  - `pilha.py`: Retorna `None` se pilha vazia (evita exceções)
  - `ingressos.py`: Valida nome e categoria ao criar ingresso
  - `main.py`: Try-except global captura e exibe erros ao usuário
- Mensagens claras: `"Erro: Ingresso inexistente"`, `"Erro: Categoria invalida"`

---
