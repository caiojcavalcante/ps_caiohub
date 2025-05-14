## Padrões de Projeto Utilizados

Durante o desenvolvimento do Social Hub com FastAPI e SQLAlchemy, aplicamos de forma natural diversos **padrões de projeto clássicos**. Abaixo estão três deles — um de cada categoria — com exemplos reais do projeto.

---

### 1. Criacional – **Builder**

No Social Hub, usamos o padrão Builder ao transformar dados recebidos (via Pydantic) em objetos de banco de dados complexos. Esse processo é feito passo a passo antes de persistir no banco.

#### Exemplo real:

```python
# services/post.py

def create_post(db: Session, post_data: PostCreate, user_id: int):
    new_post = Post(
        content=post_data.content,
        image_url=post_data.image_url,
        user_id=user_id
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
```

> Aqui, o objeto `Post` é construído parte por parte com base nos dados recebidos — exatamente como define o padrão Builder.

---

### 2. Estrutural – **Facade**

Os arquivos dentro de `services/` funcionam como uma **fachada** (Facade), encapsulando toda a lógica de negócio. As rotas simplesmente chamam funções da camada de serviço, sem se preocupar com a complexidade por trás.

#### Exemplo real:

```python
# routers/posts.py

@router.post("/", response_model=PostResponse)
def create(post_data: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_post(db, post_data, current_user.id)
```

```python
# services/post.py

def create_post(db: Session, post_data: PostCreate, user_id: int):
    ...
```

> A `router` não lida com regras de negócio nem manipulação direta do banco — ela delega tudo para a fachada (`services.post`).

---

### 3. Comportamental – **Strategy**

A autenticação é implementada usando JWT + OAuth2, mas encapsulada em uma função chamada `get_current_user`. Isso permite que a estratégia de autenticação seja trocada no futuro (por sessões, API key, etc) **sem alterar as rotas**.

#### Exemplo real:

```python
# core/security.py

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
```

```python
# dependencies.py

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    token_data = verify_access_token(token)
    return db.query(User).filter(User.id == token_data.id).first()
```

> Toda a lógica de validação de token está encapsulada. Se eu quiser trocar a estratégia de autenticação, posso fazer isso **sem tocar em nenhuma rota**.

---

### ✅ Conclusão

| Categoria       | Padrão     | Aplicado em...                      |
|----------------|------------|-------------------------------------|
| **Criacional** | Builder    | Construção de objetos ORM (`Post`, `User`, etc.) |
| **Estrutural** | Facade     | Arquivos `services/`                |
| **Comportamental** | Strategy | `get_current_user` + OAuth2/JWT    |

Esses padrões ajudaram a manter o projeto limpo, modular e pronto para crescer.

---

## Tecnologias Utilizadas

- **FastAPI** – Framework web moderno e rápido
- **SQLAlchemy** – ORM para interação com banco de dados
- **Pydantic** – Validação de dados com modelos Python
- **SQLite** – Banco de dados leve para desenvolvimento local
- **JWT (via jose)** – Autenticação segura baseada em tokens
- **Passlib** – Hash de senhas com segurança
- **Uvicorn** – ASGI server para rodar o app

---

## Como Rodar o Projeto Localmente

1. Clone o repositório:
```bash
git clone https://github.com/seuusuario/social-hub.git
cd social-hub
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o servidor:
```bash
uvicorn app.main:app --reload
```

5. Acesse o Swagger UI:
```
http://127.0.0.1:8000/docs
```

---

## Estrutura do Projeto

```
app/
├── api/            # Rotas (opcionalmente routers/)
├── models/         # Modelos SQLAlchemy
├── schemas/        # Schemas Pydantic
├── services/       # Camada de negócio
├── core/           # Segurança e configs
├── database.py     # Conexão com banco de dados
├── main.py         # Entrada do app
```

---

## Autor

Desenvolvido por Caio Daniel de Jesus Cavalcante.  
Projeto de Software – UFAL.