from fastapi import FastAPI

from backend.api.auth import router as auth_router
from backend.api.sessions import router as sessions_router

from backend.api.reports import router as reports_router
from backend.api.chat import router as chat_router
app = FastAPI(title="AgenticFlow API", version="0.0.1")


app.include_router(auth_router)
app.include_router(sessions_router)
app.include_router(chat_router)
app.include_router(reports_router)

@app.get("/")
def root():
    return {"ok": True, "msg": "AgenticFlow backend running (backend.main)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
    )
