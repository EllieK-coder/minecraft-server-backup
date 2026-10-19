import argparse
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path

from mcrcon import MCRconException

from mcbackup.rcon import paused_saving
from mcbackup.rotate import find_archives, select_for_deletion

DEFAULT_BACKUP_DIR = Path.home() / "mcbackups"

log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="mcbackup",
        description="Back up a Minecraft world and prune old archives.",
    )
    parser.add_argument("--world", type=Path, required=True,
                        help="world folder to back up")
    parser.add_argument("--backup-dir", type=Path, default=DEFAULT_BACKUP_DIR,
                        help="where archives are written")
    parser.add_argument("--keep", type=int, default=5,
                        help="number of archives to keep (default: 5)")
    parser.add_argument("--dry-run", action="store_true",
                        help="show what would happen without writing or deleting")
    parser.add_argument("--verbose", action="store_true",
                        help="enable debug logging")
    parser.add_argument("--rcon-host", default="127.0.0.1",
                        help="RCON host (default: 127.0.0.1)")
    parser.add_argument("--rcon-password", default=os.environ.get("MCRCON_PASSWORD"),
                        help="RCON password (default: $MCRCON_PASSWORD)")
    parser.add_argument("--rcon-port", type=int, default=25575,
                        help="RCON port (default: 25575)")
    return parser.parse_args()


def setup_logging(backup_dir: Path, verbose: bool) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        handlers=[
            logging.FileHandler(backup_dir / "mcbackup.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main() -> None:
    args = parse_args()
    setup_logging(args.backup_dir, args.verbose)

    if not args.world.is_dir():
        log.error("World folder not found: %s", args.world)
        raise SystemExit(1)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = args.backup_dir / f"world-{stamp}"

    if args.dry_run:
        log.info("Would back up %s to %s.zip", args.world, dest)
    else:
        try:
            if args.rcon_password:
                try:
                    with paused_saving(args.rcon_host, args.rcon_password, args.rcon_port):
                        archive = shutil.make_archive(str(dest), "zip", root_dir=args.world)
                except (ConnectionError, TimeoutError, MCRconException) as exc:
                    log.warning("RCON unavailable (%s) — backing up without pausing saves", exc)
                    archive = shutil.make_archive(str(dest), "zip", root_dir=args.world)
            else:
                log.warning("No RCON password set — backing up without pausing saves")
                archive = shutil.make_archive(str(dest), "zip", root_dir=args.world)
        except OSError:
            log.exception("Backup failed")
            raise SystemExit(1)
        size_mb = Path(archive).stat().st_size / 1_000_000
        log.info("Backed up to %s (%.1f MB)", archive, size_mb)

    doomed = select_for_deletion(find_archives(args.backup_dir), args.keep)
    for path in doomed:
        if args.dry_run:
            log.info("Would delete %s", path.name)
        else:
            path.unlink()
            log.info("Deleted %s", path.name)