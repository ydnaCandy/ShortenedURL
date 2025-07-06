from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from datetime import datetime, timedelta
import string, random

app = FastAPI()

# CORSミドルウェアの追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開発中はすべてのオリジンを許可。本番は必要に応じて制限してください
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    # 有効期限
    expires_at = Column(DateTime, nullable=True)

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
    # 有効期限は1週間
    expire_minutes: int = 60 * 24 * 7

# --- 短縮コード生成 ---
def generate_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# --- URL短縮API ---
@app.post("/shorten")
def shorten_url(request: URLRequest, db: Session = Depends(get_db)):
    # 短縮コードの作成
    code = generate_code()
    # 短縮コードが重複しないようにチェック
    while db.query(URL).filter(URL.short_code == code).first():
        code = generate_code()

    # 有効期限を指定（OSはJSTを想定）
    expires_at = datetime.now() + timedelta(minutes=request.expire_minutes)
    
    # 短縮コードを含んだURLを作成
    url = URL(original_url=str(request.url), short_code=code, expires_at=expires_at)
    # URLをデータベースに保存
    db.add(url)
    db.commit()
    return {"short_url": f"http://localhost:8000/{code}"}

# --- リダイレクトAPI ---
@app.get("/{code}")
def redirect_to_url(code: str, db: Session = Depends(get_db)):
    # 短縮URLをデータベースから取得
    url = db.query(URL).filter(URL.short_code == code).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    # 有効期限のチェック
    now_jst = datetime.now()
    if url.expires_at and now_jst > url.expires_at:
        raise HTTPException(status_code=404, detail="URL expired")

    return RedirectResponse(url.original_url)

# --- 削除APIを追加 ---
@app.delete("/del/{code}")
def delete_url(code: str, db: Session = Depends(get_db)):
    url = db.query(URL).filter(URL.short_code == code).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    db.delete(url)
    db.commit()
    return {"message": f"{code} has been deleted."}