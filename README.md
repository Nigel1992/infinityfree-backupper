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
