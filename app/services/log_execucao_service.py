from app.database import SessionLocal
from app.models.execucao_fretebras import ExecucaoFretebras


def registrar_execucao(arquivo_baixado, qtd_inseridos, qtd_ignorados, houve_reativacao, status, erro=None):
    db = SessionLocal()
    try:
        execucao = ExecucaoFretebras(
            arquivo_baixado=arquivo_baixado,
            qtd_inseridos=qtd_inseridos,
            qtd_ignorados=qtd_ignorados,
            houve_reativacao=houve_reativacao,
            status=status,
            erro=erro,
        )
        db.add(execucao)
        db.commit()
    finally:
        db.close()