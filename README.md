
**InfinityFree Backupper**

A friendly backupper tool for InfinityFree hosting (Free plan). It automates opening the InfinityFree dashboard in Chrome, helps you sign in, persist cookies, choose an account and MySQL database, export the database SQL, and save a timestamped backup archive.

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
- **Export & zip (always):** Exports the selected database to a SQL file named `<databasename>_<YYYYMMDD-HHMMSS>.sql`, compresses it to a `.zip` placed in `backups/sqls/`, and removes the original `.sql`.
- **FTP mirror & upload (automatic when configured):** If `ftp` credentials are present in `config.json` the tool will automatically download your remote `/htdocs/` into `backups/ftps/htdocs_<timestamp>/`, create a zip `backups/ftps/htdocs_<timestamp>.zip`, remove the extracted folder, and upload the SQL zip to the remote `/htdocs/`.

**Files & Locations**
- **Script:** `infinityfree_backup.py`
- **Examples:** see [config.example.json](config.example.json) and [cookies.example.json](cookies.example.json) for suggested formats you can copy into `config.json` and `cookies.json` locally (these example files are safe to keep in the repo).
- **Generated backups:** SQL dumps are stored under `backups/sqls/`. Each exported `.sql` is compressed into a `.zip` file placed in the same folder and the original `.sql` is removed.
 - **Remote site mirror:** when `ftp` credentials are present the tool downloads your remote `/htdocs/` into `backups/ftps/htdocs_<timestamp>/`, zips it to `backups/ftps/htdocs_<timestamp>.zip`, and removes the extracted folder.

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
		"ftp": {
		"host": "ftp.epizy.com",
		"port": 21,
		"user": "your_ftp_user",
		"password": "YOUR_FTP_PASSWORD",
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

If you'd like, I can also add a short `--upload` CLI flag to enable FTP per-run (so you don't need to edit `config.json`).
