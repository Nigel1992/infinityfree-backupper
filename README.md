# 🚀 InfinityFree Backupper

> A **local-first backup utility** for exporting MySQL databases from the InfinityFree control panel and mirroring your remote `/htdocs/` directory over FTP — fully automated, timestamped, and compressed.

---

## ✨ Features

- 🔐 **Cookie-based authentication** (no interactive login required)
- 🗄️ Export selected **MySQL databases** as compressed archives
- 🌐 Mirror remote `/htdocs/` via FTP
- 🕒 Automatic **timestamped backups**
- 🗃️ Clean archive structure (raw files removed after compression)
- 💾 Fully local storage (`backups/` directory)

---

## 📦 What It Does

### 🗄️ MySQL Backups

- Reads authentication cookies from `cookies.json` (or pasted JSON)
- Lists available accounts and databases
- Saves your selection to `config.json`
- Exports selected database as:

```

<databasename>_<YYYYMMDD-HHMMSS>.zip

```

- Output location:

```

backups/sqls/

```

> Raw `.sql` files are automatically removed after compression.

---

### 🌐 FTP Mirror

If FTP credentials are present in `config.json`, the tool will:

1. Download `/htdocs/`
2. Store temporarily in:
```

backups/ftps/htdocs_<timestamp>/

```
3. Compress to:
```

backups/ftps/htdocs_<timestamp>.zip

````
4. Remove the extracted folder after archiving

---

## ⚡ Quick Start

### 🛠 Prerequisites

- `python3`
- Google Chrome installed
- `chromedriver`
- Automatically handled via `webdriver-manager`
- OR provide your own compatible version

---

### 🔧 Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

---

### ▶️ Run

```bash
python infinityfree_backup.py
```

---

## 🔐 Authentication (Important)

This tool **does NOT perform interactive sign-in**.

You must authenticate using cookies:

### Option 1 — File (Recommended)

Place a `cookies.json` file in the repository root.

### Option 2 — Paste JSON

Paste cookie JSON directly into the console when prompted.

The script will:

* Normalize cookies
* Save them for future runs

> ⚠️ Never commit real cookies to the repository.

---

## 🗂 Project Structure

```
.
├── infinityfree_backup.py
├── config.example.json
├── cookies.example.json
├── backups/
│   ├── sqls/
│   └── ftps/
```

### 📄 Important Files

| File                     | Description                            |
| ------------------------ | -------------------------------------- |
| `infinityfree_backup.py` | Main script                            |
| `config.example.json`    | Example config (copy to `config.json`) |
| `cookies.example.json`   | Example cookie format                  |

---

## 🛡 Security & Privacy

* `config.json` and `cookies.json` are excluded via `.gitignore`
* Never commit real credentials
* Rotate secrets immediately if exposed
* Consider adding encrypted credential storage (PRs welcome!)

---

## 🧰 Troubleshooting

### 🔍 Selectors Not Working?

InfinityFree dashboard updates may break XPaths.
Update them inside `infinityfree_backup.py`.

### 🧩 ChromeDriver Issues?

* Install a compatible `chromedriver`
* OR let `webdriver-manager` auto-fetch

---

## 🤝 Contributing

Pull requests welcome for:

* Improved XPaths/selectors
* Better headless support
* Encrypted secret storage
* Scheduling integration (cron/systemd)
* Logging improvements
* Multi-account support

---

## 📝 License

Provided as-is. See repository `LICENSE` (if available).

---

## 💡 Philosophy

This project follows a **local-first approach**:

* No cloud uploads
* No external storage dependencies
* Your data stays on your machine

---

If this tool saves you time, feel free to ⭐ the repository!
