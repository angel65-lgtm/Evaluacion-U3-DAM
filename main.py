from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

# Inicializa la aplicación FastAPI
app = FastAPI()

# Monta la carpeta "uploads" como ruta accesible públicamente desde el navegador
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Configura el middleware CORS para permitir peticiones desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define la cadena de conexión a la base de datos MySQL
DATABASE_URL = "mysql+pymysql://root:1n2n3m4789@localhost/db_practica10"

# Crea el motor de conexión a la base de datos usando SQLAlchemy
engine = create_engine(DATABASE_URL)

# Crea una clase de sesión que se usará para interactuar con la base de datos
SessionLocal = sessionmaker(bind=engine)

# Define una base común para los modelos de base de datos
Base = declarative_base()

# Define el modelo de datos que representa la tabla 'PT8_foto'
class Foto(Base):
    __tablename__ = "PT8_foto"
    
    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(255), nullable=False)
    ruta_foto = Column(String(255), nullable=False)
    fecha = Column(TIMESTAMP, default=datetime.utcnow)

# Crea las tablas en la base de datos si no existen
Base.metadata.create_all(bind=engine)

# Define un esquema de validación y serialización usando Pydantic
class FotoSchema(BaseModel):
    id: int
    descripcion: str
    ruta_foto: str
    fecha: Optional[datetime]

    class Config:
        from_attributes = True

# Define el endpoint POST para subir una foto
@app.post("/fotos/")
async def subir_foto(descripcion: str = Form(...), file: UploadFile = File(...)):
    db = SessionLocal()
    try:
        ruta = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(ruta, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        nueva_foto = Foto(descripcion=descripcion, ruta_foto=ruta)
        
        db.add(nueva_foto)
        db.commit()
        db.refresh(nueva_foto)
        
        return {
            "msg": "Foto subida correctamente",
            "foto": FotoSchema.from_orm(nueva_foto)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        db.close()

@app.get("/fotos/")
def listar_fotos():
    try:
        db = SessionLocal()
        fotos = db.query(Foto).all()
        db.close()
        return [FotoSchema.from_orm(f) for f in fotos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        db.close()