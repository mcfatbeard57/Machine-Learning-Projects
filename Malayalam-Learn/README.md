# Kili — Learn Malayalam ⇄ English

A small, offline, gamified Malayalam course for personal use. No build step, no server.

**Run:** open `index.html` in a browser (phone or desktop).

## What's in it
- 8 units, 25 lessons: vowels, consonants, greetings, family, food, numbers, questions, everyday phrases.
- Exercises: multiple choice (both directions), tap‑the‑pairs, sentence building with word chips (both directions), typing, listening.
- Hearts (refill 1 every 20 min, practice earns one), XP, daily goal, streak, mistakes review.
- Transliteration (Manglish) toggle; hidden on script lessons so it doesn't give answers away.
- Progress saved in the browser's localStorage.

Listening exercises need a Malayalam text‑to‑speech voice on the device (Android: Google TTS → Malayalam). Without one they're skipped.

Keyboard: `1–4` pick an option, `Enter` check/continue, `Backspace` removes the last word chip.

## Adding content
Edit `data.js`. Words: `{ ml, tr, en, alt }`. Sentences: `{ ml: [tokens], tr, en, alt }`. Lessons are generated automatically (5 words each, plus a sentence lesson per unit).
