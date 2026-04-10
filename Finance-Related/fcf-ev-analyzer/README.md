# FCF/EV Analyzer — Run Locally

## What you need
- **Node.js** (v18+) — https://nodejs.org
- **Anthropic API key** — free at https://console.anthropic.com

---

## 4-step setup

### 1. Check Node is installed
```
node --version
```
Should print `v18.x.x` or higher. If not, install from nodejs.org first.

### 2. Add your API key
Copy `.env.example` → `.env` and paste your key:
```
# Mac/Linux
cp .env.example .env

# Windows
copy .env.example .env
```
Open `.env` in any text editor:
```
ANTHROPIC_API_KEY=sk-ant-...your real key here...
```

### 3. Install dependencies (once)
```
npm install
```

### 4. Run it
```
npm run dev
```
Then open **http://localhost:3000** in your browser.

---

## How it works
```
Browser → /api/messages → Express server.js → api.anthropic.com
```
Browsers block direct Anthropic API calls (CORS). Express sits in the
middle on the same machine — no CORS issue, your key stays server-side.

## Troubleshooting
| Error | Fix |
|---|---|
| `node: command not found` | Install Node from nodejs.org |
| `Cannot find module` | Run `npm install` |
| `API key not set` | Check your `.env` file exists |
| Port in use | Edit ports in `server.js` / `vite.config.js` |
