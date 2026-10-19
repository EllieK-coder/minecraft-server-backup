# Minecraft Server Backup

A Python command-line tool that creates safe, consistent backups of a Minecraft server world and automatically rotates old archives so disk usage stays under control.

Built for modded (Forge) servers, where worlds get large and a corrupted save can mean losing weeks of progress.

## Why

Copying a world folder while the server is running can produce a broken backup, because the game may be writing chunks to disk at the same time. This tool talks to the server over **RCON** to pause autosaving and flush everything to disk first. Then it archives the world and turns saving back on.

## Features

- **Consistent snapshots**: uses RCON (`save-off` → `save-all` → `save-on`) so the world isn't being written to mid-backup
- **Compressed, timestamped archives** of the world folder
- **Backup rotation**: keeps the N most recent backups and deletes older ones automatically
- **Installable CLI**: one `mcbackup` command built with `argparse`, packaged with a `pyproject.toml` entry point
- **Logging** of each backup run
- **Tested** with `pytest`

- **Dry-run mode** to preview what would be created and deleted

## Requirements

- Python 3.11+
- A Minecraft server with RCON enabled (`enable-rcon=true` in `server.properties`)

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
| `--rcon-password` | RCON password (default: `$MCRCON_PASSWORD`)              |

If no RCON password is set, or the server can't be reached, the backup still runs. You'll see a warning that saves weren't paused.

Each run is logged to `mcbackup.log` in the backup folder.

### Scheduling

To run backups automatically, schedule `mcbackup` with **Task Scheduler** (Windows) or **cron** (Linux).

## Project structure

```
src/mcbackup/   # package source (CLI entry point: mcbackup.cli:main)
tests/          # pytest test suite
pyproject.toml  # packaging and dependencies (hatchling)
```

## Running tests

```bash
pip install pytest
pytest
```

## Roadmap

- [x] Project skeleton and argparse CLI
- [x] Archive the world folder
- [x] Rotation of old backups
- [x] Logging
- [x] Test suite
- [x] RCON save-off / save-all / save-on around the backup
- [x] Dry-run mode
- [ ] Configurable RCON port
- [ ] Tests for the RCON flow
- [ ] Config file support

## Tech stack

Python · RCON (`mcrcon`) · pytest · hatchling
