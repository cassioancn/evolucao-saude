from datetime import datetime, date
import hashlib
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime, Time, Text, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from database.connection import Base, get_engine, get_db

def hash_senha(senha: str) -> str:
    """Gera hash SHA-256 seguro para as senhas."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    login = Column(String(50), unique=True, index=True, nullable=False)
    senha_hash = Column(String(128), nullable=False)
    role = Column(String(20), default="bruna")  # 'bruna', 'admin'
    criado_em = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    metas = relationship("ConfiguracaoMeta", back_populates="usuario", cascade="all, delete-orphan")
    pesagens = relationship("Pesagem", back_populates="usuario", cascade="all, delete-orphan")
    medidas = relationship("MedidaCorporal", back_populates="usuario", cascade="all, delete-orphan")
    habitos = relationship("HabitoDiario", back_populates="usuario", cascade="all, delete-orphan")
    fotos = relationship("FotoEvolucao", back_populates="usuario", cascade="all, delete-orphan")

class ConfiguracaoMeta(Base):
    __tablename__ = "configuracao_metas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, unique=True)
    altura_cm = Column(Float, nullable=False, default=165.0)
    peso_inicial = Column(Float, nullable=False, default=70.0)
    meta_peso = Column(Float, nullable=False, default=60.0)
    data_inicio = Column(Date, nullable=False, default=date.today)
    data_alvo = Column(Date, nullable=True)
    calorias_diarias_meta = Column(Integer, nullable=True, default=1600)
    meta_agua_ml = Column(Integer, default=2500)
    idade = Column(Integer, nullable=True, default=30)
    sexo = Column(String(20), nullable=True, default="Feminino")
    nivel_atividade = Column(String(100), nullable=True, default="Moderadamente Ativo (3 a 5 dias/sem)")
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="metas")

class Pesagem(Base):
    __tablename__ = "pesagens"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_pesagem = Column(Date, nullable=False, index=True)
    peso = Column(Float, nullable=False)
    
    # Métricas de Bioimpedância (OKOK Scale)
    percentual_gordura = Column(Float, nullable=True)    # % BF
    massa_muscular_kg = Column(Float, nullable=True)     # Músculo em kg ou %
    percentual_agua = Column(Float, nullable=True)        # % Água
    gordura_visceral = Column(Integer, nullable=True)     # Nível visceral (1-50)
    tmb = Column(Integer, nullable=True)                  # Taxa metabólica basal kcal
    idade_metabolica = Column(Integer, nullable=True)
    
    origem = Column(String(50), default="manual")        # 'manual', 'print_okok', 'csv'
    notas = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="pesagens")

class MedidaCorporal(Base):
    __tablename__ = "medidas_corporais"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_registro = Column(Date, nullable=False, index=True)
    
    cintura = Column(Float, nullable=True)        # cm
    abdomen = Column(Float, nullable=True)        # cm
    quadril = Column(Float, nullable=True)        # cm
    coxa_dir = Column(Float, nullable=True)       # cm
    coxa_esq = Column(Float, nullable=True)       # cm
    braco_dir = Column(Float, nullable=True)      # cm
    braco_esq = Column(Float, nullable=True)      # cm
    busto = Column(Float, nullable=True)          # cm
    pescoco = Column(Float, nullable=True)        # cm
    
    notas = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="medidas")

class HabitoDiario(Base):
    __tablename__ = "habitos_diarios"
    __table_args__ = (UniqueConstraint('usuario_id', 'data', name='uq_usuario_data_habito'),)

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data = Column(Date, nullable=False, index=True)
    
    agua_ml = Column(Integer, default=0)
    treinou = Column(Boolean, default=False)
    tipo_treino = Column(String(100), nullable=True)      # 'Musculação', 'Cardio', 'Pilates', etc.
    sono_horas = Column(Float, default=7.0)
    qualidade_sono = Column(Integer, default=3)           # 1 a 5 estrelas
    ciclo_menstrual = Column(Boolean, default=False)       # Sim/Não
    fase_ciclo = Column(String(50), nullable=True)        # 'Menstruação', 'Folicular', 'Ovulação', 'Lútea/TPM'
    humor = Column(String(50), default="bem")             # 'Excelente', 'Bem', 'Neutro', 'Cansada', 'Ansiosa'
    notas = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="habitos")

class FotoEvolucao(Base):
    __tablename__ = "fotos_evolucao"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    data_foto = Column(Date, nullable=False, index=True)
    tipo = Column(String(50), default="frente")           # 'frente', 'lado', 'costas'
    caminho_arquivo = Column(String(255), nullable=False)
    peso_no_dia = Column(Float, nullable=True)
    notas = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

    usuario = relationship("Usuario", back_populates="fotos")

def init_db():
    """Cria todas as tabelas no banco de dados e inicializa os usuários padrão."""
    from sqlalchemy import text
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    # Migração automática de colunas para PostgreSQL Neon
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE configuracao_metas ADD COLUMN IF NOT EXISTS idade INTEGER DEFAULT 30;"))
            conn.execute(text("ALTER TABLE configuracao_metas ADD COLUMN IF NOT EXISTS sexo VARCHAR(20) DEFAULT 'Feminino';"))
            conn.execute(text("ALTER TABLE configuracao_metas ADD COLUMN IF NOT EXISTS nivel_atividade VARCHAR(100) DEFAULT 'Moderadamente Ativo (3 a 5 dias/sem)';"))
            conn.commit()
    except Exception as e:
        print(f"Aviso na migração de colunas: {e}")
    
    with get_db() as db:
        # Usuário Bruna
        bruna = db.query(Usuario).filter(Usuario.login == "bruna").first()
        if not bruna:
            bruna = Usuario(
                nome="Bruna",
                login="bruna",
                senha_hash=hash_senha("bruna123"),
                role="bruna"
            )
            db.add(bruna)
            db.flush()
            
            # Meta inicial para a Bruna
            meta = ConfiguracaoMeta(
                usuario_id=bruna.id,
                altura_cm=165.0,
                peso_inicial=72.0,
                meta_peso=62.0,
                data_inicio=date.today(),
                meta_agua_ml=2500,
                idade=30,
                sexo="Feminino",
                nivel_atividade="Moderadamente Ativo (3 a 5 dias/sem)"
            )
            db.add(meta)
        
        # Usuário Cássio (Admin)
        cassio = db.query(Usuario).filter(Usuario.login == "cassio").first()
        if not cassio:
            cassio = Usuario(
                nome="Cássio",
                login="cassio",
                senha_hash=hash_senha("admin123"),
                role="admin"
            )
            db.add(cassio)
            db.flush()

            meta_c = ConfiguracaoMeta(
                usuario_id=cassio.id,
                altura_cm=178.0,
                peso_inicial=80.0,
                meta_peso=75.0,
                data_inicio=date.today(),
                meta_agua_ml=3000,
                idade=33,
                sexo="Masculino",
                nivel_atividade="Moderadamente Ativo (3 a 5 dias/sem)"
            )
            db.add(meta_c)

