import os
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.fernet import Fernet

VAULT_DIR = Path.home() / ".auth_vault"
VAULT_DIR.mkdir(parents=True, exist_ok=True)
KEY_FILE = VAULT_DIR / "vault.key"

if not KEY_FILE.exists():
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
else:
    key = KEY_FILE.read_bytes()

cipher = Fernet(key)

app = FastAPI(title="Auth State Vault Server")

class SyncRequest(BaseModel):
    domain: str
    state: dict

@app.post("/sync")
def sync_session(req: SyncRequest):
    data_str = json.dumps(req.state)
    encrypted_data = cipher.encrypt(data_str.encode("utf-8"))
    
    file_path = VAULT_DIR / f"{req.domain}.enc"
    file_path.write_bytes(encrypted_data)
    return {"status": "success", "domain": req.domain, "path": str(file_path)}

@app.get("/retrieve/{domain}")
def retrieve_session(domain: str):
    file_path = VAULT_DIR / f"{domain}.enc"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"No session vault found for domain {domain}")
    
    encrypted_data = file_path.read_bytes()
    decrypted_str = cipher.decrypt(encrypted_data).decode("utf-8")
    return json.loads(decrypted_str)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
