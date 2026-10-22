# LEGION SEAL — seal a hash in 10 seconds

**https://seal.legion-api.com** — free public registry: seal the SHA-256 of a file or a text in an append-only Merkle log
(RFC 9162) with Ed25519-signed heads (C2SP checkpoints). No account, no cookie, no payment.

> **Claim boundary.** A receipt proves that this hash was recorded at this date, within the registry's stated properties.
> It does **NOT** prove authorship, originality, ownership or truthfulness of the content.
> Limits: `observed_at` is the registry's declared clock (not a qualified timestamp, no legal value); no external witness
> cosigns today; single operator; no Bitcoin anchoring; prototype, can be withdrawn. A hash is not anonymous: short or
> guessable content can be found by dictionary, so salt it. Full rules: [docs/RULES.md](docs/RULES.md) (sealed as leaf 0).

This repository contains only the **offline verifier**, a **command-line client** and the **docs**. The server and its
keys are not here.

## Seal from the browser
1. Open https://seal.legion-api.com, pick a file or type a text.
2. The hash is computed in your browser (WebCrypto). Only `{"sha256": ...}` is sent.
   Text is salted by default with 16 random bytes, shown on screen and kept in your receipt. A file is hashed as is.
3. Download your receipt (`seal-N.json`). You land on your proof page `/seal/v1/proof/N`.

## Seal from the command line
```
python3 client/seal_client.py file FILE            # or: client/seal_client.py text "my idea"   (salted by default)
# or with curl only:
curl -s https://seal.legion-api.com/seal/v1/submit -H "Content-Type: application/json" \
  -d '{"sha256":"'$(sha256sum FILE | cut -c1-64)'"}' > seal.json
```

## Verify offline
```
python3 verify_seal.py seal.json --file FILE       # Python 3 + cryptography, no network, no LEGION import
```
`verify_seal.py` pins the registry key (`PINNED_VKEY`); the key inside a receipt is never trusted. It checks the entry
bytes (JCS, RFC 8785), the RFC 9162 inclusion proof and the Ed25519 signature of the head, and prints `RESULTAT: VALIDE`
or `RESULTAT: INVALID`. Same file as served live: compare `sha256sum verify_seal.py` with
`curl -s https://seal.legion-api.com/seal/v1/verify_seal.py | sha256sum`.

## Badge for your README (rolling out with v1)
```
[![sealed](https://seal.legion-api.com/seal/v1/badge/N.svg)](https://seal.legion-api.com/seal/v1/proof/N)
```
The badge reads `sealed · #N · <date>`: this hash is in the registry, nothing more. It says nothing about the quality
or the security of a project. Proof pages carry Open Graph previews; new public seals are listed in
`/seal/v1/feed.xml` (test and operator submissions excluded).

## Files
| file | what |
|---|---|
| `verify_seal.py` | single-file offline verifier, byte-identical to `/seal/v1/verify_seal.py` |
| `client/seal_client.py` | hash locally, submit the hash, save the receipt (standard library only) |
| `docs/RULES.md` | registry rules, byte-identical to `/seal/v1/rules` and to leaf 0 |

License: MIT.
