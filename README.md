# Crawler TJPA - Extrator de Dados Jurídicos

Este projeto realiza a extração automatizada de dados processuais do Tribunal de Justiça do Pará (TJPA) via API REST, focando em performance e resiliência para grandes volumes de dados.

## ⚖️ Análise Técnica: TJPA

### 🏗️ Estrutura e Organização
* **Interface:** Consumo de **endpoints JSON estruturados** (REST), eliminando a necessidade de parsing de tabelas HTML complexas.
* **Contextos de Dados:** A coleta é segmentada em dois blocos principais:
  * **Capa:** (`/processobycnj/`) Contém dados básicos, partes e classe.
  * **Movimentações:** (`/movimentacaobyprocesso/`) Histórico cronológico de eventos.
* **Vínculo:** Utiliza as chaves internas `cdDocProcesso` e `cdInstancia` para relacionar a capa às movimentações em um fluxo de coleta em duas etapas.

### 🚀 Navegação e Submissão
* **Método:** Requisições programáticas **GET** via URLs semânticas.
* **Busca:** Injeção direta do número CNJ no *path* da URL: `.../processobycnj/{CNJ}`.
* **Validação:** Exige cálculo rigoroso do **Dígito Verificador (ISO 7064 Mod 97-10)**. Requisições com DVs matematicamente incorretos são rejeitadas pelo servidor antes da consulta ao banco de dados.

### ⚠️ Desafios de Engenharia
* **Latência:** Necessidade de sincronia entre chamadas para garantir a integridade do vínculo entre capa e movimentação.
* **Segurança (WAF/Rate Limit):** Risco de bloqueio por IP. O sistema monitora acessos em massa; o tratamento de erros lida com retornos inesperados do firewall (ex: HTML em vez de JSON).
* **Gaps Sequenciais:** A numeração CNJ é descontínua. O crawler utiliza lógica de *checkpoint* e saltos para evitar travamentos em sequenciais inexistentes.
* **Volatilidade:** Manutenção contínua necessária devido a possíveis alterações em versões da API interna ou nomenclatura de campos.

## 🛠️ Tecnologias Utilizadas
* **Python 3.x**
* **Requests:** Comunicação HTTP de alta performance.
* **JSONL:** Formato de saída para persistência atômica de dados.

## ⚙️ Configuração
Os parâmetros de busca (Ano, Comarca, Sequencial Inicial) são gerenciados via arquivo `config.py` para facilitar a manutenção sem alteração do código core.

# 🔍 Engenharia Reversa da Numeração CNJ

Este projeto utiliza técnicas de engenharia reversa para mapear e automatizar a coleta de processos judiciais, superando as barreiras de validação e densidade de dados dos tribunais.

# 🛠️ Estratégia de Coleta de Dados

Esta seção detalha as decisões técnicas e a arquitetura implementada para garantir uma extração de dados resiliente e eficiente.

## ● Abordagem Técnica Adotada
A escolha técnica priorizou a performance ao evitar emuladores de browser (Selenium/Playwright) em favor de **requisições HTTP diretas** via biblioteca `requests`.

* **Vantagem:** Redução de consumo de memória em até 90% e maior velocidade, contornando o carregamento pesado de JavaScript do portal.
* **Engine de Captura:** O script atua como um cliente REST que injeta números CNJ gerados dinamicamente.
* **Fluxo de Dados:**
    1. Geração do CNJ com cálculo de **Dígito Verificador (DV)** em tempo de execução.
    2. Chamada ao endpoint de "Capa".
    3. Extração de tokens internos para chamada secundária de "Movimentações".
    4. Serialização direta para formato **JSONL (JSON Lines)**.

## ● Organização do Código e Manutenção
Estruturado sob princípios de **POO (Programação Orientada a Objetos)** e separação de preocupações:

* **Modularização:** A lógica de extração reside na classe `TJPAMassExtractor`. Parâmetros voláteis (ano, comarca, delays) ficam isolados em um arquivo `config.py`.
* **Checkpoint System:** Persistência de estado que salva o último sequencial processado. Isso permite retomar a coleta de onde parou em caso de interrupção, sem duplicidade.
* **Facilidade de Manutenção:** Alterações em cabeçalhos (headers) da API são feitas apenas no construtor da classe, sem afetar a lógica de negócio.

## ● Qualidade e Consistência dos Dados
Foco em gerar um dataset confiável para análise jurídica (estilo Jusbrasil):

* **Normalização de Tipos:** Conversão de strings brutas em estruturas de listas (partes) e dicionários (movimentações).
* **Identidade Única:** O número CNJ formatado é utilizado como chave primária natural no arquivo de saída.
* **Persistência Atômica:** O uso de **JSONL** garante que cada linha seja um objeto independente. Em caso de falha crítica, apenas o registro atual é perdido, preservando a integridade do restante do arquivo.

## ● Tratamento de Erros e Instabilidades
Implementação de mecanismos de defesa contra bloqueios e instabilidades do servidor:

* **Exponential Backoff & Jitter:** Uso de intervalos aleatórios (`random.uniform`) para simular comportamento humano e evitar gatilhos de *Rate Limiting*.
* **Try-Except Shields:** Tratamento de exceções em chamadas de rede. Erros de conexão ou erro 500 são registrados em logs, o checkpoint é atualizado e o processo segue para o próximo número.
* **Validação de Content-Type:** Verificação rigorosa se a resposta é um JSON válido antes do processamento, descartando páginas de erro HTML geradas em períodos de manutenção do tribunal.

# 📘 Documentação: Engenharia Reversa da Numeração CNJ

Este documento descreve a estratégia utilizada para reconstruir
programaticamente a numeração CNJ e automatizar consultas processuais no
Tribunal de Justiça do Estado do Pará (TJPA).

------------------------------------------------------------------------

## 1️⃣ Desconstrução do Objeto de Estudo

O primeiro passo foi decompor um número de processo conhecido para
identificar:

-   Componentes fixos
-   Variáveis dinâmicas
-   Elementos calculados (Dígito Verificador)

### 🔎 Exemplo analisado

0818800-53.2023.8.14.0040

  ------------------------------------------------------------------------
  Bloco      Valor     Significado                   Tipo
  ---------- --------- ----------------------------- ---------------------
  NNNNNNN    0818800   Sequencial Único              Variável (Alvo)

  DD         53        Dígito Verificador (DV)       Calculado (Algoritmo)

  AAAA       2023      Ano do Processo               Fixo/Configurável

  J.TR       8.14      Justiça Estadual (PA)         Fixo para TJPA

  OOOO       0040      Comarca (Parauapebas)         Fixo/Configurável
  ------------------------------------------------------------------------

------------------------------------------------------------------------

## 2️⃣ Algoritmo de Validação (Módulo 97)

A principal barreira da engenharia reversa é o Dígito Verificador (DV).

O tribunal rejeita qualquer requisição cujo DV não seja matematicamente
válido para o sequencial informado.

A validação segue a norma ISO 7064 (Módulo 97-10), baseada no resto da
divisão por 97.

### 🐍 Implementação em Python

``` python
def calcular_dv_cnj(sequencial, ano, comarca):
    '''
    Calcula o Dígito Verificador (DV) do padrão CNJ
    utilizando o algoritmo Módulo 97-10 (ISO 7064).
    '''

    # 1️⃣ Monta o corpo sem o DV:
    # NNNNNNN + AAAA + JTR (814 para TJPA) + OOOO
    corpo = f"{sequencial:07d}{ano}814{comarca}"

    # 2️⃣ Calcula o resto da divisão por 97
    resto = int(corpo) % 97

    # 3️⃣ Aplica a fórmula do DV
    dv = 98 - ((resto * 100) % 97)

    return f"{dv:02d}"
```

------------------------------------------------------------------------

## 3️⃣ Descoberta de Densidade (Scouting)

Os tribunais não distribuem processos de forma linear a partir do número
1.

Frequentemente existem:

-   Faixas reservadas
-   Processos migrados
-   Intervalos administrativos

Para evitar varreduras ineficientes, utilizamos a técnica de:

🔎 Sondagem por Faixas (Probing)

### 🐍 Exemplo de Probing

``` python
import requests

faixas_para_testar = [1, 1000, 500000, 800000]

for base in faixas_para_testar:
    dv = calcular_dv_cnj(base, "2023", "0040")
    cnj = f"{base:07d}{dv}20238140040"
    url = f"https://.../processobycnj/{cnj}"

    response = requests.get(url)

    print(f"Testando faixa {base}: Status {response.status_code}")
```

------------------------------------------------------------------------

## 4️⃣ Automação da Varredura (Crawl Loop)

Após identificar que a "veia" de dados inicia em 0818800, o script passa
a executar captura sequencial resiliente.

Cada requisição:

-   Gera DV válido
-   Mantém padrão legítimo
-   Evita rejeição automática

### 🐍 Loop de Backfill

``` python
def run_backfill(inicio=818800, quantidade=100):
    for i in range(inicio, inicio + quantidade):
        dv = calcular_dv_cnj(i, "2023", "0040")
        cnj = f"{i:07d}{dv}20238140040"

        # O crawler agora segue o rastro real dos dados
        data = capturar_dados(cnj)
```

------------------------------------------------------------------------

## 📈 Fluxo Completo

Análise Estrutural → Cálculo DV → Probing de Faixas → Identificação de
Densidade → Crawl Sequencial → Persistência
