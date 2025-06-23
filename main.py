from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import string, random

app = FastAPI()

# --- DB設定 ---
DATABASE_URL = "sqlite:///./urls.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# --- モデル ---
class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)

Base.metadata.create_all(bind=engine)

# --- DBセッションの依存性 ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- リクエストモデル ---
# URLとして受け取る文字列をurl型として定義
class URLRequest(BaseModel):
    url: HttpUrl

# --- 短縮コード生成 ---
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# --- URL短縮API ---
@app.post("/shorten")
def shorten_url(request: URLRequest, db: Session = Depends(get_db)):
    # 短縮コードの佐久市江
    code = generate_code()
    # 短縮コードが重複しないようにチェック
    while db.query(URL).filter(URL.short_code == code).first():
        code = generate_code()
    # 短縮コードを含んだURLを作成
    url = URL(original_url=str(request.url), short_code=code)
    # URLをデータベースに保存
    db.add(url)
    db.commit()
    return {"short_url": f"http://localhost:8000/{code}"}

# --- リダイレクトAPI ---
@app.get("/{code}")
def redirect_to_url(code: str, db: Session = Depends(get_db)):
    # 短縮URLをデータベースから取得
    url = db.query(URL).filter(URL.short_code == code).first()
    if url:
        return RedirectResponse(url.original_url)
    raise HTTPException(status_code=404, detail="URL not found")
