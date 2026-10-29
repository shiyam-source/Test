# TripleDart hiring campaign

A 6-slide animated carousel (1080×1350, 4:5) in a Thunderclap-style layout: print grid, huge headline type, outlined pills, callouts and a sticker. It is built on the **TripleDart New branding** design system (https://claude.ai/artifact/8cRAVLs6VZheX3U4MhJ4wM):

- **Colour:** Electric Lime `#D0FF00` leads, always with dark text on it. Grounds alternate Black `#0B0B0B` (01, 06), Linen `#F2F2E6` (02, 04) and full lime (03, 05).
- **Type:** NeuSans for headlines and labels, Rubik for everything you read. The hand-lettered notes from the first draft are now NeuSans callouts, because the system allows only these two fonts.
- **Logo and texture:** the official wordmark SVGs (white on dark, black on light and lime), and `texture-grid-dark.svg` behind the black slides.
- **Depth:** borders, not shadows. The only glow is the soft lime one at the bottom of the dark slides.

| # | Slide | Animation |
|---|---|---|
| 01 | Cover: 10 openings, 6 roles | Role board highlights each role in turn, spinning ×10 badge, scrolling ticker |
| 02 | Recruiter (1) | Candidate cards get stamped "Shortlisted" and swiped away, pipeline counts up |
| 03 | Account Managers (3) | Client chat plays out, client-health ring fills to 96 |
| 04 | Paid Media and ABM (1 Manager, 2 Specialists) | Pipeline chart draws in, cursor clicks "Scale winners" |
| 05 | SEO and GEO (1 Lead, 2 Specialists) | AI answer cites the client, share-of-AI-answers bars fill, Google rank climbs to #1 |
| 06 | Why TripleDart + apply CTA | Stats count up, tiles light up in turn, pulsing apply button |

Posting plan and captions are in [CAPTIONS.md](CAPTIONS.md).

## Files
- `output/png/`: static images, and the PDF for the LinkedIn document carousel (`output/tripledart-hiring-carousel.pdf`)
- `output/mp4/`: animated slides for the Instagram carousel and single video posts (5 s loop × 3)
- `output/gif/`: animated slides (720 px wide) for LinkedIn single posts, Slack and WhatsApp

## Edit and re-render
- **Brand tokens:** the palette, fonts and the three themes (`.dark`, `.linen`, `.lime`) are at the top of `src/styles.css`, copied from the design system's `tokens.json`.
- **Fonts:** `src/fonts/` holds the NeuSans **trial** cuts from the design system. Their character set is limited, so `'`, `?`, `$`, `+`, `%` and `×` fall back to Rubik, and arrows and separators are drawn as shapes. Buy the licensed NeuSans family before posting publicly and drop it into `src/fonts/`.
- **Copy:** each slide is plain HTML in `src/0X-*.html`.
- **Render:** `node render.js` renders everything. `node render.js 02` renders one slide, and `STILL_ONLY=1 node render.js` renders PNGs only, for a quick check.
  You need Playwright with Chromium, ffmpeg and ImageMagick.
