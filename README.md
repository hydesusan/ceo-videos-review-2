# CEO Videos — Round 2 Review Tool

Second-round review site for the Contra Costa County civic-education videos (the new finals from Ilena/CCTV). Same design as round 1 (`../CEO-videos-review`), separate repo and separate comment sheet so round-2 comments don't mix with round 1.

Status: **local scaffold, not yet deployed.** `review.html` is rebranded and the video list is stubbed with placeholders.

## To finish (two inputs needed)

1. **Video links.** Source files are already in Dropbox:
   - Set B (edited finals) — `Certified Election Observer Series/Finals/Finals/` — used for videos 1, 2, 3, 4, 6, 7, 8, 9, 11 (music), and 11 (voiceover).
   - Set A (March cut) — `Certified Election Observer Series/Finals/` — used ONLY for Video 5 (edited version pending from Ilena).
   Right-click each file in Dropbox → Copy link, and paste each URL into the `VIDEOS` array in `review.html` (replace the `null`s; each line names its source file). The player auto-converts `dl=0` share links to streaming.

2. **New comment sheet.** Create a new Google Sheet, open Extensions → Apps Script, paste `apps-script.gs`, deploy as a Web App (Execute as: you; Access: Anyone), and paste the resulting `/exec` URL into `WEBAPP_URL` in `review.html`. Until then the page falls back to browser localStorage (no cross-reviewer sharing).

## Then deploy
- Create GitHub repo `hydesusan/ceo-videos-review-2`, push, enable Pages → served at `https://hydesusan.github.io/ceo-videos-review-2/`.
- Regenerate transcripts for the new cuts with `transcribe.py` (the `transcripts/` here are carried over from round 1 and are stale for the re-cut videos; `video-4.srt` is still valid).

## Reviewers
Susan Hyde, Jennie Barker, Dawn Kruger, Oren Samet.
