# =======================
# BACKEND FASTAPI COMPLETO
# =======================

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from passlib.context import CryptContext
import shutil
import os

# =======================
# CONFIG
# =======================
DATABASE_URL = "mysql+pymysql://root:1n2n3m4789@localhost/entregas_paquexpress"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================
# MODELOS
# =======================
class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True)
    usr_nombre = Column(String(100))
    usr_password = Column(String(255))

class Paquete(Base):
    __tablename__ = "paquetes"

    id = Column(Integer, primary_key=True, index=True)
    pa_nombre = Column(String(100))
    pa_descripcion = Column(String(255))
    pa_dirOrigen = Column(String(255))
    pa_dirDestino = Column(String(255))
    pa_imagen = Column(String(255))
    status = Column(Enum('asignado','recolectado','entregado'))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))

class Entrega(Base):
    __tablename__ = "entregas"

    id = Column(Integer, primary_key=True, index=True)
    paquete_id = Column(Integer, ForeignKey("paquetes.id"))
    foto = Column(String(255))
    latitud = Column(String(50))
    longitud = Column(String(50))

# =======================
# DB DEPENDENCY
# =======================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =======================
# SEGURIDAD
# =======================
def hash_usr_password(usr_password: str):
    return pwd_context.hash(usr_password)

def verify_usr_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# =======================
# ENDPOINTS
# =======================

# REGISTRO
@app.post("/register")
def register(usr_nombre: str = Form(...), usr_password: str = Form(...), db: Session = Depends(get_db)):
    hashed = hash_usr_password(usr_password)

    user = Usuario(usr_nombre=usr_nombre, usr_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Usuario creado"}

# LOGIN
@app.post("/login")
def login(usr_nombre: str = Form(...), usr_password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.usr_nombre == usr_nombre).first()

    if not user or not verify_usr_password(usr_password, user.usr_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    return {"id": user.id, "nombre": user.usr_nombre}

# OBTENER PAQUETES
@app.get("/paquetes/{user_id}")
def get_paquetes(user_id: int, db: Session = Depends(get_db)):
    paquetes = db.query(Paquete).filter(Paquete.usuario_id == user_id).all()
    return paquetes

# RECOLECTAR
@app.put("/paquete/{id}/recolectar")
def recolectar(id: int, db: Session = Depends(get_db)):
    paquete = db.query(Paquete).get(id)
    paquete.status = "recolectado"
    db.commit()
    return {"message": "Recolectado"}

# ENTREGAR
@app.put("/paquete/{id}/entregar")
def entregar(
    id: int,
    latitud: str = Form(...),
    longitud: str = Form(...),
    foto: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    paquete = db.query(Paquete).get(id)

    # Guardar pa_imagen
    file_path = f"uploads/{foto.filename}"
    os.makedirs("uploads", exist_ok=True)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

    entrega = Entrega(
        paquete_id=id,
        foto=file_path,
        latitud=latitud,
        longitud=longitud
    )

    paquete.status = "entregado"

    db.add(entrega)
    db.commit()

    return {"message": "Entregado correctamente"}

# =======================
# CREAR TABLAS
# =======================
Base.metadata.create_all(bind=engine)
