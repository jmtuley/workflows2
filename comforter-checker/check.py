"""Fetch the 16 King variants directly from Feathered Friends' Shopify store."""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

PRODUCTS = {
    "regular": "feathered-friends-bavarian-down-comforter",
    "seconds": "bavarian-down-comforter-washed-and-returned-or-factory-second",
    "organic-seconds": "organic-bavarian-down-comforter-washed-and-returned-or-factory-second",
}


def parse_variants(product, group):
    weights = ("Light", "Medium") if group == "organic-seconds" else ("Summer", "Light", "Medium")
    rows = []
    for weight in weights:
        for fill in ("700+ Goose Down", "850+ Goose Down"):
            matches = [v for v in product["variants"]
                       if v.get("options") == ["King", weight, fill]]
            if len(matches) != 1:
                raise ValueError(f"{group}: expected one King/{weight}/{fill}, found {len(matches)}")
            v = matches[0]
            if type(v.get("available")) is not bool or type(v.get("price")) is not int or v["price"] <= 0:
                raise ValueError(f"{group}: invalid availability or price: {v.get('id')}")
            rows.append(dict(group=group, weight=weight, fill=fill, id=v["id"],
                             available=v["available"], price_cents=v["price"],
                             url=f"https://featheredfriends.com/products/{PRODUCTS[group]}?variant={v['id']}"))
    return rows


def main():
    out = Path("comforter-results")
    out.mkdir(exist_ok=True)
    rows = []
    for group, handle in PRODUCTS.items():
        url = f"https://featheredfriends.com/products/{handle}.js"
        print(f"Fetching {url}", flush=True)
        request = Request(url, headers={"User-Agent": "ComforterStockChecker/1.0", "Accept": "application/json"})
        with urlopen(request, timeout=45) as response:
            print(f"HTTP {response.status}; content-type={response.headers.get('Content-Type')}", flush=True)
            product = json.load(response)
        (out / f"{group}.json").write_text(json.dumps(product, indent=2) + "\n")
        if product.get("handle") != handle:
            raise ValueError(f"Unexpected product handle for {url}")
        rows.extend(parse_variants(product, group))
    snapshot = dict(observed_at=datetime.now(timezone.utc).isoformat(), currency="USD", variants=rows)
    (out / "snapshot.json").write_text(json.dumps(snapshot, indent=2) + "\n")
    lines = ["| Product | King weight | Fill | Availability | Price (USD) |",
             "|---|---|---|---|---:|"]
    for row in rows:
        lines.append(f"| {row['group']} | {row['weight']} | {row['fill']} | "
                     f"{'In stock' if row['available'] else 'Sold out'} | ${row['price_cents']/100:.2f} |")
    report = "\n".join(lines) + "\n"
    print(report)
    (out / "report.md").write_text(report)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as summary:
            summary.write(report)


if __name__ == "__main__":
    main()
