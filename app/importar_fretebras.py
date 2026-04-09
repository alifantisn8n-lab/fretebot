from pathlib import Path

from app.database import Base, engine, SessionLocal
from app.models.frete import Frete
from app.services.fretebras_parser import FretebrasParser


def montar_chave(row) -> str:
    origem = str(row["origem"] or "").strip().lower()
    destino = str(row["destino"] or "").strip().lower()
    carga = str(row["carga"] or "").strip().lower()
    veiculo = str(row["veiculo"] or "").strip().lower()
    preco = str(row["preco"] or "").strip().lower()
    peso_ton = str(row["peso_ton"] or "").strip().lower()

    return f"{origem}|{destino}|{carga}|{veiculo}|{preco}|{peso_ton}"


def importar_planilha(caminho_arquivo: str) -> dict:
    Base.metadata.create_all(bind=engine)

    parser = FretebrasParser(caminho_arquivo)
    df = parser.processar()

    db = SessionLocal()
    try:
        arquivo_nome = Path(caminho_arquivo).name
        inseridos = 0
        ignorados = 0

        for _, row in df.iterrows():
            chave_unica = montar_chave(row)

            existente = db.query(Frete).filter(Frete.chave_unica == chave_unica).first()
            if existente:
                ignorados += 1
                continue

            frete = Frete(
                chave_unica=chave_unica,
                linha_relatorio=int(row["linha_relatorio"]) if row["linha_relatorio"] is not None else None,
                origem=row["origem"],
                destino=row["destino"],
                carga=row["carga"],
                especie=row["especie"],
                exige_rastreamento=row["exige_rastreamento"],
                veiculo=row["veiculo"],
                carroceria=row["carroceria"],
                preco=row["preco"],
                peso_ton=row["peso_ton"],
                observacao=row["observacao"],
                arquivo_origem=arquivo_nome,
            )
            db.add(frete)
            inseridos += 1

        db.commit()

        print("Importação concluída com sucesso.")
        print(f"Inseridos: {inseridos}")
        print(f"Ignorados por duplicidade: {ignorados}")

        return {
            "arquivo": arquivo_nome,
            "inseridos": inseridos,
            "ignorados": ignorados,
        }

    except Exception as e:
        db.rollback()
        print(f"Erro ao importar planilha: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    caminho = base_dir / "downloads" / "Fretes 07-04-2026 11_32.xlsx"
    resultado = importar_planilha(str(caminho))
    print(resultado)