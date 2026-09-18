from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "FastAPI running on Vercel"}

# Required for Vercel Serverless Execution
app = app