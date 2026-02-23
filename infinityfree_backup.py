import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import zipfile
import ftplib
import getpass

from selenium.webdriver.chrome.webdriver import WebDriver as SeleniumChrome
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import shutil
import os

ROOT = Path(__file__).parent
COOKIES_FILE = ROOT / "cookies.json"
CONFIG_FILE = ROOT / "config.json"
COOKIE_TXT = ROOT / "cookies.txt"


def print_status(msg: str, level: str = "info"):
	ts = time.strftime("%H:%M:%S")
	# ANSI color codes
	RESET = "\033[0m"
	BOLD = "\033[1m"
	COLORS = {
		"info": "\033[94m",
		"ok": "\033[92m",
		"warn": "\033[93m",
		"error": "\033[91m",
		"debug": "\033[90m",
	}
	labels = {"info": "INFO", "ok": "OK", "warn": "WARN", "error": "ERROR", "debug": "DEBUG"}
	# Show debug messages but without the DEBUG tag
	if level == "debug":
		color = COLORS.get("debug", "")
		print(f"{BOLD}[{ts}] {color}{msg}{RESET}")
		return
	label = labels.get(level, level.upper())
	color = COLORS.get(level, "")
	print(f"{BOLD}[{ts}] {color}{label}:{RESET} {msg}")


def save_json(path: Path, data: Any):
	with path.open("w") as f:
		json.dump(data, f, indent=2)


def load_json(path: Path):
	if not path.exists():
		return None
	with path.open() as f:
		return json.load(f)


def start_driver(headless: bool = False, download_dir: Optional[Path] = None):
	options = ChromeOptions()
	if headless:
		options.add_argument("--headless=new")
	options.add_argument("--disable-gpu")
	options.add_argument("--no-sandbox")
	# configure downloads
	if download_dir is None:
		download_dir = ROOT / "downloads"
	download_dir.mkdir(parents=True, exist_ok=True)
	prefs = {
		"download.default_directory": str(download_dir.resolve()),
		"download.prompt_for_download": False,
		"download.directory_upgrade": True,
		"safebrowsing.enabled": True,
	}
	options.add_experimental_option("prefs", prefs)
	# choose chromedriver: prefer webdriver_manager if available, otherwise use system chromedriver
	driver_service = None
	try:
		from webdriver_manager.chrome import ChromeDriverManager
		driver_service = ChromeService(ChromeDriverManager().install())
	except Exception:
		# fallback: look for chromedriver in PATH or use CHROMEDRIVER_PATH env
		chromedriver_path = os.environ.get('CHROMEDRIVER_PATH') or shutil.which('chromedriver')
		if chromedriver_path:
			driver_service = ChromeService(chromedriver_path)
		else:
			raise RuntimeError('Chromedriver not found. Install webdriver-manager or place chromedriver in PATH or set CHROMEDRIVER_PATH.')
	# start driver
	driver = SeleniumChrome(service=driver_service, options=options)
	driver.maximize_window()
	return driver


def apply_cookies(driver: WebDriver, cookies: List[Dict[str, Any]]):
	driver.delete_all_cookies()
	for ck in cookies:
		# normalize common cookie fields to what Selenium expects
		name = ck.get("name")
		value = ck.get("value")
		if name is None or value is None:
			continue
		cookie = {
			"name": name,
			"value": value,
			"path": ck.get("path", "/"),
		}
		if "domain" in ck and ck.get("domain"):
			cookie["domain"] = ck.get("domain")
		# httpOnly / secure
		if "httpOnly" in ck:
			cookie["httpOnly"] = bool(ck.get("httpOnly"))
		if "secure" in ck:
			cookie["secure"] = bool(ck.get("secure"))
					ftp_cfg = cfg.get('ftp')
					if not ftp_cfg:
						print_status('No FTP configuration found; skipping FTP actions.', level='debug')
					else:
						try:
							ftp = ftplib.FTP()
							# validate and coerce FTP host and port to proper types
							host_raw = ftp_cfg.get('host')
							if not host_raw:
								raise ValueError("FTP host is missing in FTP configuration")
							try:
								port = int(ftp_cfg.get('port', 21))
							except Exception:
								port = 21
							ftp.connect(str(host_raw), port, timeout=30)
							# Coerce user/password to strings to avoid passing None to ftplib.login
							user_val = ftp_cfg.get('user') or ''
							pwd_val = ftp_cfg.get('password') or ''
							ftp.login(str(user_val), str(pwd_val))

							# Download remote /htdocs into local ftps folder, zip it, and remove folder
							remote_base = ftp_cfg.get('remote_path') or '/htdocs'
							try:
								# prepare local paths
								ftps_base = base_dir / 'ftps'
								ftps_base.mkdir(parents=True, exist_ok=True)
								htdocs_local = ftps_base / f"htdocs_{ts}"
								htdocs_local.mkdir(parents=True, exist_ok=True)

								def download_ftp_dir(ftp_obj, remote_dir, local_dir):
									# Recursively download a remote FTP directory into local_dir
									try:
										ftp_obj.cwd(remote_dir)
									except Exception:
										return
									items = []
									try:
										items = ftp_obj.nlst()
									except Exception:
										return
									for name in items:
										if name in ('.', '..'):
											continue
										# attempt to cwd into the name to see if it's a directory
										try:
											ftp_obj.cwd(name)
											# it is a directory
											local_sub = local_dir / name
											local_sub.mkdir(parents=True, exist_ok=True)
											# recurse into directory
											download_ftp_dir(ftp_obj, '.', local_sub)
											# go back up
											ftp_obj.cwd('..')
										except Exception:
											# treat as a file, retrieve it
											local_file = local_dir / name
											try:
												with open(local_file, 'wb') as lf:
													ftp_obj.retrbinary(f'RETR {name}', lf.write)
											except Exception:
												# skip unreadable files
												continue

								# start from the configured remote path
								cwd_ok = True
								try:
									ftp.cwd(remote_base)
								except Exception:
									try:
										# try removing leading slash
										ftp.cwd(remote_base.lstrip('/'))
									except Exception:
										cwd_ok = False
								if cwd_ok:
									download_ftp_dir(ftp, '.', htdocs_local)
								# create a zip of the downloaded htdocs folder
								htdocs_zip = ftps_base / f"htdocs_{ts}.zip"
								try:
									with zipfile.ZipFile(htdocs_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
										for root, _, files in os.walk(htdocs_local):
											for fname in files:
												fpath = Path(root) / fname
												arcname = str(fpath.relative_to(ftps_base))
												zf.write(fpath, arcname=arcname)
									print_status(f"Created FTP htdocs zip {htdocs_zip}", level="ok")
									# remove the local extracted folder
									try:
										shutil.rmtree(htdocs_local)
										print_status(f"Removed temporary folder {htdocs_local}", level="debug")
									except Exception:
										pass
								except Exception as e:
									print_status(f"Failed to zip FTP htdocs: {e}", level="warn")
							except Exception as e:
								print_status(f"Failed to download remote htdocs: {e}", level="warn")

							# close FTP connection (no uploads performed)
							try:
								ftp.quit()
							except Exception:
								pass
							print_status("FTP session completed (no uploads performed)", level="debug")
						except Exception as e:
							print_status(f"FTP actions failed: {e}", level="warn")
				dl_dir = ROOT / "downloads"
				val = cfg.get('download_dir')
				if val is not None:
					try:
						if isinstance(val, bytes):
							s = os.fsdecode(val)
						else:
							s = os.fspath(val)
						dl_dir = Path(s)
					except Exception:
						dl_dir = ROOT / "downloads"
				dl_dir.mkdir(parents=True, exist_ok=True)
				before = set(p.name for p in dl_dir.iterdir())
				# click to start export/download
				try:
					go_btn.click()
				except Exception:
					try:
						driver.execute_script("arguments[0].click();", go_btn)
					except Exception:
						print_status("Failed to click export button", level="warn")

				print_status("Waiting for download to finish")
				downloaded = None
				timeout = 120
				start = time.time()
				# ensure we check the configured download directory
				cfg = load_json(CONFIG_FILE) or {}
				dl_dir_val = cfg.get('download_dir')
				if dl_dir_val:
					try:
						dl_dir = Path(str(dl_dir_val))
					except Exception:
						dl_dir = ROOT / "downloads"
				else:
					dl_dir = ROOT / "downloads"
				candidates = {}
				# Wait until we find a new file whose size stabilizes for a few consecutive checks
				samples_needed = 2
				while time.time() - start < timeout:
					# scan directory for candidates and update size history
					for p in dl_dir.iterdir():
						try:
							st = p.stat()
						except Exception:
							continue
						# ignore files obviously present before click unless modified after click
						if p.name in before and st.st_mtime < start:
							continue
						# ignore Chromium helper files
						if p.name.startswith('.com.google.Chrome') or p.name.startswith('._'):
							continue
						key = str(p)
						sz = st.st_size
						prev = candidates.get(key)
						if prev is None:
							# store raw size initially
							candidates[key] = sz
							continue
						# if size hasn't changed for 3 consecutive checks, assume download finished
						if isinstance(prev, tuple):
							last_size, count = prev
							if sz == last_size and sz > 0:
								count += 1
							else:
								count = 1 if sz > 0 else 0
							candidates[key] = (sz, count)
						else:
							# prev is raw size int
							if sz == prev and sz > 0:
								candidates[key] = (sz, 1)
							else:
								candidates[key] = sz
						entry = candidates.get(key)
						if isinstance(entry, tuple) and entry[1] >= samples_needed:
							downloaded = p
							break
					# additionally, if a final .sql file appears and hasn't been modified for >1s, consider it finished
					for p in dl_dir.iterdir():
						try:
							st = p.stat()
						except Exception:
							continue
						if p.suffix.lower() == '.sql' and st.st_size > 0 and st.st_mtime >= start - 2:
							if time.time() - st.st_mtime > 1.0:
								downloaded = p
								break
					if downloaded:
						break
					time.sleep(1)

				# Fallback: if we timed out or missed the file, pick the newest non-temp file
				if not downloaded:
					try:
						recent = []
						for p in dl_dir.iterdir():
							if p.name.startswith('.com.google.Chrome') or p.name.startswith('._'):
								continue
							if p.name.endswith('.crdownload'):
								continue
							try:
								st = p.stat()
							except Exception:
								continue
							# consider files created/modified since we started waiting (or within last 5 minutes)
							if st.st_mtime >= start - 300 and st.st_size > 0:
								recent.append((st.st_mtime, p))
						if recent:
							recent.sort(reverse=True)
							downloaded = recent[0][1]
							print_status(f"Using fallback to detect download: {downloaded}", level="warn")
					except Exception:
						pass

				if downloaded:
					ts = time.strftime('%Y%m%d-%H%M%S')
					# Always use .sql extension for exported databases
					new_name = f"{sel_name}_{ts}.sql"
					# organize into backups/sqls and backups/archives for clarity
					# Coerce config value safely to a Path to avoid passing Optional/Any to Path()
					_dd = cfg.get('download_dir')
					if _dd:
						try:
							base_dir = Path(str(_dd))
						except Exception:
							base_dir = ROOT / 'backups'
					else:
						base_dir = ROOT / 'backups'
					sql_dir = base_dir / 'sqls'
					sql_dir.mkdir(parents=True, exist_ok=True)
					new_path = sql_dir / new_name
					try:
						downloaded.rename(new_path)
						print_status(f"Export saved as {new_path}", level="ok")
					except Exception:
						# fallback: copy if rename fails
						try:
							import shutil
							shutil.copy2(downloaded, new_path)
							print_status(f"Export copied to {new_path}", level="ok")
						except Exception:
							print_status(f"Download finished at {downloaded}", level="ok")

					# Create a zip file containing the SQL and save into the sqls folder
					zip_path = None
					try:
						zip_name = f"{sel_name}_{ts}.zip"
						zip_path = sql_dir / zip_name
						with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
							zf.write(new_path, arcname=new_path.name)
						print_status(f"Created zip {zip_path}", level="ok")
						# remove the original .sql now that it's zipped
						try:
							new_path.unlink()
							print_status(f"Removed original SQL file {new_path}", level="debug")
						except Exception:
							pass
					except Exception as e:
						print_status(f"Failed to create zip: {e}", level="warn")

					# Upload zip to FTP /htdocs/ if FTP config available (FTP now runs when credentials are present)
					cfg = load_json(CONFIG_FILE) or {}
					ftp_cfg = cfg.get('ftp')
					if not ftp_cfg:
						# prompt for FTP details (skip in headless)
						if driver.capabilities.get('headless'):
							print_status("Headless mode: no FTP config provided; skipping FTP actions.", level="warn")
							ftp_cfg = None
						else:
							host = input('FTP host: ').strip()
							port_raw = input('FTP port (press Enter for 21): ').strip()
							port = int(port_raw) if port_raw.isdigit() else 21
							user = input('FTP username: ').strip()
							pwd = getpass.getpass('FTP password: ')
							ftp_cfg = {'host': host, 'port': port, 'user': user, 'password': pwd}
							cfg['ftp'] = ftp_cfg
							save_json(CONFIG_FILE, cfg)

					# attempt upload (if ftp_cfg present and zip exists)
					if ftp_cfg and zip_path and zip_path.exists():
						try:
							ftp = ftplib.FTP()
							# validate and coerce FTP host and port to proper types
							host_raw = ftp_cfg.get('host')
							if not host_raw:
								raise ValueError("FTP host is missing in FTP configuration")
							try:
								port = int(ftp_cfg.get('port', 21))
							except Exception:
								port = 21
							ftp.connect(str(host_raw), port, timeout=30)
							# Coerce user/password to strings to avoid passing None to ftplib.login
							user_val = ftp_cfg.get('user') or ''
							pwd_val = ftp_cfg.get('password') or ''
							ftp.login(str(user_val), str(pwd_val))
							# Optionally download remote /htdocs into local ftps folder, zip it, and remove folder
							remote_base = ftp_cfg.get('remote_path') or '/htdocs'
							# Always download remote /htdocs into local ftps folder when FTP is enabled
							# (previously optional). This ensures a local mirror zip is created.
		
							try:
								# prepare local paths
								ftps_base = base_dir / 'ftps'
								ftps_base.mkdir(parents=True, exist_ok=True)
								htdocs_local = ftps_base / f"htdocs_{ts}"
								htdocs_local.mkdir(parents=True, exist_ok=True)
		
								def download_ftp_dir(ftp_obj, remote_dir, local_dir):
									# Recursively download a remote FTP directory into local_dir
									try:
										ftp_obj.cwd(remote_dir)
									except Exception:
										return
									items = []
									try:
										items = ftp_obj.nlst()
									except Exception:
										return
									for name in items:
										if name in ('.', '..'):
											continue
										# attempt to cwd into the name to see if it's a directory
										try:
											ftp_obj.cwd(name)
											# it is a directory
											local_sub = local_dir / name
											local_sub.mkdir(parents=True, exist_ok=True)
											# recurse into directory
											download_ftp_dir(ftp_obj, '.', local_sub)
											# go back up
											ftp_obj.cwd('..')
										except Exception:
											# treat as a file, retrieve it
											local_file = local_dir / name
											try:
												with open(local_file, 'wb') as lf:
													ftp_obj.retrbinary(f'RETR {name}', lf.write)
											except Exception:
												# skip unreadable files
												continue
		
								# start from the configured remote path
								cwd_ok = True
								try:
									ftp.cwd(remote_base)
								except Exception:
									try:
										# try removing leading slash
										ftp.cwd(remote_base.lstrip('/'))
									except Exception:
										cwd_ok = False
								if cwd_ok:
									download_ftp_dir(ftp, '.', htdocs_local)
								# create a zip of the downloaded htdocs folder
								htdocs_zip = ftps_base / f"htdocs_{ts}.zip"
								try:
									with zipfile.ZipFile(htdocs_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
										for root, _, files in os.walk(htdocs_local):
											for fname in files:
												fpath = Path(root) / fname
												arcname = str(fpath.relative_to(ftps_base))
												zf.write(fpath, arcname=arcname)
									print_status(f"Created FTP htdocs zip {htdocs_zip}", level="ok")
									# remove the local extracted folder
									try:
										# ensure shutil is bound in this scope before use
										import shutil as _shutil
										_shutil.rmtree(htdocs_local)
										print_status(f"Removed temporary folder {htdocs_local}", level="debug")
									except Exception:
										pass
								except Exception as e:
									print_status(f"Failed to zip FTP htdocs: {e}", level="warn")
							except Exception as e:
								print_status(f"Failed to download remote htdocs: {e}", level="warn")

							# change to /htdocs/ creating if necessary for upload
							try:
								ftp.cwd('/htdocs')
							except Exception:
								try:
									ftp.mkd('htdocs')
									ftp.cwd('/htdocs')
								except Exception:
									pass
							# upload zip (from sqls folder)
							with open(zip_path, 'rb') as af:
								ftp.storbinary(f'STOR {zip_path.name}', af)
							ftp.quit()
							print_status(f"Uploaded zip to FTP /htdocs/: {zip_path.name}", level="ok")
						except Exception as e:
							print_status(f"FTP upload failed: {e}", level="warn")
					elif cfg.get('enable_ftp', False) and ftp_cfg:
						# configured to upload but no valid zip to send
						print_status("FTP upload requested but zip not available; skipping upload.", level="warn")
					# if we reach here and downloaded was falsy, report timeout
				else:
					print_status("No download detected within timeout", level="warn")
			else:
				print_status("Could not find export button on Export page", level="warn")
		else:
			print_status("Export tab not found on the page", level="warn")
	except Exception as e:
		print_status(f"Export failed: {e}", level="error")


def main(headless: bool = False):
	# Load config early to avoid prompting for actions already set
	config = load_json(CONFIG_FILE) or {}

	# Determine download directory: prefer saved config, otherwise ask user (headed)
	download_dir = None
	val = config.get('download_dir')
	if val is not None:
		try:
			# accept str, bytes, or os.PathLike: coerce bytes to str and use os.fspath for PathLike to ensure a str is passed to Path
			if isinstance(val, bytes):
				# decode filesystem bytes to str
				s = os.fsdecode(val)
			else:
				# os.fspath returns a str for PathLike[str] or the original str
				s = os.fspath(val)
			download_dir = Path(s)
		except Exception:
			download_dir = None

	if not download_dir:
		if headless:
			# fallback to workspace downloads when headless
			download_dir = None
		else:
			try:
				# prompt user for a folder using a simple Tk file dialog
				import tkinter as tk
				from tkinter import filedialog
				root = tk.Tk()
				root.withdraw()
				path = filedialog.askdirectory(title="Select folder to save exported SQLs")
				root.destroy()
				if path:
					download_dir = Path(path)
					config['download_dir'] = str(download_dir)
					save_json(CONFIG_FILE, config)
					print_status(f"Saved download folder to {CONFIG_FILE}", level="debug")
			except Exception:
				# if GUI not available, continue with default
				download_dir = None

	print_status("Launching Chrome and navigating to https://dash.infinityfree.com", level="debug")
	driver = start_driver(headless=headless, download_dir=download_dir)
	driver.get("https://dash.infinityfree.com")

	# Try to load cookies if they exist. If none, look for cookies.txt (JSON array) or offer paste/file input.
	saved_cookies = load_json(COOKIES_FILE)
	if not saved_cookies and COOKIE_TXT.exists():
		try:
			data = load_json(COOKIE_TXT)
			if data:
				save_json(COOKIES_FILE, data)
				saved_cookies = data
				print_status(f"Loaded cookies from {COOKIE_TXT} and saved to {COOKIES_FILE}", level="debug")
		except Exception as e:
			print_status(f"Failed to load cookies from {COOKIE_TXT}: {e}", level="debug")

	if not saved_cookies:
		print_status("No saved cookies found.", level="debug")
		if headless:
			print_status("Running headless and no cookies are available — proceeding without cookies.", level="debug")
		else:
			want = input("Would you like to paste cookies JSON now or provide a file path? (paste/file/skip): ").strip().lower()
			if want == "file":
				path = input("Enter path to cookies JSON file: ").strip()
				try:
					with open(path, 'r') as f:
						data = json.load(f)
					save_json(COOKIES_FILE, data)
					saved_cookies = data
					print_status(f"Saved cookies to {COOKIES_FILE}", level="debug")
				except Exception as e:
					print_status(f"Failed to load cookies from file: {e}", level="debug")
			elif want == "paste":
				print_status("Paste the cookies JSON now. End with a single line containing only END", level="debug")
				lines = []
				while True:
					try:
						line = input()
					except EOFError:
						break
					if line.strip() == "END":
						break
					lines.append(line)
				raw = "\n".join(lines).strip()
				if raw:
					try:
						data = json.loads(raw)
						save_json(COOKIES_FILE, data)
						saved_cookies = data
						print_status(f"Saved cookies to {COOKIES_FILE}", level="debug")
					except Exception as e:
						print_status(f"Failed to parse pasted cookies JSON: {e}", level="debug")
			else:
				print_status("Continuing without saved cookies; you'll be prompted to sign in if required.", level="debug")
	else:
		try:
			apply_cookies(driver, saved_cookies)
			driver.get("https://dash.infinityfree.com")
			time.sleep(2)
		except Exception:
			print_status("Warning: failed to apply saved cookies", level="debug")

	# Detect login prompt heuristically; if sign-in required and non-headless, wait for user to sign in
	time.sleep(1)
	page_source = driver.page_source.lower()
	if "log in to your account" in page_source or ("log in" in page_source and "email" in page_source):
		print_status("Detected sign-in screen.", level="debug")
		if headless:
			print_status("Headless mode: cannot interact with sign-in. Continuing without signing in.", level="debug")
		else:
			print_status("Please sign in using the opened browser window. Waiting up to 300 seconds for sign-in...", level="debug")
			signed_in = False
			try:
				# wait until accounts are visible or URL changes away from login
				WebDriverWait(driver, 300).until(lambda d: len(list_accounts(d)) > 0 or 'dashboard' in d.current_url.lower())
				signed_in = True
			except Exception:
				signed_in = False
			if signed_in:
				cookies = driver.get_cookies()
				save_json(COOKIES_FILE, cookies)
				print_status(f"Saved cookies to {COOKIES_FILE}", level="debug")
			else:
				print_status("Timed out waiting for sign-in. You can re-run the script to try again.", level="debug")
				driver.quit()
				return

	# List accounts
	print_status("Finding accounts on the dashboard...", level="debug")
	try:
		WebDriverWait(driver, 10).until(lambda d: len(list_accounts(d)) > 0)
	except TimeoutException:
		pass
	accounts = list_accounts(driver)
	config = load_json(CONFIG_FILE) or {}
	# If an account is already saved in config, use it and skip prompting
	if config.get('account') and isinstance(config.get('account'), dict):
		sel = config['account']
		print_status(f"Using saved account: {sel.get('text')}", level="debug")
		if sel.get('href'):
			try:
				driver.get(sel['href'])
				time.sleep(2)
			except Exception:
				pass
	else:
		if not accounts:
			print_status("No accounts found using the configured XPath. The page structure may have changed.", level="debug")
		else:
			print_status("Accounts found:", level="debug")
			for i, acc in enumerate(accounts, start=1):
				print_status(f"{i}: {acc.get('text')}", level="debug")
			choice = input("Select an account number to use (or press Enter to skip): ").strip()
			if choice.isdigit() and 1 <= int(choice) <= len(accounts):
				sel = accounts[int(choice) - 1]
				config['account'] = sel
				save_json(CONFIG_FILE, config)
				print_status(f"Saved selected account to {CONFIG_FILE}", level="debug")
				if sel.get('href'):
					try:
						driver.get(sel['href'])
						time.sleep(2)
					except Exception:
						pass
	# Open MySQL Databases. Prefer navigating to the account's /databases URL when available,
	# otherwise fall back to clicking the configured menu XPath.
	try:
		config = load_json(CONFIG_FILE) or {}
		acct_href = None
		if isinstance(config.get('account'), dict):
			acct_href = config['account'].get('href')
		# If we have an account link, go directly to its /databases page
		if acct_href:
			db_url = acct_href.rstrip('/') + '/databases'
			try:
				driver.get(db_url)
				time.sleep(2)
			except Exception:
				# fallback to clicking menu
				menu_xpath = '//*[@id="manageAccountMenu"]/div/a[7]'
				el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, menu_xpath)))
				el.click()
				time.sleep(2)
		else:
			menu_xpath = '//*[@id="manageAccountMenu"]/div/a[7]'
			el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, menu_xpath)))
			el.click()
			time.sleep(2)
	except Exception:
		print_status("Failed to open MySQL Databases via configured XPath or account URL. You may need to navigate manually.", level="debug")

	# List databases - prefer explicit data-label cells
	try:
		WebDriverWait(driver, 10).until(lambda d: len(get_database_names(d)) > 0)
	except TimeoutException:
		pass
	db_names = get_database_names(driver)

	# If database is already set in config, skip listing and run export automatically
	if config.get('database'):
		sel_name = config['database']
		print_status(f"Using saved database: {sel_name}", level="debug")
		# ensure we're on the databases page for this account
		try:
			cur = driver.current_url
			if '/databases' not in cur:
				if isinstance(config.get('account'), dict) and config['account'].get('href'):
					driver.get(config['account']['href'].rstrip('/') + '/databases')
				else:
					# try to navigate to accounts/<account>/databases
					driver.get(cur.rstrip('/') + '/databases')
				time.sleep(2)
		except Exception:
			pass
		# run export flow
		export_database(driver, sel_name)
		print_status("Done. Keep the browser open if you plan further actions; quitting now.", level="debug")
		driver.quit()
		return

	if not db_names:
		try:
			WebDriverWait(driver, 5).until(lambda d: len(list_databases(d)) > 0)
		except TimeoutException:
			pass
		raw_rows = list_databases(driver)
		db_names = [r.splitlines()[0] for r in raw_rows if r]

	if not db_names:
		print_status("No databases found on the page. The page structure may have changed.", level="debug")
	else:
		print_status("Databases found:", level="debug")
		for i, name in enumerate(db_names, start=1):
			print_status(f"{i}: {name}", level="debug")
		choice = input("Select a database number to use (or press Enter to skip): ").strip()
		config = load_json(CONFIG_FILE) or {}
		if choice.isdigit() and 1 <= int(choice) <= len(db_names):
			sel_name = db_names[int(choice) - 1]
			config['database'] = sel_name
			save_json(CONFIG_FILE, config)
			print_status(f"Saved selected database to {CONFIG_FILE}", level="debug")
			# Navigate to the database-specific URL by appending the db name
			try:
				cur = driver.current_url
				target = cur.rstrip('/') + '/' + sel_name
				print_status(f"Navigating to database page: {target}", level="debug")
				export_database(driver, sel_name)
			except Exception:
				print_status("Failed to navigate to database URL; you may need to open it manually.", level="debug")

	print_status("Done. Keep the browser open if you plan further actions; quitting now.", level="debug")
	driver.quit()


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument('--headless', action='store_true', help='Run Chrome in headless mode')
	args = parser.parse_args()
	main(headless=args.headless)
