import json
from pathlib import Path
from cryptography.fernet import Fernet
from playwright.async_api import async_playwright, BrowserContext

VAULT_DIR = Path.home() / ".auth_vault"
KEY_FILE = VAULT_DIR / "vault.key"

class AuthenticatedBrowserContext:
    def __init__(self, domain: str):
        self.domain = domain
        if not KEY_FILE.exists():
            raise RuntimeError("Vault key not found. Sync session via extension first.")
        self.cipher = Fernet(KEY_FILE.read_bytes())

    def get_decrypted_state(self) -> dict:
        file_path = VAULT_DIR / f"{self.domain}.enc"
        if not file_path.exists():
            raise FileNotFoundError(f"No encrypted state file found for domain {self.domain}")
        encrypted_bytes = file_path.read_bytes()
        decrypted_str = self.cipher.decrypt(encrypted_bytes).decode("utf-8")
        return json.loads(decrypted_str)

    async def launch_context(self, headless: bool = True) -> tuple[any, BrowserContext]:
        state = self.get_decrypted_state()
        pw = await async_playwright().start()
        browser = await pw.chromium.launch(headless=headless)
        
        # Convert cookies for Playwright
        pw_cookies = []
        for c in state.get("cookies", []):
            cookie_dict = {
                "name": c["name"],
                "value": c["value"],
                "domain": c["domain"],
                "path": c.get("path", "/"),
                "secure": c.get("secure", False),
                "httpOnly": c.get("httpOnly", False)
            }
            if "sameSite" in c and c["sameSite"] in ["Strict", "Lax", "None"]:
                cookie_dict["sameSite"] = c["sameSite"]
            pw_cookies.append(cookie_dict)

        context = await browser.new_context()
        await context.add_cookies(pw_cookies)

        page = await context.new_page()
        target_url = state.get("url", f"https://{self.domain}")
        await page.goto(target_url, wait_until="domcontentloaded")

        # Inject localStorage and sessionStorage
        l_store = state.get("localStorage", {})
        s_store = state.get("sessionStorage", {})
        
        if l_store or s_store:
            await page.evaluate("""
                ({ lStore, sStore }) => {
                    for (let [k, v] of Object.entries(lStore)) {
                        localStorage.setItem(k, v);
                    }
                    for (let [k, v] of Object.entries(sStore)) {
                        sessionStorage.setItem(k, v);
                    }
                }
            """, {"lStore": l_store, "sStore": s_store})
            
            await page.reload(wait_until="networkidle")

        return pw, context
