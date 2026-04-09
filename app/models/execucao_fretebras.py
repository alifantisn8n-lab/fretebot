from sqlalchemy import Column, Integer, BigInteger, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base


class ExecucaoFretebras(Base):
    __tablename__ = "execucoes_fretebras"

    id = Column(BigInteger, primary_key=True, index=True)
    executado_em = Column(DateTime(timezone=True), server_default=func.now())
    arquivo_baixado = Column(Text, nullable=True)
    qtd_inseridos = Column(Integer, nullable=True)
    qtd_ignorados = Column(Integer, nullable=True)
    houve_reativacao = Column(Boolean, nullable=True)
    status = Column(Text, nullable=True)
    erro = Column(Text, nullable=True)