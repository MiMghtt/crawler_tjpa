import requests
import json
import time
import os
import random
import config  

class TJPAMassExtractor:
    def __init__(self):
        self.base_api = "https://consulta-processual-unificada-prd.tjpa.jus.br/consilium-rest"
        self.ano = config.ANO
        self.comarca = config.COMARCA
        self.output_file = config.OUTPUT_FILE
        self.checkpoint_file = config.CHECKPOINT_FILE
        self.headers = {
            "User-Agent": config.USER_AGENT,
            "Accept": "application/json"
        }

    def calcular_dv_cnj(self, sequencial):
        corpo = f"{sequencial:07d}{self.ano}814{self.comarca}"
        resto = int(corpo) % 97
        dv = 98 - ((resto * 100) % 97)
        return f"{dv:02d}"

    def fetch_movimentacoes(self, cd_doc, cd_instancia):
        url = f"{self.base_api}/movimentacaobyprocesso/{cd_doc}/{cd_instancia}"
        try:
            res = requests.get(url, headers=self.headers, timeout=config.TIMEOUT)
            return res.json() if res.status_code == 200 else []
        except:
            return []

    def capturar_dados_completos(self, cnj_limpo):
        url_dados = f"{self.base_api}/processobycnj/{cnj_limpo}"
        try:
            res = requests.get(url_dados, headers=self.headers, timeout=config.TIMEOUT)
            if res.status_code != 200 or 'application/json' not in res.headers.get('Content-Type', ''):
                return None
            
            dados_brutos = res.json()
            processos_na_instancia = []

            for proc in dados_brutos.get("listaProcessos", []):
                item = {
                    "numero": proc.get("numeroFormatado"),
                    "classe": proc.get("classe"),
                    "assunto": proc.get("assunto"),
                    "instancia": proc.get("instancia"),
                    "partes": [{"nome": p.get("nome"), "tipo": p.get("tipo"), "polo": p.get("polo")} for p in proc.get("partes", [])],
                    "movimentacoes": []
                }

                cd_doc = proc.get("cdDocProcesso")
                cd_inst = proc.get("cdInstancia")
                if cd_doc and cd_inst:
                    movs = self.fetch_movimentacoes(cd_doc, cd_inst)
                    item["movimentacoes"] = [{"data": m.get("dataMovimentacaoFormatada"), "descricao": m.get("textoMovimentacao")} for m in movs]
                
                processos_na_instancia.append(item)
            return processos_na_instancia
        except:
            return None

    def carregar_checkpoint(self):
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, "r") as f:
                return int(f.read().strip())
        return config.SEQUENCIAL_INICIAL

    def salvar_checkpoint(self, seq):
        with open(self.checkpoint_file, "w") as f:
            f.write(str(seq))

    def run(self, range_busca=100):
        sequencial_atual = self.carregar_checkpoint()
        fim = sequencial_atual + range_busca
        
        print(f"Iniciando raspagem: Ano {self.ano}, Comarca {self.comarca}")
        print(f"Salvando em: {self.output_file}\n")

        for seq in range(sequencial_atual, fim):
            dv = self.calcular_dv_cnj(seq)
            cnj_limpo = f"{seq:07d}{dv}{self.ano}814{self.comarca}"
            
            dados = self.capturar_dados_completos(cnj_limpo)
            
            if dados:
                with open(self.output_file, "a", encoding="utf-8") as f:
                    for p in dados:
                        f.write(json.dumps(p, ensure_ascii=False) + "\n")
                print(f"SUCESSO: {cnj_limpo} | {len(dados[0]['movimentacoes'])} movimentações")
            else:
                print(f"VAZIO: {cnj_limpo}")

            self.salvar_checkpoint(seq + 1)
            time.sleep(random.uniform(config.DELAY_MIN, config.DELAY_MAX))

if __name__ == "__main__":
    scraper = TJPAMassExtractor()
    scraper.run(range_busca=50)