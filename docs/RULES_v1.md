# LEGION SEAL: registry rules, version 1

Version 1 replaces version 0. Version 0 is sealed as leaf 0 and stays in the log, unchanged; it governed every entry
before the leaf that seals these rules. Version 1 applies from that leaf on: its SHA-256 is sealed by the operator
with the label "LEGION SEAL rules v1". Changing the rules again requires a new version sealed in a later leaf.

## Version history
- The rules that apply to an entry are the latest version sealed before its `leaf_index`: version 0 for the leaves
  before the version-1 leaf, version 1 from that leaf on. Earlier versions stay published: this is the versioning
  model, not an error.
- Version 0: leaf 0, SHA-256 `492da8f6cb7f789556ae49d3c28f41204a989d42a231057aae233689d0fa25ad`,
  https://seal.legion-api.com/seal/v1/rules/v0
- Version 1 (these rules): https://seal.legion-api.com/seal/v1/rules/v1, also served at /seal/v1/rules once its leaf
  is sealed.

## Change from version 0
- The per-IP Genesis cap (3 Genesis entries per hashed IP) is removed. It refused legitimate seals, for example
  builds from shared CI runners, and it was not a real Sybil defence: many addresses bypassed it.
- A submission is never refused for a quota on Genesis. Only the rate limits of §5 apply.
- Genesis is unchanged: the first 1000 leaves (`leaf_index` 0 to 999), with no reservation per IP.

## 1. What the registry does
- The registry stores a SHA-256 that you send, and an optional label of 64 characters or fewer. It never receives your content.
- Each entry becomes a leaf of an append-only Merkle tree (RFC 9162). The head of that tree is a C2SP checkpoint
  signed with Ed25519.
- Log origin: `seal.legion-api.com/v0`. The key name equals the origin.

## 1b. Confidentiality: a hash is not anonymous
- FR : un hash n'est pas anonyme ; un contenu court ou devinable est retrouvable par dictionnaire ; sale ton contenu si tu
  veux la confidentialité.
- EN: a hash is not anonymous; short or guessable content can be recovered by dictionary; salt your content if you want
  confidentiality.
- The page salts text by default, with 16 random bytes kept only in your receipt. Files are hashed as they are; the
  same file always gives the same hash.

## 2. What a receipt proves, and what it does not
- FR : Prouve que ce hash était enregistré à cette date selon les garanties du registre. Ne prouve PAS l'auteur,
  l'originalité, la propriété ni la véracité du contenu.
- EN: Proves that this hash was recorded at this date, within the registry's stated properties. Does NOT prove
  authorship, originality, ownership or truthfulness of the content.
- Stated properties:
  - the leaf is included in a signed tree head;
  - a later head is consistent with an earlier one (RFC 9162 consistency proof).
- Not provided today:
  - `observed_at` is the time declared by the registry's clock, not a qualified timestamp, and it has no legal value;
  - no external witness cosigns the heads, so there is no "same view for everyone" property;
  - one operator runs the registry;
  - no Bitcoin anchoring.

## 3. Order and Genesis
- An entry's order is its `leaf_index`. It is proven by the inclusion proof under a signed head.
- Genesis means the entries with `leaf_index` from 0 to 999.
  - A Genesis number is the entry's `leaf_index`, nothing more.
  - It grants no right. It is not sold, reserved or transferable, and it never will be.
- Genesis entries are first come, first served. There is no per-IP Genesis quota (removed in version 1).
- Operator entries are marked `"submitter":"operator"` inside the leaf, and they consume indexes like any other
  entry. They include these rules, the registry's code fingerprints and any retraction.
- The first submission of a given SHA-256 keeps its index. A later submission of the same hash returns the
  first entry's receipt.

## 4. Labels and retraction
- A label is optional and limited to 64 characters (NFC). It must not contain:
  - control or format characters;
  - URLs.
- The leaf commits to `label_sha256` only. The label text is served beside the leaf.
- An abusive label is retracted by a tombstone leaf (`"kind":"tombstone"`, operator) that names the target leaf.
  - The registry then stops serving the label text.
  - The original leaf, its hash and its proof stay unchanged.
  - Nothing is rewritten.
- A sealed hash is never retracted: a hash reveals no content.

## 5. Limits of use
- Submissions:
  - 6 per minute and 100 per day per IP;
  - 3000 per day in total.
- The body must be at most 256 bytes and contain exactly `{"sha256": "<64 lowercase hex>", "label"?: "<text>"}`.
- No account and no cookie. IP addresses are stored only as salted HMAC hashes, for rate limits and adoption
  counters.
- Free. No payment of any kind is wired. Possible extras (certificate, anchoring, short name) are marked "coming"
  and collect nothing.

## 6. Status
Prototype. The registry can be withdrawn. Before any withdrawal, the complete log (entries, signed heads and public
key) would be published for offline verification.
