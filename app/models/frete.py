from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text
from datetime import datetime
from app.database import Base

class Frete(Base):
    __tablename__ = "fretes"

    id = Column(Integer, primary_key=True, index=True)
    chave_unica = Column(String, unique=True, index=True, nullable=True)

    linha_relatorio = Column(Integer, nullable=True)
    origem = Column(String, nullable=True)
    destino = Column(String, nullable=True)
    carga = Column(String, nullable=True)
    especie = Column(String, nullable=True)
    exige_rastreamento = Column(String, nullable=True)
    veiculo = Column(Text, nullable=True)
    carroceria = Column(Text, nullable=True)
    preco = Column(Numeric(12, 2), nullable=True)
    peso_ton = Column(Numeric(12, 3), nullable=True)
    observacao = Column(Text, nullable=True)
    arquivo_origem = Column(String, nullable=True)
    importado_em = Column(DateTime, default=datetime.utcnow)