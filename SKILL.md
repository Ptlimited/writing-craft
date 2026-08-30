---
name: writing-craft
description: Apply the nine writing traits that three blind AI judges independently valued when scoring 50 pieces of writing, and gate the draft against them before returning it. Use when writing or rewriting ANY prose a human will read - a post, a newsletter opening, hooks, a punch-up of flat copy, angles on a topic, an email, an essay, ad copy, a landing page. Trigger on "write a post", "write hooks", "give me angles", "make this less boring", "punch this up", "make this sound human", "does this read as AI", "rewrite this", or any drafting request. Also invoke from inside another writing skill that owns voice, since this skill owns craft and stays voice-neutral. Not for code, commit messages, config, or documentation.
---

# writing-craft

Nine traits, taken from what three independent blind judges said separated the best
writing from the worst across 50 pieces. Applied while drafting, then checked before the
draft is returned.

The rules are not style preferences. Each one is what a judge wrote down, unprompted by
any supplied vocabulary, after scoring 50 files down columns without knowing who wrote
what. See "Where these came from" at the end.

## How to use this skill

1. **Read the nine rules below before drafting.** They shape the draft. They are not a
   post-hoc edit pass.
2. **Draft.**
3. **Run the gate.** `python3 <skill>/check.py <draft-file>`. Add `--hooks` for hook
   lists, where hedging is zero-tolerance.
4. **Fix what fails, re-check.** Up to two revision passes.
5. **Return the draft with the check report.** If anything still fails after two passes,
   say so plainly rather than shipping it quietly.

Never claim a judgment rule passed without saying what you concluded. Never return a
draft that failed a mechanical check without naming the failure.

---

## The nine rules

### 1. Specificity only someone who did it would have

A number, an incident, a duration, a witnessed detail. Ninety lines. Forty minutes.
Three separate reminders about em-dashes. One task in ten. The top scorers all carry at
least one detail that would be pointless to invent. The bottom ones speak entirely in
category: "routine work", "genuinely complex problems", "a lot of people".

**This cannot be checked by counting numbers.** In the corpus the weak files carried
*more* digits than the strong ones, because they invented them. Judge the detail, not the
digit count. See rule 9, which is this rule's counterweight.

### 2. Argue with the brief

Add something the brief did not contain. The best drafts in the corpus admitted where the
recommended approach actually failed, named the honest limit the source skipped, or refused
the question as asked and answered a better one. Weak files restated the premise in a nicer
order and stopped.

This is why the Usable scores clustered high while Human and Post spread wide. Compliance
produces clean, shippable, forgettable copy. Plenty of drafts can ship. Far fewer are
worth shipping.

**Check:** name in one line what the draft adds that the brief did not contain. If you
cannot, it has not departed.

### 3. One load-bearing analogy, driven

The split is fit, not cleverness. Gears on a hill. A chess clock. A corridor question
against go-away-and-come-back. A phone brightness slider. Each makes a distinction the
piece could not make without it, and the piece stays inside it.

Decorative analogies are interchangeable and turned up in three or four files each:
sledgehammer and picture frame, consultants and subject lines, board meetings and email.
One weak rewrite ran gears, hood, final exam and consultants in a single short piece.

**Check:** count them. Keep one. Could it be swapped for a different analogy with nothing
lost? Then it is decoration. Cut it.

### 4. No stacked template shapes

Five shapes, each survivable alone:

- stacked single-sentence paragraphs
- an "unpopular opinion" or litany opener
- an aphorism couplet close
- a question aimed at the reader
- a tidy three-part list

Two or more together and the shape arrived before the thinking did.

**Check by reading, not by regex.** This rule resisted mechanisation: detectors built for
it fired on high and low scorers at the same rate, so `check.py` deliberately does not
test it. The judges saw these shapes by reading. So must you.

### 5. Cut the hedges

Might, may, often, can, sometimes, probably, tends to, arguably, perhaps, somewhat,
generally, typically. Once a piece hedges twice in a paragraph it stops having a point of
view, and a piece with no point of view reads as machine-made however clean the prose is.

**In hooks this is absolute.** A hedged hook is a contradiction in terms. "Your prompt
might be making it worse" is a shrug. "I'll bet you can't explain why half those lines
are there" is a dare.

**Mechanical:** at most 0.5 hedges per 100 words. Zero in hooks mode. Keep one only if you
can say out loud why it is load-bearing.

### 6. N options means N genuinely different options

When the brief asks for several of anything, the request splits writers into two
populations. Six files answering "give me 3 different angles" returned the same three
angles with different labels. Four returned angles that changed what the piece would be.
There was no overlap between the groups.

The good ones also said why each angle would work on a reader, which is the difference
between a list and a brief.

**Check:** does each option change what the finished piece would be? Give each a one-line
reason it works on a reader.

### 7. Contractions

Every file scored 2 on Human wrote "it is", "do not", "you are", "I am" throughout. Every
file scored 5 used contractions naturally. The surface symptom of something real: the low
files are being narrated, the high files are being said.

**Mechanical:** contracted forms must be at least 70% of contracted-plus-expanded.

### 8. Vary the rhythm

Formulaic files share a cadence: sentences of nearly equal length, one after another. The
human-sounding ones have a long sentence that runs on because the thought does, then a
short one that stops.

**Mechanical:** coefficient of variation of sentence length at least 0.45. This turned out
to be the single best discriminator of the four mechanical checks, firing on 10 of 12
low-scoring files and only 2 of 19 high-scoring ones.

### 9. Do not invent the specifics

Rule 1's counterweight, and the reason rule 1 cannot be automated. Unsupported first-person
claims, invented percentages and sweeping assertions all reduce usability, because a writer
has to verify or replace them before publishing. Two judges independently flagged an
unsourced 80% statistic in one file, having never been asked to fact-check anything.

**Mechanical:** every number, percentage, year, duration and first-person claim is
extracted and listed. Each is then either sourced, or marked for the writer to confirm.
Never invent one to satisfy rule 1.

---

## The gate

`check.py` tests rules 5, 7 and 8 mechanically and extracts rule 9's claim list. On the
50-file corpus those three checks together caught **12 of 12** of the lowest-scoring
files, at a cost of firing on 7 of 19 of the highest-scoring ones.

That false-positive rate is deliberate. A fired check costs one revision pass, in which a
hedge is either cut or defended. It does not reject the draft.

Rules 1, 2, 3, 4 and 6 are judgment. Work through them explicitly and write down your
conclusion for each. A silent pass is not a pass.

## Composing with a voice skill

This skill is voice-neutral and project-neutral on purpose. It owns craft, not sound.

A skill that owns voice - brand, cadence, banned phrases, platform rules - should call
this one before returning any artifact, and its own rules win any conflict. Craft says
"vary the rhythm"; voice says what the sentences sound like. If a voice guide bans a word
this skill would keep, the voice guide is right.

Where a voice guide already bans some hedges or stock phrases, that list is the specific
case of rule 5 and this skill is the general one. Keep both. Do not merge them, and do not
let this skill relax a stricter house rule.

## Not for

- Code, commit messages, config, technical documentation.
- Voice, brand or platform formatting decisions.
- Scoring or grading finished writing.
- Fiction and long-form narrative. The corpus does not cover it, so the rules are not
  evidenced there.

---

## Where these came from

Five models were each given the same five everyday writing jobs, twice: a social post, a
newsletter opening, three different angles on a topic, a punch-up of flat copy, and ten
hooks. Fifty outputs in total.

Filenames were scrambled and punctuation normalised so no output could be traced to its
author. Three frontier models from two different labs then scored all fifty blind, one
criterion at a time, on three questions: does this sound like a person wrote it, could it
ship after a light edit, and would a working writer put their name on it.

Each judge was then asked one open question, identical for all three and with no vocabulary
supplied: what separated the high scorers from the low ones, in your own words. None of them
saw another's answer. The nine rules are what came back.

**The mechanical thresholds were fitted to that corpus**, joining each file to the mean of
the three judges' scores for sounding human:

| Check | Threshold | Fires on the best (n=19) | Fires on the worst (n=12) |
|---|---|---:|---:|
| Hedges | > 0.5 per 100 words | 4 | 9 |
| Contractions | ratio < 0.7 | 2 | 8 |
| Rhythm | sentence-length CV < 0.45 | 2 | 10 |
| **Any of the three** | | **7** | **12** |

Sentence rhythm is the strongest single signal of the three.

**Two checks were built and cut.** Detectors for the template shapes in rule 4 fired equally
on the best and worst writing, so rule 4 is judged by reading. And counting numbers as a
proxy for rule 1 runs backwards: the weakest writing carried *more* numbers than the
strongest, because it invented them. That is why rule 9 exists.

**Measured effect.** Run against the same five jobs in a later blind round, a mid-tier model
using this skill improved on all five jobs, was worse on none, and took a perfect score on the
three-angles task. It closed just under half the gap to the larger model without overtaking it.
The scores themselves are in the repo README.

**Honest limit.** The rules were extracted from the judges' own notes, so anything scored
against them is being measured against the source of its own rules. Treat the numbers
as a direction, not a measurement.
