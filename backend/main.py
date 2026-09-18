import os
import shutil
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import engine, Base, get_db
from backend.models import Documento, Comentario

# criação das tabelas no banco de dados na inicialização
Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Gestão de Documentos")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "backend/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}

class ComentarioCreate(BaseModel):
    texto: str

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

@app.get("/api/documentos/", status_code=status.HTTP_200_OK)
def listar_documentos(db: Session = Depends(get_db)):
    documentos = db.query(Documento).order_by(Documento.data_upload.desc()).all()
    
    return [
        {
            "id": doc.id,
            "titulo": doc.titulo,
            "descricao": doc.descricao,
            "data_upload": doc.data_upload
        }
        for doc in documentos
    ]

@app.get("/api/documentos/{id}/download", status_code=status.HTTP_200_OK)
def download_documento(id: int, db: Session = Depends(get_db)):
    documento = db.query(Documento).filter(Documento.id == id).first()
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de documento não encontrado."
        )
    
    if not os.path.exists(documento.caminho_armazenamento):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Arquivo físico não localizado no armazenamento do servidor."
        )
        
    return FileResponse(
        path=documento.caminho_armazenamento,
        filename=documento.nome_arquivo_original
    )

@app.post("/api/documentos/{id}/comentarios", status_code=status.HTTP_201_CREATED)
def adicionar_comentario(id: int, payload: ComentarioCreate, db: Session = Depends(get_db)):
    documento = db.query(Documento).filter(Documento.id == id).first()
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de documento não encontrado."
        )
    
    novo_comentario = Comentario(
        documento_id=id,
        texto=payload.texto
    )
    
    db.add(novo_comentario)
    db.commit()
    db.refresh(novo_comentario)
    
    return {
        "id": novo_comentario.id,
        "texto": novo_comentario.texto,
        "data_hora_registro": novo_comentario.data_hora_registro
    }

@app.get("/api/documentos/{id}/comentarios", status_code=status.HTTP_200_OK)
def listar_comentarios(id: int, db: Session = Depends(get_db)):
    documento = db.query(Documento).filter(Documento.id == id).first()
    
    if not documento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de documento não encontrado."
        )
    
    comentarios = db.query(Comentario).filter(Comentario.documento_id == id).order_by(Comentario.data_hora_registro.asc()).all()
    
    return [
        {
            "id": com.id,
            "texto": com.texto,
            "data_hora_registro": com.data_hora_registro
        }
        for com in comentarios
    ]

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")