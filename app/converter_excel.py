from pathlib import Path
import shutil


def converter_xls_para_xlsx(caminho_arquivo: str) -> str:
    caminho = Path(caminho_arquivo).resolve()

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    # no Railway/Linux não vamos converter via Excel
    # por enquanto apenas retorna o próprio caminho
    return str(caminho)