from pathlib import Path
import shutil
import win32com.client as win32


def converter_xls_para_xlsx(caminho_arquivo: str) -> str:
    caminho = Path(caminho_arquivo).resolve()

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    # se já for .xls, cria cópia com nome diferente
    if caminho.suffix.lower() == ".xls":
        caminho_temp_xls = caminho.with_name(f"{caminho.stem}__temp.xls")
    else:
        caminho_temp_xls = caminho.with_suffix(".xls")

    caminho_xlsx_final = caminho.with_name(f"{caminho.stem}.convertido.xlsx")

    if caminho_temp_xls.exists():
        caminho_temp_xls.unlink()

    if caminho_xlsx_final.exists():
        caminho_xlsx_final.unlink()

    shutil.copyfile(caminho, caminho_temp_xls)

    excel = win32.Dispatch("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    workbook = None
    try:
        workbook = excel.Workbooks.Open(str(caminho_temp_xls))
        workbook.SaveAs(str(caminho_xlsx_final), FileFormat=51)  # xlsx
        workbook.Close(False)
        workbook = None
    finally:
        if workbook is not None:
            workbook.Close(False)
        excel.Quit()

        if caminho_temp_xls.exists():
            caminho_temp_xls.unlink()

    return str(caminho_xlsx_final)