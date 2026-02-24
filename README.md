# ⚖️ Crawler TJPA: Extrator de Dados Processuais

Este projeto é um protótipo desenvolvido para a
extração, normalização e persistência de dados jurídicos do Tribunal de
Justiça do Pará [(TJPA)](https://consulta-processual-unificada-prd.tjpa.jus.br/#/consulta). O foco principal é a superação de barreiras de
validação e a eficiência no consumo de APIs REST internas.

------------------------------------------------------------------------

## 📝 Descrição da Fonte e Desafios Técnicos

A fonte de dados é o portal de consulta pública do TJPA, que
disponibiliza informações através de endpoints JSON estruturados (Capa e
Movimentação).

### Principais Desafios

-   **Validação Matemática:** O servidor exige o cálculo exato do Dígito
    Verificador (ISO 7064 Mod 97-10). Requisições com DVs inválidos são
    descartadas antes da consulta ao banco.

-   **Fragmentação de Endpoints:** Os dados não residem em um único
    local. É necessário capturar IDs internos (`cdDocProcesso`) na Capa
    para acessar as Movimentações.

-   **Segurança (WAF):** Monitoramento ativo de Rate Limiting. O
    firewall do tribunal frequentemente retorna páginas HTML de erro
    quando detecta comportamento automatizado agressivo.

-   **Gaps de Numeração:** A distribuição de processos no PJe não é
    linear, apresentando grandes "buracos" sequenciais que podem travar
    crawlers simplistas.

------------------------------------------------------------------------

## 🚀 Estratégias de Coleta Adotadas

Para garantir eficiência e furtividade, foram implementadas as seguintes
táticas:

-   **Engenharia Reversa do CNJ:** Desconstrução da máscara do processo
    para geração dinâmica de números válidos via algoritmo de Módulo 97.

-   **Requisições Atômicas (Requests):** Substituição de emuladores de
    browser (Selenium) por chamadas HTTP diretas, reduzindo o consumo de
    memória em até 90%.

-   **Sondagem de Densidade (Scouting):** Uso de técnica de probing para
    localizar as faixas numéricas onde os processos estão realmente
    concentrados antes de iniciar a varredura em massa.

-   **Intervalos Aleatórios (Jitter):** Implementação de
    `random.uniform()` entre requisições para simular o tempo de leitura
    humano e evitar bloqueios por IP.

------------------------------------------------------------------------

## 📊 Resultados Obtidos com o Protótipo

-   **Velocidade:** Capacidade de processar aproximadamente 60--100
    processos por minuto (variando conforme a latência do servidor).

-   **Estabilidade:** Recuperação automática de erros de rede sem
    interrupção do script.

-   **Armazenamento:** Geração de arquivos JSONL, permitindo que cada
    registro seja lido ou escrito de forma independente, ideal para
    pipelines de Big Data.

------------------------------------------------------------------------

## ✅ Validações de Qualidade de Dados

Para garantir que a saída seja "Jusbrasil Style" (pronta para consumo),
o crawler executa:

-   **Normalização de Tipos:** Conversão de strings de data e listas de
    advogados em objetos estruturados.

-   **Checkpoint System:** Gravação do estado da coleta em tempo real.
    Se o processo for interrompido, ele retoma exatamente do último CNJ
    válido.

-   **Sanitização de Resposta:** Verificação de `Content-Type`. O script
    ignora retornos que não sejam JSON válido (como erros 404 ou 503
    mascarados em HTML).

------------------------------------------------------------------------

## 🛠️ Possíveis Melhorias e Manutenção

Para escalar o projeto e reduzir falhas recorrentes, sugere-se:

-   **Rotação de Proxies:** Implementar um pool de IPs para contornar
    bloqueios geográficos ou de volume do WAF.

-   **Contêinerização (Docker):** Isolar o ambiente para garantir que o
    crawler rode de forma idêntica em qualquer servidor ou instância na
    nuvem.

-   **Integração com Banco de Dados:** Migrar de JSONL para um banco
    NoSQL (como MongoDB) para facilitar buscas complexas e evitar
    duplicidade de registros.

-   **Monitoramento de Versão:** Criar um alerta para mudanças nos
    campos da API do tribunal, garantindo que o parser seja atualizado
    proativamente.
