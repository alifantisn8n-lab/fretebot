from app.baixar_fretebras import baixar_listagem
from app.importar_fretebras import importar_planilha
from app.services.log_execucao_service import registrar_execucao

def main():
    print("🚀 Iniciando execução única...")

    try:
        resultado_download = baixar_listagem()
        arquivo = resultado_download["arquivo"]
        houve_reativacao = resultado_download.get("houve_reativacao", False)

        resultado_importacao = importar_planilha(str(arquivo))

        registrar_execucao(
            arquivo_baixado=str(arquivo),
            qtd_inseridos=resultado_importacao["inseridos"],
            qtd_ignorados=resultado_importacao["ignorados"],
            houve_reativacao=houve_reativacao,
            status="SUCESSO",
            erro=None,
        )

        print("✅ Execução finalizada com sucesso.")

    except Exception as e:
        registrar_execucao(
            arquivo_baixado=None,
            qtd_inseridos=0,
            qtd_ignorados=0,
            houve_reativacao=False,
            status="ERRO",
            erro=str(e),
        )
        print(f"❌ Erro na execução: {e}")
        raise

if __name__ == "__main__":
    main()