# Data schema: `data/journey-data.js`

Everything the site shows comes from one file, `data/journey-data.js`. It sets `window.AFM_DATA` to a JSON object. Edit the data, never `dist/index.html`. `scripts/check_data.py` enforces the rules below, and CI runs it on every push.

## Top level

| Key | Type | What it holds |
|---|---|---|
| `meta` | object | `candidate`, `start`, `exam`, `updated` (all dates `YYYY-MM-DD`), `planRule` |
| `topicFrequency` | object | Topic name to number of the last 8 sittings it appeared in. These names are the only valid `topic` values. |
| `days` | array | The 22 study days, numbered 1..N |
| `questions` | array | The question library (core and stretch) |
| `mocks` | array | The six full mock exams |
| `skills` | array | Professional-skills placements after each marking |
| `errors` | array | The mistake ledger |
| `journal` | array | Free notes (reserved) |

## `days[]`

```js
{ day: 4, phase: "1 Foundations", hours: 4,
  focus: "Interest rate hedging", tasks: "Sentence one. Sentence two.",
  status: null | "Done", actualHours: null | 3.5 }
```

`tasks` is split into numbered steps at each full stop, so write one instruction per sentence.

## `questions[]`

```js
{ id: "Q05", tier: 1,                     // 1 must do, 2 should do, 3 stretch
  name: "Abertafol Co", sitting: "Dec 2023 Q3", marks: 25,
  topic: "Interest rate hedging & netting",
  day: 4,                                 // plan day, or null for stretch
  note: "short context", why: null,       // why: required for core questions before 2023
  where: "Drive: Past papers and relevant material > ...",
  links: {
    q: "<Drive file URL>",                // ACCA question paper
    a: "<Drive file URL>",                // ACCA answer paper
    notes: "<Drive file URL>",            // tutor notes PDF
    notesKind: "summary",                 // optional: notes cover the whole paper
    xlsx: "<Drive file URL>",             // tutor workings
    folder: "<Drive folder URL>",         // tutor folder for the question
    bundle: true,                         // optional: q/a are the merged old-P4 PDFs
    locked: true                          // optional: PDFs are password-protected
  },
  video: false,
  attempts: [ { date: "2026-11-20", marks: 20, by: "Claude", notes: "short" } ] }
```

Link buttons open in a new tab. Mocks have no links (they are sat on the ACCA Practice Platform).

## `mocks[]`

```js
{ id: "M1", paper: "ACCA Mar/Jun 2024", questions: "Mahoney / Littlebredy / Garnod",
  day: 15, target: 0.45,
  q1: null | 0-50, q2: null | 0-25, q3: null | 0-25, prof: null | 0-20,
  date: null | "YYYY-MM-DD", lessons: "" }
```

## `skills[]`

```js
{ date: "2026-11-20", source: "Oxwick Co",
  communication: null | 0-3, analysis: 0-3, scepticism: 0-3, commercial: 0-3 }
```

0 Not at all, 1 Not so well, 2 Quite well, 3 Very well. Use `null` when the skill was not on offer (Communication is Section A only).

## `errors[]`

```js
{ date: "2026-11-20", question: "Oxwick Co", topic: "M&A & valuation",
  mistake: "what went wrong", rule: "the rule to remember", lost: 1 }
```
