#Ano que tem uma quantidade considerável de processos não vázios para serem utilizados 
ANO = "2023"
#Esse código de Comarca se refere a cidade de Parauapebas
COMARCA = "0040"

#O sequencial é o contador (ID) que identifica cada processo dentro de uma comarca e ano específicos. 
#Escolhi o 818800 por engenharia reversa observando que processos reais nessa comarca/ano iniciam nessa faixa de numeração, evitando varrer milhares de números iniciais vazios ou administrativos.
SEQUENCIAL_INICIAL = 818800 

OUTPUT_FILE = "base_tjpa.jsonl"
CHECKPOINT_FILE = f"checkpoint_{ANO}_{COMARCA}.txt"

TIMEOUT = 10
DELAY_MIN = 1.5
DELAY_MAX = 3.0
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"