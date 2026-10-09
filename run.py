import uvicorn
import os

if __name__ == "__main__":
    print("Iniciando o servidor web CAEd em http://localhost:8000 ...")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
