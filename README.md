
**InfinityFree Backupper**

A friendly backupper tool for InfinityFree hosting (Free plan). It automates opening the InfinityFree dashboard in Chrome, helps you sign in, persist cookies, choose an account and MySQL database, export and **backup your SQL data**, and optionally mirror your `/htdocs/` folder over FTP — everything is timestamped and zipped for safekeeping.

**Why this exists:** InfinityFree's control panel doesn't provide easy automated scheduled dumps for free accounts. This tool makes repeatable backups simple and local-first — you control where the backups are stored.

**Quick Start**
- **Prerequisites:** `python3`, Chrome installed, and `chromedriver` (the script will prefer `webdriver-manager` to fetch it automatically).
- Create and activate a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Run the backupper (interactive):

```bash
python infinityfree_backup.py
```

**What it does**
- **Interactive sign-in:** Opens Chrome and navigates to https://dash.infinityfree.com. If sign-in is required you can sign in manually; the script will detect completion and save cookies for reuse.
- **Cookie handling:** Accepts pasted cookie JSON or a cookie file and saves normalized cookies locally so future runs can reuse them.
- **Account & DB selection:** Lists available accounts and MySQL databases (using configured XPaths) and lets you pick one. Selections are persisted to `config.json` for convenience.
- **Export & archive:** Exports the selected database to a SQL file named `<databasename>_<YYYYMMDD-HHMMSS>.sql`, then creates a compressed archive for safekeeping.


**Files & Locations**
- **Script:** `infinityfree_backup.py`
- **Examples:** see [config.example.json](config.example.json) and [cookies.example.json](cookies.example.json) for suggested formats you can copy into `config.json` and `cookies.json` locally (these example files are safe to keep in the repo).
- **Generated backups:** SQL dumps are stored under `backups/sqls/` and archives under `backups/archives/` by default.
- **Generated backups:** SQL dumps are stored under `backups/sqls/`. Each exported `.sql` is also compressed into a `.zip` file placed next to the SQL in the same folder (no separate `archives/` folder is used).
- **Remote site mirror (optional):** when enabled the tool can download your remote `/htdocs/` via FTP into a timestamped `backups/ftps/htdocs_<timestamp>/` folder and then compress it into `backups/ftps/htdocs_<timestamp>.zip` (the extracted folder is removed afterwards).

**Config & Cookies (examples)**
- The repository includes example files you should copy and edit locally:

	- [config.example.json](config.example.json) — contains saved selections and optional FTP settings. Copy to `config.json` and edit values you want to persist. Example snippet:

```json
{
	"account_xpath": "//div[@class='account-row']",
	"account_index": 0,
	"database_xpath": "//table[@id='mysql-databases']//tr",
	"database_index": 0,
	"download_dir": "./backups/sqls",
	"enable_ftp": false,
	"ftp": {
		"host": "ftp.epizy.com",
		"user": "your_ftp_user",
		"pass": "YOUR_FTP_PASSWORD",
		"remote_path": "/htdocs/"
	}
}
```

	- [cookies.example.json](cookies.example.json) — shows the JSON array format used for cookie imports. Do **not** commit your real `cookies.json` to the repo; the repository `.gitignore` prevents it from being tracked.

How to load cookies:
- On first run, the script will look for `cookies.json` locally. If not present it offers to:
	- Paste cookie JSON in the console, or
	- Provide a path to a cookie file, or
	- Let you sign in interactively and then save cookies.

**Security & privacy**
- Never commit `config.json` or `cookies.json` containing real secrets. They are excluded from the repository by `.gitignore` and a history purge was performed to remove earlier accidental commits.
- If you think credentials were exposed before the purge, rotate passwords immediately.

**Troubleshooting**
- If the script cannot find accounts or DBs, InfinityFree likely changed the dashboard layout — update the XPaths in `infinityfree_backup.py`.
- If Chrome/Chromedriver mismatch occurs, install a matching chromedriver manually or let `webdriver-manager` fetch one.

**Development & Contribution**
- Pull requests welcome for improved selectors, better headless support, encrypted secrets, or scheduling integration (cron/systemd).

**License**
- This project is provided as-is. See repository LICENSE (if present) for details.

---

