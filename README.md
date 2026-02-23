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
- 🖥️ Cross-platform (Windows, macOS, Linux)

---

## ⚠️ Important Setup Step

The repository includes:

- `config.example.json`
- `cookies.example.json`

👉 **Before running the tool, rename these files on your system:**

- Rename `config.example.json` → `config.json`
- Rename `cookies.example.json` → `cookies.json`

You can do this using your file explorer (right-click → Rename).

After renaming:

- Edit `config.json` and add your FTP credentials (if needed)
- Replace the contents of `cookies.json` with your real InfinityFree cookie JSON

❗ The script will NOT use the `.example.json` files.  
They must be renamed exactly to:

- `config.json`
- `cookies.json`

---

## 📦 What It Does

### 🗄️ MySQL Backups

- Reads authentication cookies from `cookies.json`
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
# Activate the virtual environment (platform-specific)
pip install -r requirements.txt
````

---

### ▶️ Run

```bash
python infinityfree_backup.py
```

---

## 🔐 Authentication

This tool **does NOT perform interactive sign-in**.

Authentication is cookie-based only.

You must:

* Provide a properly formatted `cookies.json` file
  **or**
* Paste your cookie JSON into the console when prompted

The script will normalize and save cookies for future runs.

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

---

## 🛡 Security & Privacy

* `config.json` and `cookies.json` are excluded via `.gitignore`
* Never commit real credentials
* Rotate secrets immediately if exposed

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
* Scheduling integration (Task Scheduler / cron / systemd)
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
