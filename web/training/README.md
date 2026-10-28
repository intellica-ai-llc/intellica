# arc42 workshop: course material

Writing Architecture Documentation with arc42. One-day beginner workshop,
Saturday 5 December 2026, UWI St Augustine.

## Files

- `index.html`: the course page (marketing, student guide, registration form)
- `slides.html`: the full-screen slides for facilitating the day

Both are single self-contained files. Upload them to `web/training/`.

## Before going live

In `index.html`, find the `CONFIG` block near the end of the file to change
the email, date, venue or early bird price. After the early bird date the page
removes the price automatically.

## Slides keys

Arrows, space or swipe: move. F: full screen. O: overview. N: notes.
P: presenter window (opens in a second window and stays in sync). T: timer.
Print to PDF from the browser for a handout (one slide per page).

To add slides, add entries to the `SL` array at the top of the script in
`slides.html`: `{t:"Title", h:"<h2>…</h2>", n:"speaker notes"}`.
