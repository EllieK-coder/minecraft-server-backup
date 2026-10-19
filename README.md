# Minecraft Server Backup

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Release](https://img.shields.io/github/v/release/EllieK-coder/minecraft-server-backup)

A Python command-line tool that creates safe, consistent backups of a Minecraft server world and automatically rotates old archives so disk usage stays under control.

Built for modded (Forge) servers, where worlds get large and a corrupted save can mean losing weeks of progress.

## Why

Copying a world folder while the server is running can produce a broken backup, because the game may be writing chunks to disk at the same time. This tool talks to the server over **RCON** to pause autosaving and flush everything to disk first. Then it archives the world and turns saving back on.

## Features

- **Consistent snapshots**: pauses saves over RCON (`save-off` → `save-all flush` → archive → `save-on`)
- **Guaranteed recovery**: `save-on` runs in a `finally` block, so saving is always resumed even if the backup fails
- **Graceful fallback**: if RCON is unreachable, times out, or the password is wrong, the backup still runs and logs a warning
- **Timestamped zip archives** of the world folder
- **Backup rotation**: keeps the N most recent archives and deletes older ones automatically
- **Dry-run mode** to preview what would be created and deleted
- **Logging** to both the console and `mcbackup.log`
- **Installable CLI**: one `mcbackup` command built with `argparse`, packaged with a `pyproject.toml` entry point
- **Tested** with `pytest`, including mocked RCON tests that need no running server

## How it works

```
mcbackup
  ├─ connect to the server over RCON
  ├─ save-off, then save-all flush        ← world is now static on disk
  ├─ zip the world folder → world-YYYYMMDD-HHMMSS.zip
  ├─ save-on                              ← always runs, even on failure
  └─ delete archives beyond --keep
```

## Requirements

- Python 3.11+
- A Minecraft server with RCON enabled. In `server.properties`:
  ```
  enable-rcon=true
  rcon.port=25575
  rcon.password=your-rcon-password
  ```

## Installation

```bash
git clone https://github.com/EllieK-coder/minecraft-server-backup.git
cd minecraft-server-backup
pip install -e .
```

## Usage

```bash
# set the RCON password once (PowerShell)
$env:MCRCON_PASSWORD = "your-rcon-password"

# back up the world, keep the 7 most recent archives
mcbackup --world "C:/servers/my-server/world" --backup-dir "D:/backups" --keep 7

# preview what would be created and deleted, without touching anything
mcbackup --world "C:/servers/my-server/world" --dry-run
```

| Option            | Description                                              |
|-------------------|----------------------------------------------------------|
| `--world`         | Path to the server's world folder (required)             |
| `--backup-dir`    | Where archives are written (default: `~/mcbackups`)      |
| `--keep`          | Number of archives to keep (default: 5)                  |
| `--dry-run`       | Show what would happen without writing or deleting       |
| `--verbose`       | Enable debug logging                                     |
| `--rcon-host`     | RCON host (default: `127.0.0.1`)                         |
| `--rcon-port`     | RCON port (default: `25575`)                             |
| `--rcon-password` | RCON password (default: `$MCRCON_PASSWORD`)              |

The password is read from the `MCRCON_PASSWORD` environment variable by default, so it doesn't end up in your shell history or scheduled task definitions.

### Scheduling

To run backups automatically, schedule `mcbackup` with **Task Scheduler** (Windows) or **cron** (Linux). For example, a nightly cron job:

```
0 4 * * * MCRCON_PASSWORD=secret mcbackup --world /srv/minecraft/world --keep 7
```

## Project structure

```
src/mcbackup/
  cli.py        # argument parsing, logging setup, backup flow
  rcon.py       # paused_saving() context manager around RCON commands
  rotate.py     # finding archives and choosing which to delete
tests/          # pytest suite
pyproject.toml  # packaging and dependencies (hatchling)
```

## Running tests

```bash
pip install pytest
pytest
```

## Roadmap

**v1.0.0 (released)**
- [x] Archive the world folder
- [x] RCON save pausing with guaranteed resume
- [x] Fallback when RCON is unavailable
- [x] Rotation of old backups
- [x] Dry-run mode and logging
- [x] Test suite, including mocked RCON tests

**Ideas for later**
- [ ] Config file support (e.g. `mcbackup.toml`)
- [ ] Back up multiple worlds or dimensions in one run
- [ ] Optional upload to cloud storage

## Tech stack

Python · argparse · RCON (`mcrcon`) · pytest · hatchling
