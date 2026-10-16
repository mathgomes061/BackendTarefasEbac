from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets

from sqlalchemy import (
    create_engine,
    select,
    func,
    UniqueConstraint
)
from sqlalchemy.orm import (
    sessionmaker,
    DeclarativeBase,
    Session,
    Mapped,
    mapped_column
)
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "sqlite:///./tarefas.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

MEU_USUARIO = "admin"
MINHA_SENHA = "admin"

security = HTTPBasic()


class Base(DeclarativeBase):
    pass


class TarefaBD(Base):
    __tablename__ = "Tarefas"

    __table_args__ = (
        UniqueConstraint(
            "nome",
            name="uq_nome"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(index=True)
    descricao: Mapped[str] = mapped_column(index=True)
    concluida: Mapped[bool] = mapped_column()


class Tarefa(BaseModel):
    nome: str
    descricao: str
    concluida: bool = False


class TarefaAtualizacao(BaseModel):
    concluida: bool


class TarefaResponse(BaseModel):
    nome_tarefa: str
    descricao_tarefa: str
    tarefa_concluida: bool


class ListaTarefaResponse(BaseModel):
    page: int
    size: int
    total: int
    tarefas: list[TarefaResponse]


class MensagemResponse(BaseModel):
    mensagem: str


Base.metadata.create_all(bind=engine)


def get_session_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def autenticar_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = secrets.compare_digest(
        credentials.username, MEU_USUARIO
    )
    is_password_correct = secrets.compare_digest(
        credentials.password, MINHA_SENHA
    )

    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=401,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Basic"}
        )


@app.post("/adicionar", response_model=MensagemResponse)
def post_tarefa(
    tarefa: Tarefa,
    db: Session = Depends(get_session_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario)
):
    try:
        stmt = select(TarefaBD).where(
            TarefaBD.nome == tarefa.nome
        )

        db_tarefa = db.scalars(stmt).first()

        if db_tarefa:
            raise HTTPException(
                    status_code=400,
                    detail="Tarefa já existe na lista."
                )

        nova_tarefa = TarefaBD(
            nome=tarefa.nome,
            descricao=tarefa.descricao,
            concluida=tarefa.concluida
        )

        db.add(nova_tarefa)
        db.commit()
        db.refresh(nova_tarefa)

    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao salvar a tarefa no banco de dados."
        )

    return {
        "mensagem": "Tarefa adicionada com sucesso.",
    }


@app.get("/tarefas", response_model=ListaTarefaResponse)
def get_tarefas(
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_session_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario),
    ordena: Optional[str] = None
):
    if page < 1 or size < 1:
        raise HTTPException(
            status_code=400,
            detail="Página ou limites não podem ser menores que 1"
        )

    stmt = select(TarefaBD)

    if ordena:
        if ordena not in ["nome", "descricao", "concluida"]:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Não é possível ordenar pelo campo '{ordena}'. "
                    "Escolha entre: nome, descricao ou concluida."
                )
            )

        stmt = stmt.order_by(getattr(TarefaBD, ordena))

    stmt = (
        stmt
        .offset((page - 1) * size)
        .limit(size)
    )

    try:
        tarefas = db.scalars(stmt).all()

        total_tarefas = db.scalar(
            select(func.count()).select_from(TarefaBD)
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Erro ao consultar banco de dados."
        )

    if not tarefas:
        return {
            "page": page,
            "size": size,
            "total": 0,
            "tarefas": []
        }

    return {
        "page": page,
        "size": size,
        "total": total_tarefas,
        "tarefas": [
            {
                "nome_tarefa": tarefa.nome,
                "descricao_tarefa": tarefa.descricao,
                "tarefa_concluida": tarefa.concluida
            }
            for tarefa in tarefas
        ]
    }


@app.put("/atualizar/{nome}", response_model=MensagemResponse)
def put_tarefa(
    nome: str,
    atualizacao: TarefaAtualizacao,
    db: Session = Depends(get_session_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario)
):
    try:
        stmt = select(TarefaBD).where(TarefaBD.nome == nome)

        db_tarefa = db.scalars(stmt).first()

        if not db_tarefa:
            raise HTTPException(
                status_code=404,
                detail="Tarefa não encontrada."
            )

        db_tarefa.concluida = atualizacao.concluida
        db.commit()
        db.refresh(db_tarefa)

    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao atualizar a tarefa no banco de dados."
        )

    return {
        "mensagem": f"Tarefa '{db_tarefa.nome}' atualizada com sucesso!"
    }


@app.delete("/deletar/{nome}", response_model=MensagemResponse)
def delete_tarefa(
    nome: str,
    db: Session = Depends(get_session_db),
    credentials: HTTPBasicCredentials = Depends(autenticar_usuario)
):
    try:
        stmt = select(TarefaBD).where(TarefaBD.nome == nome)

        db_tarefa = db.scalars(stmt).first()

        if not db_tarefa:
            raise HTTPException(
                    status_code=404,
                    detail="Tarefa não encontrada na lista."
                )

        nome_tarefa = db_tarefa.nome

        db.delete(db_tarefa)
        db.commit()

    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao deletar a tarefa no banco de dados."
        )

    return {
        "mensagem": f"Tarefa '{nome_tarefa}' deletada com sucesso!"
    }
