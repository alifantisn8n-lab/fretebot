import pandas as pd
from pathlib import Path


class FretebrasParser:
    def __init__(self, caminho_arquivo: str):
        self.caminho_arquivo = Path(caminho_arquivo)

    def limpar_texto(self, valor):
        if pd.isna(valor):
            return None
        texto = str(valor).strip()
        return texto if texto else None

    def limpar_decimal_brasil(self, valor):
        if pd.isna(valor):
            return None

        if isinstance(valor, (int, float)):
            return float(valor)

        texto = str(valor).strip()
        if not texto:
            return None

        texto = texto.replace(".", "").replace(",", ".")
        try:
            return float(texto)
        except ValueError:
            return None

    def _encontrar_linha_cabecalho(self, df_bruto: pd.DataFrame) -> int:
        for i in range(min(len(df_bruto), 40)):
            linha = [str(x).strip().lower() for x in df_bruto.iloc[i].tolist()]
            if "origem" in linha and "destino" in linha:
                return i
        raise ValueError("Não encontrei a linha de cabeçalho da planilha.")

    def ler_arquivo(self):
    print("🌐 Tentando ler arquivo do Fretebras como HTML...")

    try:
        # lê o arquivo bruto como bytes
        with open(self.caminho_arquivo, "rb") as f:
            conteudo = f.read()

        # tenta decodificar corretamente (Fretebras geralmente latin1)
        try:
            html = conteudo.decode("latin1")
        except:
            html = conteudo.decode("utf-8", errors="ignore")

        # passa o HTML já tratado pro pandas
        tabelas = pd.read_html(html)

        if not tabelas:
            raise ValueError("Nenhuma tabela encontrada no arquivo")

        print(f"✅ {len(tabelas)} tabela(s) encontrada(s)")
        return tabelas[0]

    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo do Fretebras como HTML: {e}")
    
    def processar(self):
        df_bruto = self.ler_arquivo()

        linha_cabecalho = self._encontrar_linha_cabecalho(df_bruto)
        cabecalho = df_bruto.iloc[linha_cabecalho].tolist()
        df = df_bruto.iloc[linha_cabecalho + 1:].copy()
        df.columns = cabecalho

        df = df.rename(columns={
            "#": "linha_relatorio",
            "Origem": "origem",
            "Destino": "destino",
            "Carga": "carga",
            "Espécie": "especie",
            "Exige Rastreamento": "exige_rastreamento",
            "Veículo": "veiculo",
            "Carroceria": "carroceria",
            "Preço": "preco",
            "Peso (ton)": "peso_ton",
            "Obs.": "observacao",
        })

        colunas_esperadas = [
            "linha_relatorio",
            "origem",
            "destino",
            "carga",
            "especie",
            "exige_rastreamento",
            "veiculo",
            "carroceria",
            "preco",
            "peso_ton",
            "observacao",
        ]

        faltantes = [c for c in colunas_esperadas if c not in df.columns]
        if faltantes:
            raise ValueError(f"Colunas não encontradas após leitura: {faltantes}")

        df = df[colunas_esperadas].copy()
        df = df.dropna(subset=["origem", "destino"], how="all")

        for coluna in [
            "origem",
            "destino",
            "carga",
            "especie",
            "exige_rastreamento",
            "veiculo",
            "carroceria",
            "observacao",
        ]:
            df[coluna] = df[coluna].apply(self.limpar_texto)

        df["linha_relatorio"] = pd.to_numeric(df["linha_relatorio"], errors="coerce")
        df["preco"] = df["preco"].apply(self.limpar_decimal_brasil)
        df["peso_ton"] = df["peso_ton"].apply(self.limpar_decimal_brasil)

        df = df.reset_index(drop=True)
        return df