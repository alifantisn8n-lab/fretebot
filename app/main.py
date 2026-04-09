from app.database import Base, engine
from app.models.frete import Frete
from app.models.execucao_fretebras import ExecucaoFretebras

Base.metadata.create_all(bind=engine)
print("Tabelas criadas com sucesso")