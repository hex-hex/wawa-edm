# 143rd v2 tick — Chris Boyle / Mighty (chris@mighty.nz)

- source_id: `d58af9b2-8e6a-4f5c-8693-aea7eeccd865` v1
- new_id: `112b40a9-7490-489e-af75-10fb48fd8304` v2 (gap=1, clean baseline)
- envelope: Drafts 274 (APPENDUID 4 274)
- eml_md5: `34822acc29a8ab8d431666a6a8992965` (26,485-byte `.eml`)
- to: chris@mighty.nz
- subject: "Quick question for Chris Boyle"
- defects_fixed: [logo, h1, sig_pad, logo_pad]
  - logo.png × 1 → base64 inline (cached `/tmp/wa-logo.b64`)
  - H1 leak SUFFIX-LESS variant stripped via fix-script `H1_BLOCK` regex (NOT v2.7.5 EXEMPTION because leak comment `<!-- Subject-style H1 title -->` was present — disqualifying condition #1 per v2.7.100 TWO-condition gate)
  - sig padding lh:1.5 `8 32 24 32` → `8 32 8 32`
  - logo padding `16 32 24 32 align="left"` → `0 32 24 32 align="left"`
- verify_envelope.py: EXIT 0 cleanly on first try (`h1_comment_markers=0, h1_open_tags=0, hardcoded_png_imgs=0, base64_imgs=1, sig_padding_old=0, logo_padding_old=0`) — no `check_h1_exemption.py` invocation needed (the leak comment presence already disqualified EXEMPTION at the source-discriminator step)
- cross-tick md5 dedup: 0 hits across 366 docs scanned via dual-glob per v2.7.93 (167 step logs + 199 refs)
- 20th consecutive "Quick question for …" subject for a distinct recipient inbox
- source status-projection mismatch recurred (~102nd confirmation: filter=`scheduled` → initial GET=`scheduled` → final GET=`draft`; `updated_at=2026-06-23T21:13:15.870368Z` byte-identical throughout; v1 unchanged; 47s `created_at`-to-`updated_at` gap is a pre-existing one-shot touch from 2026-06-23, NOT this cron)
- v2.7.43 dual-filter pagination (1052 scheduled + 194 draft = 1246 candidate rows merged, v2.7.93 row count after exclusion = 1086), v2.7.45 stale-lock cleanup (0 stale), v2.7.51 self-cleanup of own `.inprogress` lock, v2.7.73 no-pipe PATCH verification, v2.7.74 raw-IMAP `BODY.PEEK[]` verification, v2.7.87 IMAP-UID fetch via `imap.uid('FETCH', '274', ...)`, v2.7.88 verify_envelope.py invoked via `python3 <path>`, v2.7.89 byte-identical `updated_at` discipline, v2.7.91 step-log via `write_file` (preserves backtick text cleanly), v2.7.92 raw-IMAP shape-probe (this tick observed **shape variant 3**: `d[0]` is a 2-tuple `(meta_str, raw_bytes)` and raw bytes at `d[0][1]` — same shape as 133rd / 135th / 139th / 142nd ticks), v2.7.93 dual-glob md5 dedup, v2.7.94 raw-scan over-report (this tick observed `padding 8 32 24 32=2` raw vs `sig_pad=True` regex with 1 live defect — 7th consecutive tick; v2.7.96 codification holds: trust the fix script's per-marker regex matching only), v2.7.100 TWO-condition gate re-validated as clean fall-through (3rd consecutive tick: 141 + 142 + 143), v2.7.80 source-version edge case (re-read GET showed `version=1` — POST auto-assigned `version=2`) all validated once more. 168 step logs total. 1,086 unprocessed candidates remain after this tick (1,087 → 1,086, −1).

**No new pitfall or workflow change discovered this tick.** Pure no-finding release documenting the 143rd v2 tick.

**Three non-pitfall observations worth recording:**

1. **v2.7.100 TWO-condition gate validated for a 3rd consecutive tick (141 + 142 + 143).** This tick's source carried BOTH `<!-- Subject-style H1 title -->` (suffix-less leak form, disqualifying condition #1) AND an `<h1 style="margin:0; font-size:22px; line-height:1.3; color:#1f2937; font-weight:600;">` open tag with all 4 canonical style fields in range (satisfied condition #2). Result: **EXEMPTION did NOT apply** — the leak comment's presence overrides the inline-styled `<h1>`. The fix script's `H1_BLOCK` regex (v2.7.18 permissive pattern with `re.DOTALL`) correctly stripped the entire block (comment + `<h1>` + `</tr>`) and `verify_envelope.py` exited 0 cleanly on first try without needing `check_h1_exemption.py`. **Lesson reaffirmed at the 143rd tick**: the TWO-condition gate continues to fall through cleanly when source has BOTH leak comment AND inline-styled `<h1>`. The pre-filter on `h1_comment_markers` remains the canonical decision point — when `h1_comment_markers >= 1`, the fix script handles it; EXEMPTION gate is only relevant when `h1_comment_markers == 0` AND `h1_open_tags == 1`.

2. **v2.7.94 raw-scan over-report re-validated (7th consecutive tick — 130 / 134 / 136 / 138 / 139 / 142 / 143).** This tick observed pre-fix `padding_8_32_24_32=2` raw vs fix-script regex matches=1 (live defect). The 2nd raw hit was the body `<td>` with `line-height:1.7` — fix-script `SIG_PAD_OLD` lookahead `(?=[^<\x27\x22]*line-height:1\.5)` correctly targeted only the lh:1.5 signature context, leaving the lh:1.7 body `<td>` untouched. The v2.7.96 codification ("**future ticks should NOT raise pre-filter raw-count drift as anomaly**") continues to hold. Trust the fix script's per-marker regex matching only.

3. **Source-status-projection mismatch bumped to ~102nd confirmation** of the canonical variant (filter=`scheduled` → initial GET=`scheduled` → final GET=`draft`; byte-identical `updated_at=2026-06-23T21:13:15.870368Z` confirms source untouched). The 47s `created_at`-to-`updated_at` gap was a pre-existing one-shot touch from 2026-06-23 (NOT this cron). Future ticks should continue trusting the byte-identical `updated_at` discipline per v2.7.89.

Reference: `/home/hex-bot/.hermes/skills/wawa-edm-push-drafts-to-himalaya/references/tick-2026-07-17-chris-boyle.md`
