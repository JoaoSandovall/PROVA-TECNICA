import os
import shutil
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import engine, Base, get_db
from backend.models import Documento

# criação das tabelas no banco de dados na inicialização
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Gestão de Documentos")

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

@app.post("/api/documentos/", status_code=status.HTTP_201_CREATED)
def upload_documento(
    titulo: str = Form(...),
    descricao: str = Form(None),
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    extensao = os.path.splitext(arquivo.filename)[1].lower()
    if extensao not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de arquivo não permitido. Extensões aceitas: PDF, JPG, PNG."
        )

    nome_arquivo_salvo = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{arquivo.filename}"
    caminho_completo = os.path.join(UPLOAD_DIR, nome_arquivo_salvo)

    try:
        with open(caminho_completo, "wb") as buffer:
            shutil.copyfileobj(arquivo.file, buffer)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Falha ao gravar o arquivo fisicamente no servidor."
        )
    finally:
        arquivo.file.close()

    novo_documento = Documento(
        titulo=titulo,
        descricao=descricao,
        nome_arquivo_original=arquivo.filename,
        caminho_armazenamento=caminho_completo
    )

    db.add(novo_documento)
    db.commit()
    db.refresh(novo_documento)

    return {
        "id": novo_documento.id,
        "titulo": novo_documento.titulo,
        "mensagem": "Upload e registro realizados com sucesso."
    }