
**InfinityFree Backupper**

A friendly backupper tool for InfinityFree hosting (Free plan). It automates opening the InfinityFree dashboard in Chrome, helps you sign in, persist cookies, choose an account and MySQL database, export and **backup your SQL data**, and optionally mirror your `/htdocs/` folder over FTP — everything is timestamped and zipped for safekeeping.

**Why this exists:** InfinityFree's control panel doesn't provide easy automated scheduled dumps for free accounts. This tool makes repeatable backups simple and local-first — you control where the backups are stored.

**Quick Start**
- **Prerequisites:** `python3`, Chrome installed, and `chromedriver` (the script will prefer `webdriver-manager` to fetch it automatically).
- Create and activate a virtual environment and install dependencies:

````markdown

**InfinityFree Backupper**

Small utility to export MySQL databases from the InfinityFree control panel and mirror the remote `/htdocs/` folder over FTP. The tool is local-first: it saves timestamped, compressed backups under `backups/` for your convenience.

**Quick Start**
- **Prerequisites:** `python3` and Chrome installed. The script prefers `webdriver-manager` to fetch a matching `chromedriver`, but a system `chromedriver` also works.
- Create and activate a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Run the backupper:

```bash
python infinityfree_backup.py
```

**Important usage notes**
- This tool does NOT perform interactive sign-in. Authentication is cookie-based only: provide a `cookies.json` file or paste cookie JSON into the console. The script will normalize and persist cookies for future runs.
- The tool always exports the selected MySQL database to a timestamped SQL file and creates a compressed ZIP of the export.
- The tool always mirrors the remote `/htdocs/` directory via FTP when valid FTP credentials are present in your `config.json` (the mirrored site is compressed to a ZIP and the extracted folder is removed after archiving).
- There is no upload functionality in this project.

**What it does**
- Reads cookie data from `cookies.json` (or pasted JSON) to authenticate.
- Lists accounts and MySQL databases (using configured XPaths) so you can select which database to export. Selections are saved to `config.json`.
- Exports the selected database into `backups/sqls/` as `<databasename>_<YYYYMMDD-HHMMSS>.sql`, then creates a `.zip` archive and removes the raw `.sql` file.
- If FTP credentials are present in `config.json`, downloads the remote `/htdocs/` into `backups/ftps/htdocs_<timestamp>/`, compresses it to `backups/ftps/htdocs_<timestamp>.zip`, and removes the extracted folder.

**Files & Locations**
- `infinityfree_backup.py` — main script.
- `config.example.json` and `cookies.example.json` — safe examples you can copy to `config.json` and `cookies.json` locally.
- Backups:
  - `backups/sqls/` — contains zipped SQL exports (each export is a `.zip` file; original `.sql` files are removed after archiving).
  - `backups/ftps/` — contains zipped mirrors of remote `/htdocs/` named `htdocs_<timestamp>.zip`.

**Config & Cookies (examples)**
- Copy and edit the included examples locally:

  - [config.example.json](config.example.json) — configure saved selections and FTP credentials. Copy to `config.json` locally and edit values before running.

  - [cookies.example.json](cookies.example.json) — shows the JSON array format used for cookie imports. Do **not** commit your real `cookies.json` to the repo; the repository `.gitignore` prevents it from being tracked.

How to provide cookies:
- Place a `cookies.json` file in the repository root (ignored by git), or paste the cookie JSON when the script prompts; the script will save normalized cookies for subsequent runs.

**Security & privacy**
- Never commit `config.json` or `cookies.json` containing real secrets. They are excluded from the repository by `.gitignore`. If secrets were exposed previously, rotate them immediately.

**Troubleshooting**
- If account or DB selectors stop working, update the XPaths in `infinityfree_backup.py` to match the dashboard's current markup.
- For Chrome/Chromedriver mismatches, install a compatible `chromedriver` or let `webdriver-manager` fetch one.

**Development & Contribution**
- PRs welcome for improved selectors, encrypted credential support, or scheduling integrations.

**License**
- This project is provided as-is. See repository LICENSE (if present) for details.

````
- Pull requests welcome for improved selectors, better headless support, encrypted secrets, or scheduling integration (cron/systemd).


