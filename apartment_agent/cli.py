from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .matching import score_listing
from .outreach import draft_message
from .requirements_io import load_requirements
from .sources import build_source
from .storage import Store


def cmd_run(args: argparse.Namespace) -> int:
    req = load_requirements(args.requirements)
    out_dir = Path(args.out)
    drafts_dir = out_dir / "drafts"
    drafts_dir.mkdir(parents=True, exist_ok=True)

    store = Store(args.db)
    new_count = 0
    for spec in args.sources.split(","):
        spec = spec.strip()
        try:
            source = build_source(spec)
            found = source.search(args.area)
        except Exception as exc:  # one bad source shouldn't kill the run
            print(f"[warn] source '{spec}' failed: {exc}", file=sys.stderr)
            continue
        for listing in found:
            if store.upsert(listing):
                new_count += 1

    matched, rejected = [], []
    for listing in store.list(status="new"):
        result = score_listing(listing, req)
        store.update_score(listing.id, result.score)
        if result.passes:
            draft = draft_message(listing, req, your_name=args.your_name)
            (drafts_dir / f"{listing.id.replace(':', '_')}.txt").write_text(draft)
            store.update_status(listing.id, "drafted")
            matched.append(result)
        else:
            store.update_status(listing.id, "rejected")
            rejected.append(result)

    report = {
        "area": args.area,
        "new_listings_found": new_count,
        "matched": [
            {
                "id": r.listing.id,
                "title": r.listing.title,
                "source": r.listing.source,
                "price": r.listing.price,
                "url": r.listing.url,
                "score": round(r.score, 3),
                "reasons": r.matched_reasons,
                "draft_file": str(drafts_dir / f"{r.listing.id.replace(':', '_')}.txt"),
            }
            for r in matched
        ],
        "rejected": [
            {"id": r.listing.id, "title": r.listing.title, "reasons": r.failed_reasons}
            for r in rejected
        ],
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=2))

    print(f"Found {new_count} new listing(s) for '{args.area}'.")
    print(f"{len(matched)} matched your requirements -- drafts written to {drafts_dir}/")
    for r in matched:
        print(f"  [{r.score:.2f}] {r.listing.title} (${r.listing.price if r.listing.price else '?'}) -> {r.listing.url or 'no url'}")
    print(f"{len(rejected)} rejected. See {out_dir / 'report.json'} for reasons.")
    store.close()
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    store = Store(args.db)
    for listing in store.list(status=args.status):
        print(f"{listing.id}\t{listing.title}\t${listing.price}\t{listing.url or ''}")
    store.close()
    return 0


def cmd_mark(args: argparse.Namespace) -> int:
    store = Store(args.db)
    store.update_status(args.listing_id, args.status)
    store.close()
    print(f"Marked {args.listing_id} as {args.status}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="apartment_agent", description="Search, match, and draft apartment inquiries.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Search sources, match requirements, and write draft inquiries.")
    p_run.add_argument("--area", required=True, help='Area to search, e.g. "Austin, TX" or a zip code')
    p_run.add_argument("--requirements", required=True, help="Path to a requirements JSON file")
    p_run.add_argument("--sources", default="mock", help="Comma-separated source specs, e.g. mock,csv:sample_data/listings.csv,craigslist:austin")
    p_run.add_argument("--db", default="apartments.db", help="SQLite file for tracking seen listings")
    p_run.add_argument("--out", default="out", help="Output directory for drafts and report.json")
    p_run.add_argument("--your-name", default="[Your name]", help="Name to sign draft messages with")
    p_run.set_defaults(func=cmd_run)

    p_list = sub.add_parser("list", help="List stored listings.")
    p_list.add_argument("--db", default="apartments.db")
    p_list.add_argument("--status", default=None, choices=["new", "drafted", "contacted", "rejected", "saved"])
    p_list.set_defaults(func=cmd_list)

    p_mark = sub.add_parser("mark", help="Update a listing's status (e.g. after you send a message).")
    p_mark.add_argument("listing_id")
    p_mark.add_argument("status", choices=["new", "drafted", "contacted", "rejected", "saved"])
    p_mark.add_argument("--db", default="apartments.db")
    p_mark.set_defaults(func=cmd_mark)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
