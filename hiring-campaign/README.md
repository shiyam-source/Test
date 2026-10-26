# TripleDart hiring campaign

A 5-slide animated carousel (1080×1350, 4:5) in a Thunderclap-style layout: print grid, huge grotesk type, outlined pills, marker scrawls and a sticker. It uses TripleDart's neon blue in place of Thunderclap's green.

| # | Slide | Animation |
|---|---|---|
| 01 | Cover: all 3 roles | Role board highlights each role in turn, spinning badge, scrolling ticker |
| 02 | Senior Recruiter | Candidate cards get stamped "Shortlisted" and swiped away, pipeline counts up |
| 03 | Account Managers | Client chat plays out, client-health ring fills to 96 |
| 04 | Director of Paid Media | Pipeline chart draws in, cursor clicks "Scale winners" |
| 05 | Why TripleDart + apply CTA | Stats count up, tiles light up in turn, pulsing apply button |

Posting plan and captions are in [CAPTIONS.md](CAPTIONS.md).

## Files
- `output/png/`: static images, and the PDF for the LinkedIn document carousel (`output/tripledart-hiring-carousel.pdf`)
- `output/mp4/`: animated slides for the Instagram carousel and single video posts (5 s loop × 3)
- `output/gif/`: animated slides (720 px wide) for LinkedIn single posts, Slack and WhatsApp

## Edit and re-render
- **Brand colour and fonts:** edit the tokens at the top of `src/styles.css` (`--blue`, `--font-display`, …).
- **Logo:** add `src/assets/logo.svg` (dark) and `src/assets/logo-white.svg` (for the dark slides). They replace the text wordmark automatically.
- **Copy:** each slide is plain HTML in `src/0X-*.html`.
- **Render:** `node render.js` renders everything. `node render.js 02` renders one slide, and `STILL_ONLY=1 node render.js` renders PNGs only, for a quick check.
  You need Playwright with Chromium, ffmpeg and ImageMagick.
