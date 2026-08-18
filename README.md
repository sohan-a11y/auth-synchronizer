# Browser Auth-State Synchronizer (`auth-synchronizer`)

![GitHub License](https://img.shields.io/github/license/sohan-a11y/auth-synchronizer?style=flat-square)
![GitHub Last Commit](https://img.shields.io/github/last-commit/sohan-a11y/auth-synchronizer?style=flat-square)
![GitHub Stars](https://img.shields.io/github/stars/sohan-a11y/auth-synchronizer?style=flat-square)

[![Skills](https://skillicons.dev/icons?i=python,js,chrome,fastapi)](https://skillicons.dev)


Export authenticated browser sessions (cookies, `localStorage`, `sessionStorage`) from your human desktop browser via a Manifest V3 extension, encrypt them into a local FastAPI vault, and seamlessly inject them into headless Playwright scripts.

## Setup & Usage

1. Start the FastAPI Vault backend:
```bash
cd backend
pip install -r requirements.txt
python vault_server.py
```

2. Load Chrome Extension:
- Open Chrome and navigate to `chrome://extensions`.
- Enable "Developer mode" (top right toggle).
- Click "Load unpacked" and select the `auth-synchronizer/extension` directory.

3. Sync Session:
- Log in manually to any target website (e.g. ChatGPT, GitHub, internal portal).
- Click the "Auth State Sync" extension icon and click "Sync Active Session".
- Your encrypted session payload is stored securely in `~/.auth_vault/{domain}.enc`.

4. Inject in Playwright:
```python
import asyncio
from backend.playwright_injector import AuthenticatedBrowserContext

async def run():
    injector = AuthenticatedBrowserContext("github.com")
    pw, context = await injector.launch_context(headless=True)
    page = context.pages[0]
    print("Page Title:", await page.title())
    await pw.stop()

asyncio.run(run())
```


---

<div align="center">

**Built by [M Sai Sohan (@sohan-a11y)](https://github.com/sohan-a11y)**

*If you find this project useful, please consider giving it a ⭐ on GitHub!*

</div>
