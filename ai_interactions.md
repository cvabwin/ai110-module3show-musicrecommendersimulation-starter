# AI Interactions Log

This log records the AI-assisted work completed in this project.
The agent was Codex. The main stretch work was the agentic workflow,
diversity penalties, and a visual terminal table.
A separate design-pattern stretch feature was not implemented.

## Agentic Workflow (SF8)

**What task did you give the agent?**

I asked Codex to test different user profiles, run a weight experiment,
explain limitations, and complete the project documentation.
I also asked it to implement diversity penalties and a readable terminal table.
The agent read the local files, edited the code, ran commands, and checked the results.

**Prompts used:**

These are excerpts from my project requests:

> Define at least three distinct user preference dictionaries.

> Double the importance of energy and half the importance of genre.

> Implement a "Diversity Penalty" that prevents the recommender from suggesting too many songs from the same artist or genre in the top results.

> Ensure your prompt specifies that the table must include the "reasons" for each score.

> Please complete any sections not completed in README.md and model_card.md.

The README also preserves reusable prompts for the diversity rule and table formatting.

**What did the agent generate or change?**

- `src/main.py`: Added seven named profiles, including boundary and missing-label cases.
  Added an ASCII table with ranks, songs, artists, adjusted scores, and reasons.
- `src/recommender.py`: Changed the genre bonus from 2 to 1 and the energy weight
  from 1.5 to 3. Added penalties of 1 point per earlier artist match and 0.5 points
  per earlier genre match. Connected the class interface to the shared functions.
- `tests/test_scoring.py`: Updated expected scores for the new weights.
- `tests/test_ranking.py`: Kept checks for ranking, explanations, and tie handling.
  Used zero penalties when checking the earlier preference-only ranking.
- `tests/test_diversity.py`: Added checks for cumulative penalties, label normalization,
  input preservation, invalid penalty weights, and the class interface.
- `README.md` and `model_card.md`: Added explanations, experiment results,
  fenced terminal output, limitations, future work, and reflections.

The agent ran the recommender with all seven profiles.
It also ran the test suite with the project's virtual environment:

```powershell
.\.venv\Scripts\python.exe -m src.main
.\.venv\Scripts\python.exe -m pytest -q
```

The latest test run passed all 34 tests.

**What did you verify or fix manually?**

I listened to the music to test whether it felt like a good fit for the assigned categories.
This was a subjective check based on my own listening experience.
It helped me evaluate the category labels beyond the numerical scores and automated tests.
My impressions reflect my own taste, so other listeners may judge the fit differently.
I also ran manually ran pytests.

## Diversity and Fairness Logic

AI helped turn the request for variety into a concrete rule.
The recommender chooses one song at a time and penalizes candidates whose
artist or genre is already represented.
It recalculates deductions from each song's original preference score before every choice.
Repeats remain possible, so this encourages variety rather than enforcing a strict quota.

For Chill Lofi, the top five changed from four artists and three genres to
five artists and four genres.
Focus Flow lost points for repeating LoRoom and lofi, allowing Desert Compass to enter.
This increased variety, but did not prove fairness for every listener.

## Visual Summary Table

AI helped format the output with Python's standard library.
The table includes Rank, Song, Artist, Score, and Reasons columns.
Long text wraps, and each scoring contribution or penalty stays visible.
No extra table library was added.
Checks covered all seven profiles, long text, and an empty result list.

## What I Learned from Using AI

AI helped connect several steps: changing code, running experiments, checking results,
and explaining the behavior in the documentation.
The biggest lesson was to compare its explanations with actual outputs.
For example, a larger score after a weight change does not prove better recommendations.
I also learned to distinguish more variety from fairness and to keep old experiment
results separate from descriptions of the current system.
