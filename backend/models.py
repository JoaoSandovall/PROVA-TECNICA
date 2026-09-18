from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base

class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    nome_arquivo_original = Column(String, nullable=False)
    caminho_armazenamento = Column(String, nullable=False)
    data_upload = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    comentarios = relationship("Comentario", back_populates="documento", cascade="all, delete-orphan")


class Comentario(Base):
    __tablename__ = "comentarios"

    id = Column(Integer, primary_key=True, index=True)
    documento_id = Column(Integer, ForeignKey("documentos.id"), nullable=False)
    texto = Column(Text, nullable=False)
    data_hora_registro = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    documento = relationship("Documento", back_populates="comentarios")