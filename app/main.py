from fastapi import FastAPI

app = FastAPI(title="FX Meta Backend")

@app.get("/health")
async def health():
    return {"status": "ok"}