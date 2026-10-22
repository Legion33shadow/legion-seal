#!/usr/bin/env python3
"""LEGION SEAL client: hash locally, send only the SHA-256, save the receipt. Python standard library only.

  python3 seal_client.py file PATH [--label TEXT] [--out seal.json]
  python3 seal_client.py text "my idea" [--no-salt] [--out seal.json]   # 16-byte random salt by default, kept in the receipt

Your content never leaves your machine. Then verify offline: python3 verify_seal.py seal.json --file PATH
(for a salted text: python3 verify_seal.py seal.json --sha256 <entry.sha256>, after recomputing it from seal_local).
A receipt proves that this hash was recorded at this date, within the registry's stated properties. It does NOT prove
authorship, originality, ownership or truthfulness of the content."""
import argparse, hashlib, json, os, sys, urllib.request

BASE = os.environ.get("SEAL_BASE", "https://seal.legion-api.com")


def salted(text, salt_hex):
    return ("legion-seal-salt " + salt_hex + "\n").encode() + text.encode()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("kind", choices=("file", "text")); ap.add_argument("value")
    ap.add_argument("--label"); ap.add_argument("--no-salt", action="store_true"); ap.add_argument("--out")
    ap.add_argument("--base", default=BASE); ap.add_argument("--test", action="store_true", help="send X-Legion-Test (excluded from counters)")
    a = ap.parse_args(argv)
    if a.kind == "file":
        h = hashlib.sha256()
        with open(a.value, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        local = {"kind": "file", "name": os.path.basename(a.value), "salt_hex": None}
    else:
        salt = None if a.no_salt else os.urandom(16).hex()
        h = hashlib.sha256(salted(a.value, salt) if salt else a.value.encode())
        local = {"kind": "text", "name": None, "salt_hex": salt,
                 "salted_format": "UTF-8('legion-seal-salt ' + salt_hex + '\\n') + UTF-8(text)" if salt else None}
    sha = local["sha256"] = h.hexdigest()
    body = {"sha256": sha}
    if a.label:
        body["label"] = a.label
    hdr = {"Content-Type": "application/json", "User-Agent": "legion-seal-client/1"}
    if a.test:
        hdr["X-Legion-Test"] = "client"
    q = urllib.request.Request(a.base.rstrip("/") + "/seal/v1/submit", data=json.dumps(body).encode(), headers=hdr, method="POST")
    with urllib.request.urlopen(q, timeout=30) as r:
        rec = json.loads(r.read())
    if rec.get("entry", {}).get("sha256") != sha:
        print("receipt hash does not match the local hash", file=sys.stderr); return 1
    rec["seal_local"] = local
    out = a.out or "seal-%d.json" % rec["leaf_index"]
    with open(out, "w") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    print("sha256 %s\nleaf %d%s\nreceipt %s\nproof %s" % (sha, rec["leaf_index"], " (already sealed: first entry)" if rec.get("duplicate_of_first_submission") else "",
                                                        out, rec["proof_url"]))
    if local["salt_hex"]:
        print("salt %s  (keep the receipt AND the exact text)" % local["salt_hex"])
    print("badge [![sealed](%s/seal/v1/badge/%d.svg)](%s)" % (a.base.rstrip("/"), rec["leaf_index"], rec["proof_url"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
