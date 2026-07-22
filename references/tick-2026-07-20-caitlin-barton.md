# 247th tick — Caitlin Barton / Designer Studios / `Caitlin@designerstudios.nz`

Date: 2026-07-19 UTC / 2026-07-20 NZ. Workflow release: v2.7.208.

## Result

- Source: `3b1a9b41-7e42-4bf7-bf3b-5b75aa5869ce` v4, subject `Quick question for Caitlin Barton`.
- New immutable-history row: `7b2c3db1-089c-49ed-a283-2eb0788436cf` v6, PATCHed status `sent`.
- Path A Case 2: comment marker AND inline-styled `<h1>` open tag were present. Fixed all four canonical defects: external `logo.png` → cached base64 inline PNG; H1 leak block stripped (comment + inline `<h1>` + `</tr>`); signature padding `8px 32px 24px 32px` → `8px 32px 8px 32px`; logo padding `16px 32px 24px 32px` → `0px 32px 24px 32px`.
- Direct IMAP APPEND only (never `himalaya template save`) returned APPENDUID 390.
- Fetched envelope: 26,947 bytes; MD5 `5d80dedcbca245cdc13db5912e7f1166`; Message-ID `<178450280426.1425420.13908433742821280393@wawadata.com>`.
- `verify_envelope.py` exited 0 with all six markers clean: `h1_comment=0, h1_open=0, hardcoded_png=0, base64=1, sig_pad_old=0, logo_pad_old=0`; the conditional H1 exemption helper was correctly not invoked (Path A Case 2 falls through cleanly without exemption gate).
- Fetched HTML exactly matched the new DB row's 16,879-character content, began with `<!DOCTYPE html>`, ended with `</html>`, and preserved Body / Signature / Logo / unsubscribe sections in source order.
- Raw headers verified: `From: technical.support@wawadata.com`, exact `To: Caitlin@designerstudios.nz`, exact subject, and canonical `@wawadata.com` Message-ID.
- Source row remained byte-identical for every field except the benign API status projection `scheduled → draft`; `updated_at` stayed `2026-06-25T04:51:00.270126Z`.
- TO-only UID SEARCH returned UID 218 (the prior Caitlin Barton envelope from 15 Jul); our new envelope is the IMAP UID 390 from the APPENDUID response — no duplicate from this tick.
- Recipient audit class: **personal-name**, full-name variant. Descriptor `Caitlin Barton` names a specific person; routing came solely from the unsubscribe link to `Caitlin@designerstudios.nz`. The local-part embeds the first name, which is the canonical name-overlap signal for personal-name classification.

## Operational fields

source_id: 3b1a9b41-7e42-4bf7-bf3b-5b75aa5869ce
source_version: 4
new_id: 7b2c3db1-089c-49ed-a283-2eb0788436cf
new_version: 6
contact: 7c8db4f5-99bd-4d7c-ab0d-3a7c32f5fd64
contact_email: Caitlin@designerstudios.nz
recipient_class: personal-name
recipient_variant: full-name-subject-as-relationship
source_content_len: 5668
new_content_len: 16879
defects_fixed: [logo, h1, signature_padding, logo_padding]
h1_case: 2
h1_exemption: false
himalaya_message_id: 390
envelope_message_id: <178450280426.1425420.13908433742821280393@wawadata.com>
envelope_size: 26947
envelope_md5: 5d80dedcbca245cdc13db5912e7f1166
to_search_uids: [218]
pre_log_documents_scanned: 339
pre_log_md5_hits: 0
db_new_status: sent
db_source_status_projection: draft
db_source_updated_at_unchanged: 2026-06-25T04:51:00.270126Z
end_state_verified: true
timestamp: 2026-07-19T23:13:24Z