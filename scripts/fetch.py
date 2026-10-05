import argparse
from pathlib import Path

from electrical_kaoyan.fetchers import CachedHttpFetcher

parser = argparse.ArgumentParser()
parser.add_argument("url")
parser.add_argument("--cache", type=Path, default=Path(".cache/http"))
parser.add_argument("--refresh", action="store_true")
args = parser.parse_args()
fetcher = CachedHttpFetcher(args.cache, user_agent="electrical-kaoyan-navigator/0.4",
                            delay_seconds=2.0)
print(fetcher.fetch(args.url, refresh=args.refresh))
