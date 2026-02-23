# InfinityFree Dashboard helper

This script automates opening the InfinityFree dashboard in Chrome, helps you sign in, saves cookies, lists accounts and MySQL databases, and stores your selections for reuse.

Setup

1. Create and activate a virtualenv (recommended).

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the script:

```
python infinityfree_backup.py
```

Behavior

- Opens Chrome and navigates to https://dash.infinityfree.com
- If sign-in is detected, the script asks you to sign in in the opened browser and then to confirm in the console. If you confirm, cookies are saved to `cookies.json` for future runs.
- If no saved cookies are found the script will offer to let you paste cookies JSON or provide a cookies JSON file path; saved cookies are written to `cookies.json` for future runs.
 - The script also checks for a `cookies.txt` file in the script directory. If present and it contains a JSON array of cookies (example format shown below), it will be loaded and persisted to `cookies.json` automatically.

Example `cookies.txt` format:

```
[
	{ "domain": "dash.infinityfree.com", "name": "infinityfree_session", "value": "...", "expirationDate": 1771798174, ... },
	{ "domain": ".infinityfree.com", "name": "esid", "value": "...", ... }
]
```
- The script attempts to locate accounts and prompts you to select one; the selection is saved into `config.json`.
- The script opens the "MySQL Databases" menu (via XPath) and lists database rows; you can pick one to save into `config.json`.

Notes

- XPaths in the script are brittle. If InfinityFree changes its dashboard layout you may need to update the XPaths in `infinityfree_backup.py`.
- Chrome must be installed on your system. `webdriver-manager` will download a matching chromedriver.
- The script runs with a visible browser window so you can interactively sign in.