# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0** is a small, explainable music recommender.

---

## 2. Intended Use

VibeMatch suggests five songs from a listener's genre, mood, and energy preferences.
The listener can also ask for a more acoustic sound.
It assumes one genre, one mood, and one energy target can describe a listening session.

This project is for classroom learning and small experiments.
It shows how scoring rules and diversity choices affect recommendations.
It is not a full music service or a tool for judging someone's emotions.
It should not be used for music therapy or health decisions.
The scores are compatibility points, not predictions of enjoyment.

---

## 3. How the Model Works

The system uses fixed rules instead of learning from listening history.
It loads 18 songs from `data/songs.csv` and scores every song.
The weight-shift experiment is active:

- A matching genre earns 1 point.
- A matching mood earns 1 point.
- Energy earns up to 3 points. A closer match earns more points.
- An acoustic preference adds up to 0.5 points. More acoustic songs earn more.

Genre and mood matches ignore capital letters and surrounding spaces.
A mismatch earns no matching points, but does not exclude the song.
Energy and acousticness must be between zero and one.
Tempo, valence, and danceability are loaded but do not affect the score.
The maximum preference score is 5.5 with the acoustic preference, or 5 without it.

The system builds the recommendation list one song at a time.
For each earlier song by the same artist, a candidate loses 1 point.
For each earlier song in the same genre, it loses another 0.5 points.
Both penalties can apply together.
Before every choice, penalties are calculated from the original preference score.
The song with the highest adjusted score is selected next.
Equal scores favor the lower song ID.

These penalties encourage variety but still allow repeats.
Adjusted scores can be negative when few alternatives remain.
The system returns five songs, or all available songs if there are fewer.
The terminal table includes the adjusted score and every reason.
Only displayed scores are rounded; ranking uses full precision.

For Happy Pop with energy 0.80, Sunrise City leads with 4.940 points.
It earns 1 for pop, 1 for happy, and 2.940 for energy similarity.
Gym Hero earns 3.610 preference points, then loses 0.500 because pop is already represented.
Its displayed final score is 3.110.

The CLI and the `Recommender` class share the same selection logic.
The class's single-song explanation covers the preference match.
The `recommend_songs` results also explain list-dependent diversity penalties.

---

## 4. Data

The catalog contains 18 fictional songs across 15 genres.
The original 10 rows were kept, and 8 fictional songs were added.
The added feature values are invented examples, not measurements of recordings.
No original songs were removed.

Genres include pop, lofi, rock, ambient, jazz, synthwave, indie pop, soul,
folk, salsa, country, classical, hip hop, metal, and reggae.
Lofi has three songs, pop has two, and each other genre has one.
Mood labels include happy, chill, intense, relaxed, moody, focused,
melancholic, reflective, festive, nostalgic, solemn, confident, defiant, and hopeful.
There is no song labeled sad.

Each row has an ID, title, artist, genre, and mood.
It also has energy, tempo, valence, danceability, and acousticness.
Valence describes how positive the music sounds.
These numerical features use a zero-to-one scale, except tempo, which uses beats per minute.
Energy ranges from 0.19 to 0.98.

The catalog is too small to represent many listening needs or musical traditions.
It has no user ratings, listening history, lyrics, or language information.
A few labels and numerical values cannot describe someone's full musical taste.

---

## 5. Strengths

The ordinary profiles produce different leaders that fit their stated preferences.
Sunrise City leads happy pop, Midnight Coding leads chill lofi, and Storm Runner leads intense rock.
Energy rewards closeness to the listener's target instead of always favoring louder music.
Changing capital letters and surrounding spaces does not change the results.

The reasons make each score easy to check against the rules.
The diversity step increases Chill Lofi from four to five artists and from three to four genres.
The ASCII table keeps all score contributions and penalties visible.
These are useful results for a classroom simulation, not proof of listener satisfaction.

---

## 6. Limitations and Bias 

The exact-label mood check in `src/recommender.py` poorly serves listeners whose
preferred mood is missing from `data/songs.csv`: the catalog includes
"melancholic" and "solemn," but neither receives mood credit for a "sad" request.
In the High-Energy Sad Pop experiment, no song earned mood points, and Gym Hero,
which is labeled "intense," ranked first with 3.910 points under the active weights.
Energy similarity now contributes up to 3 points versus 1 for mood, so a close
energy match can dominate results when the requested emotional category is unsupported.
The absolute energy gap treats equally distant lower- and higher-energy songs
equally, but energy alone cannot capture sadness, and the available valence
feature is ignored.
The diversity penalties reduce repeated artists and genres, but the same
profile still returns the same list, so limited exposure remains a risk.

---

## 7. Evaluation

I ran seven profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock,
High-Energy Sad Pop, Unknown Labels with Zero Energy, Maximum-Energy Acoustic Rock,
and Pop with Mixed Case and Spaces.
I compared their top five songs, scores, and explanations.
I also compared the original weights, the weight shift, and the diversity step.
The zero-energy and maximum-energy inputs both worked.
The two equivalent pop profiles returned identical results.

I was surprised that Gym Hero still appeared for happy pop.
Its genre and energy matches earned points even without a mood match.
The weight shift changed the order for three profiles, including the duplicate pop profile.
Adding diversity later changed some selected songs as well as their scores.
These checks show how the rules behave, but listener feedback is needed to judge enjoyment.

### Diversity penalty (current version)

The current version keeps the experimental preference weights and adds a
selection step for variety. It chooses one song at a time. Before choosing
the next song, it subtracts 1 point for each earlier song by the same artist
and 0.5 points for each earlier song in the same genre. Both deductions apply
when both labels repeat. Labels ignore capitalization and surrounding spaces.
Each round starts with the original preference score, so penalties are not
accidentally subtracted twice.

The returned score and explanation include the penalties at the time the song
was selected. Ties still favor the lower song ID. Repeated artists and genres
are discouraged, not banned. The system can still fill the requested list even
if the catalog has few artists or genres. Adjusted scores can be negative.
Set `artist_penalty=0` and `genre_penalty=0` when calling `recommend_songs`
to reproduce the earlier ranking without diversity penalties.

The following comparison uses the same seven profiles and experimental weights
on both sides. Only the diversity penalties change. Counts refer to distinct
artists and genres in the top five. Scores in the last column include penalties.

| Profile | Artists before -> after | Genres before -> after | Current top five, in order |
| --- | --- | --- | --- |
| High-Energy Pop | 4 -> 5 | 4 -> 4 | Sunrise City (4.940); Rooftop Lights (3.880); Gym Hero (3.110); Concrete Crown (2.970); Brass Parade (2.730) |
| Chill Lofi | 4 -> 5 | 3 -> 4 | Midnight Coding (5.295); Library Rain (4.780); Spacewalk Thoughts (4.100); Coffee Shop Stories (3.355); Desert Compass (3.200) |
| Deep Intense Rock | 5 -> 5 | 4 -> 5 | Storm Runner (4.970); Gym Hero (3.910); Brass Parade (2.970); Iron Horizon (2.760); Concrete Crown (2.730) |
| High-Energy Sad Pop | 5 -> 5 | 4 -> 4 | Gym Hero (3.910); Sunrise City (3.260); Storm Runner (2.970); Brass Parade (2.970); Iron Horizon (2.760) |
| Unknown Labels, Zero Energy | 5 -> 5 | 5 -> 5 | Quiet Cathedral (2.430); Spacewalk Thoughts (2.160); Desert Compass (2.070); Velvet Goodbye (1.980); Library Rain (1.950) |
| Maximum-Energy Acoustic Rock | 5 -> 5 | 4 -> 5 | Storm Runner (4.780); Gym Hero (3.815); Brass Parade (2.980); Iron Horizon (2.950); Concrete Crown (2.470) |
| Pop with Mixed Case and Spaces | 4 -> 5 | 4 -> 4 | Sunrise City (4.940); Rooftop Lights (3.880); Gym Hero (3.110); Concrete Crown (2.970); Brass Parade (2.730) |

Chill Lofi changes from four artists and three genres to five artists and four
genres. Focus Flow loses points because Midnight Coding already represents
both LoRoom and lofi. Desert Compass enters the top five instead. Happy Pop
also replaces Night Drive Loop, a second Neon Echo song, with Brass Parade.
These changes give more artists and genres space in the list. They do not prove
fairness for all users: someone who wants only lofi may prefer the old list.
The results remain deterministic, so this does not add random exploration.

The command-line and object-oriented interfaces now share this selection logic.
The object-oriented single-song explanation describes the preference match;
list-dependent penalty explanations are available in the `recommend_songs` results.
Tests cover cumulative penalties, label normalization, tie handling, independent
artist and genre penalties, unchanged input data, and invalid penalty weights.
All 34 tests pass. All seven command-line profiles return five results.

#### Current Chill Lofi terminal output

The current CLI uses an ASCII table. The Reasons column preserves every score
contribution and diversity deduction. Earlier experiment captures below keep
their original list format.

```text
============================================================
MUSIC RECOMMENDER | Chill Lofi
============================================================
Loaded songs: 18
Profile: genre=lofi | mood=chill | energy=0.40 | likes_acoustic=True

Top 5 recommendations
+------+--------------------------+--------------------+---------+------------------------------------------+
| Rank | Song                     | Artist             | Score   | Reasons                                  |
+------+--------------------------+--------------------+---------+------------------------------------------+
| 1    | Midnight Coding          | LoRoom             | 5.295   | - genre match (+1.0)                     |
|      |                          |                    |         | - mood match (+1.0)                      |
|      |                          |                    |         | - energy similarity (+2.940)             |
|      |                          |                    |         | - acoustic preference (+0.355)           |
+------+--------------------------+--------------------+---------+------------------------------------------+
| 2    | Library Rain             | Paper Lanterns     | 4.780   | - genre match (+1.0)                     |
|      |                          |                    |         | - mood match (+1.0)                      |
|      |                          |                    |         | - energy similarity (+2.850)             |
|      |                          |                    |         | - acoustic preference (+0.430)           |
|      |                          |                    |         | - repeated genre penalty (-0.500)        |
+------+--------------------------+--------------------+---------+------------------------------------------+
| 3    | Spacewalk Thoughts       | Orbit Bloom        | 4.100   | - mood match (+1.0)                      |
|      |                          |                    |         | - energy similarity (+2.640)             |
|      |                          |                    |         | - acoustic preference (+0.460)           |
+------+--------------------------+--------------------+---------+------------------------------------------+
| 4    | Coffee Shop Stories      | Slow Stereo        | 3.355   | - energy similarity (+2.910)             |
|      |                          |                    |         | - acoustic preference (+0.445)           |
+------+--------------------------+--------------------+---------+------------------------------------------+
| 5    | Desert Compass           | Cedar Trail        | 3.200   | - energy similarity (+2.730)             |
|      |                          |                    |         | - acoustic preference (+0.470)           |
+------+--------------------------+--------------------+---------+------------------------------------------+
```

The following baseline and weight-shift results were captured before the
diversity penalties were added. They remain as evidence of the earlier experiments.

### Baseline stress test with diverse profiles

The following results were captured with baseline weights (genre 2.0, energy
1.5), before diversity penalties. `python -m src.main` now also applies
the diversity penalties described above.
Each named preference dictionary is defined in `src/main.py`; every run scores
all 18 catalog songs and prints the top five with scores and reasons. These
are observations of the earlier scoring rules, not listener satisfaction metrics.

| Profile | What it probes | Observed result |
| --- | --- | --- |
| High-Energy Pop | Pop, happy, energy 0.80 | Sunrise City leads with 4.470 points. |
| Chill Lofi | Lofi, chill, energy 0.40, acoustic preference | Library Rain leads with 4.855; its acoustic bonus outweighs Midnight Coding's closer energy match (4.825 total). |
| Deep Intense Rock | Rock, intense, energy 0.90 | Storm Runner leads with 4.485. Only one rock song exists, so the remaining results cross genres. |
| High-Energy Sad Pop | Potentially conflicting preferences: pop, sad, energy 0.90 | Gym Hero leads with 3.455. No song is labeled sad, so no mood points are awarded; the system still returns five songs. High energy and sadness are not inherently incompatible, but exact labels cannot capture that combination here. |
| Unknown Labels, Zero Energy | Unsupported genre and mood, lower energy boundary 0.00 | Quiet Cathedral leads with 1.215. With neither category matching, results depend entirely on energy similarity. There is no warning that both labels are unsupported. |
| Maximum-Energy Acoustic Rock | Rock and intense with an acoustic preference, upper energy boundary 1.00 | Storm Runner leads with 4.415 despite earning only 0.050 acoustic points. Acousticness is a small bonus, so it does not guarantee acoustic recommendations. |
| Pop with Mixed Case and Spaces | Attempt to change results using capitalization and surrounding whitespace | All five songs and full-precision scores match High-Energy Pop, confirming normalization. |

The three ordinary profiles give distinct leaders consistent with their category
preferences. The adversarial profiles expose limited label coverage and the
tradeoffs between fixed weights: a requested mood or acoustic sound can remain
poorly represented even when the recommender returns a complete list. Scores
measure rule compatibility, not confidence that the listener will enjoy a song.
The boundary inputs 0.00 and 1.00 both run successfully.

### Captured terminal output

The fenced blocks below contain baseline output from `python -m src.main`, split
by profile. Displayed scores are rounded to three decimal places.

#### High-Energy Pop

```text
============================================================
MUSIC RECOMMENDER | High-Energy Pop
============================================================
Loaded songs: 18
Profile: genre=pop | mood=happy | energy=0.80 | likes_acoustic=False

Top 5 recommendations
------------------------------------------------------------
1. Sunrise City - Neon Echo
   Final score: 4.470
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy similarity (+1.470)

2. Gym Hero - Max Pulse
   Final score: 3.305
   Reasons:
     - genre match (+2.0)
     - energy similarity (+1.305)

3. Rooftop Lights - Indigo Parade
   Final score: 2.440
   Reasons:
     - mood match (+1.0)
     - energy similarity (+1.440)

4. Concrete Crown - Verse Atlas
   Final score: 1.485
   Reasons:
     - energy similarity (+1.485)

5. Night Drive Loop - Neon Echo
   Final score: 1.425
   Reasons:
     - energy similarity (+1.425)
```

#### Chill Lofi

```text
============================================================
MUSIC RECOMMENDER | Chill Lofi
============================================================
Loaded songs: 18
Profile: genre=lofi | mood=chill | energy=0.40 | likes_acoustic=True

Top 5 recommendations
------------------------------------------------------------
1. Library Rain - Paper Lanterns
   Final score: 4.855
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy similarity (+1.425)
     - acoustic preference (+0.430)

2. Midnight Coding - LoRoom
   Final score: 4.825
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy similarity (+1.470)
     - acoustic preference (+0.355)

3. Focus Flow - LoRoom
   Final score: 3.890
   Reasons:
     - genre match (+2.0)
     - energy similarity (+1.500)
     - acoustic preference (+0.390)

4. Spacewalk Thoughts - Orbit Bloom
   Final score: 2.780
   Reasons:
     - mood match (+1.0)
     - energy similarity (+1.320)
     - acoustic preference (+0.460)

5. Coffee Shop Stories - Slow Stereo
   Final score: 1.900
   Reasons:
     - energy similarity (+1.455)
     - acoustic preference (+0.445)
```

#### Deep Intense Rock

```text
============================================================
MUSIC RECOMMENDER | Deep Intense Rock
============================================================
Loaded songs: 18
Profile: genre=rock | mood=intense | energy=0.90 | likes_acoustic=False

Top 5 recommendations
------------------------------------------------------------
1. Storm Runner - Voltline
   Final score: 4.485
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy similarity (+1.485)

2. Gym Hero - Max Pulse
   Final score: 2.455
   Reasons:
     - mood match (+1.0)
     - energy similarity (+1.455)

3. Brass Parade - Sol del Barrio
   Final score: 1.485
   Reasons:
     - energy similarity (+1.485)

4. Iron Horizon - Ashen Forge
   Final score: 1.380
   Reasons:
     - energy similarity (+1.380)

5. Sunrise City - Neon Echo
   Final score: 1.380
   Reasons:
     - energy similarity (+1.380)
```

#### High-Energy Sad Pop

```text
============================================================
MUSIC RECOMMENDER | High-Energy Sad Pop
============================================================
Loaded songs: 18
Profile: genre=pop | mood=sad | energy=0.90 | likes_acoustic=False

Top 5 recommendations
------------------------------------------------------------
1. Gym Hero - Max Pulse
   Final score: 3.455
   Reasons:
     - genre match (+2.0)
     - energy similarity (+1.455)

2. Sunrise City - Neon Echo
   Final score: 3.380
   Reasons:
     - genre match (+2.0)
     - energy similarity (+1.380)

3. Storm Runner - Voltline
   Final score: 1.485
   Reasons:
     - energy similarity (+1.485)

4. Brass Parade - Sol del Barrio
   Final score: 1.485
   Reasons:
     - energy similarity (+1.485)

5. Iron Horizon - Ashen Forge
   Final score: 1.380
   Reasons:
     - energy similarity (+1.380)
```

#### Unknown Labels, Zero Energy

```text
============================================================
MUSIC RECOMMENDER | Unknown Labels, Zero Energy
============================================================
Loaded songs: 18
Profile: genre=unknown | mood=unknown | energy=0.00 | likes_acoustic=False

Top 5 recommendations
------------------------------------------------------------
1. Quiet Cathedral - Elena Vale
   Final score: 1.215
   Reasons:
     - energy similarity (+1.215)

2. Spacewalk Thoughts - Orbit Bloom
   Final score: 1.080
   Reasons:
     - energy similarity (+1.080)

3. Desert Compass - Cedar Trail
   Final score: 1.035
   Reasons:
     - energy similarity (+1.035)

4. Velvet Goodbye - June Hollow
   Final score: 0.990
   Reasons:
     - energy similarity (+0.990)

5. Library Rain - Paper Lanterns
   Final score: 0.975
   Reasons:
     - energy similarity (+0.975)
```

#### Maximum-Energy Acoustic Rock

```text
============================================================
MUSIC RECOMMENDER | Maximum-Energy Acoustic Rock
============================================================
Loaded songs: 18
Profile: genre=rock | mood=intense | energy=1.00 | likes_acoustic=True

Top 5 recommendations
------------------------------------------------------------
1. Storm Runner - Voltline
   Final score: 4.415
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy similarity (+1.365)
     - acoustic preference (+0.050)

2. Gym Hero - Max Pulse
   Final score: 2.420
   Reasons:
     - mood match (+1.0)
     - energy similarity (+1.395)
     - acoustic preference (+0.025)

3. Brass Parade - Sol del Barrio
   Final score: 1.645
   Reasons:
     - energy similarity (+1.335)
     - acoustic preference (+0.310)

4. Iron Horizon - Ashen Forge
   Final score: 1.480
   Reasons:
     - energy similarity (+1.470)
     - acoustic preference (+0.010)

5. Sunrise City - Neon Echo
   Final score: 1.320
   Reasons:
     - energy similarity (+1.230)
     - acoustic preference (+0.090)
```

#### Pop with Mixed Case and Spaces

```text
============================================================
MUSIC RECOMMENDER | Pop with Mixed Case and Spaces
============================================================
Loaded songs: 18
Profile: genre= POP  | mood= HaPpY  | energy=0.80 | likes_acoustic=False

Top 5 recommendations
------------------------------------------------------------
1. Sunrise City - Neon Echo
   Final score: 4.470
   Reasons:
     - genre match (+2.0)
     - mood match (+1.0)
     - energy similarity (+1.470)

2. Gym Hero - Max Pulse
   Final score: 3.305
   Reasons:
     - genre match (+2.0)
     - energy similarity (+1.305)

3. Rooftop Lights - Indigo Parade
   Final score: 2.440
   Reasons:
     - mood match (+1.0)
     - energy similarity (+1.440)

4. Concrete Crown - Verse Atlas
   Final score: 1.485
   Reasons:
     - energy similarity (+1.485)

5. Night Drive Loop - Neon Echo
   Final score: 1.425
   Reasons:
     - energy similarity (+1.425)
```

### Small data experiment: weight shift (before diversity penalties)

The experiment in `src/recommender.py` halves `GENRE_MATCH_POINTS` from 2.0
to 1.0 and doubles `ENERGY_WEIGHT` from 1.5 to 3.0. Mood stays at 1.0 and
acousticness at 0.5. The catalog, seven profiles, validation, and ranking rule
are unchanged. All CLI profiles use these shared constants. This earlier experiment used only the CLI functions. The object-oriented
methods have since been connected to those functions.

**Math verification.** Let G and M be 1 for an exact normalized genre or mood
match and 0 otherwise, E be song energy, T be target energy, A be acousticness,
and L be 1 when acoustic preference is enabled and 0 otherwise:

```text
Baseline:   score = 2G + M + 1.5 * (1 - abs(E - T)) + 0.5 * L * A
Experiment: score =  G + M + 3.0 * (1 - abs(E - T)) + 0.5 * L * A
```

Because E and T are validated in [0, 1], their absolute difference is in [0, 1],
so energy similarity stays in [0, 1] and energy points stay in [0, 3]. All
contributions are nonnegative. The maximum is now 5.5 with acoustic preference,
or 5.0 without it. Scores are compatibility points, not probabilities; they do
not need to sum to one. Higher scores alone are not evidence of better results
because the score scale changed.

For Midnight Coding with Chill Lofi, the new calculation is
`1 + 1 + 3 * (1 - abs(0.42 - 0.40)) + 0.5 * 0.71 = 5.295`.
Library Rain earns `1 + 1 + 3 * (1 - abs(0.35 - 0.40)) + 0.5 * 0.86 = 5.280`.
The energy advantage is now 0.090, larger than Library Rain's 0.075 acoustic
advantage, so Midnight Coding moves from second to first. The baseline energy
advantage was only 0.045.

**Before/after comparison.** Each cell lists ranks 1 through 5. Baseline results
use the original weights; experimental results come from rerunning
`python -m src.main` with the new weights.

| Profile | Baseline top five | Experimental top five | Order changed? |
| --- | --- | --- | --- |
| High-Energy Pop | Sunrise City; Gym Hero; Rooftop Lights; Concrete Crown; Night Drive Loop | Sunrise City; Rooftop Lights; Gym Hero; Concrete Crown; Night Drive Loop | Yes |
| Chill Lofi | Library Rain; Midnight Coding; Focus Flow; Spacewalk Thoughts; Coffee Shop Stories | Midnight Coding; Library Rain; Focus Flow; Spacewalk Thoughts; Coffee Shop Stories | Yes |
| Deep Intense Rock | Storm Runner; Gym Hero; Brass Parade; Iron Horizon; Sunrise City | Storm Runner; Gym Hero; Brass Parade; Iron Horizon; Sunrise City | No |
| High-Energy Sad Pop | Gym Hero; Sunrise City; Storm Runner; Brass Parade; Iron Horizon | Gym Hero; Sunrise City; Storm Runner; Brass Parade; Iron Horizon | No |
| Unknown Labels, Zero Energy | Quiet Cathedral; Spacewalk Thoughts; Desert Compass; Velvet Goodbye; Library Rain | Quiet Cathedral; Spacewalk Thoughts; Desert Compass; Velvet Goodbye; Library Rain | No |
| Maximum-Energy Acoustic Rock | Storm Runner; Gym Hero; Brass Parade; Iron Horizon; Sunrise City | Storm Runner; Gym Hero; Brass Parade; Iron Horizon; Sunrise City | No |
| Pop with Mixed Case and Spaces | Sunrise City; Gym Hero; Rooftop Lights; Concrete Crown; Night Drive Loop | Sunrise City; Rooftop Lights; Gym Hero; Concrete Crown; Night Drive Loop | Yes |

Three of seven profiles changed order, including the normalization duplicate
of High-Energy Pop. The set of five recommended songs stayed the same for every
profile. In the pop profiles, Rooftop Lights moves above Gym Hero: it matches
happy and is closer to energy 0.80 (0.76 versus 0.93). Reducing genre's bonus
allows that mood and energy combination to outweigh Gym Hero's pop match.

**Accuracy or just different?** This experiment demonstrates sensitivity to
weights. The new lofi leader matches target energy more closely, but gives up
some acousticness; the pop change trades genre fidelity for mood and energy.
Without listener ratings or an independent relevance target, neither tradeoff
establishes improved accuracy. Unsupported sad/unknown labels still receive no
category bonus. The unknown-label profile keeps its order because doubling its
only contributing signal scales every score equally.

The experimental preference weights remain active. To reproduce the baseline,
restore `GENRE_MATCH_POINTS = 2.0` and `ENERGY_WEIGHT = 1.5`, and pass
`artist_penalty=0, genre_penalty=0` to `recommend_songs`. The earlier stress-test
blocks are preserved as baseline evidence. Tests with numerical score
expectations have been updated to the experimental recipe.

#### Experimental terminal output

##### High-Energy Pop

```text
============================================================
MUSIC RECOMMENDER | High-Energy Pop
============================================================
Loaded songs: 18
Profile: genre=pop | mood=happy | energy=0.80 | likes_acoustic=False

Top 5 recommendations
------------------------------------------------------------
1. Sunrise City - Neon Echo
   Final score: 4.940
   Reasons:
     - genre match (+1.0)
     - mood match (+1.0)
     - energy similarity (+2.940)

2. Rooftop Lights - Indigo Parade
   Final score: 3.880
   Reasons:
     - mood match (+1.0)
     - energy similarity (+2.880)

3. Gym Hero - Max Pulse
   Final score: 3.610
   Reasons:
     - genre match (+1.0)
     - energy similarity (+2.610)

4. Concrete Crown - Verse Atlas
   Final score: 2.970
   Reasons:
     - energy similarity (+2.970)

5. Night Drive Loop - Neon Echo
   Final score: 2.850
   Reasons:
     - energy similarity (+2.850)
```

##### Chill Lofi

```text
============================================================
MUSIC RECOMMENDER | Chill Lofi
============================================================
Loaded songs: 18
Profile: genre=lofi | mood=chill | energy=0.40 | likes_acoustic=True

Top 5 recommendations
------------------------------------------------------------
1. Midnight Coding - LoRoom
   Final score: 5.295
   Reasons:
     - genre match (+1.0)
     - mood match (+1.0)
     - energy similarity (+2.940)
     - acoustic preference (+0.355)

2. Library Rain - Paper Lanterns
   Final score: 5.280
   Reasons:
     - genre match (+1.0)
     - mood match (+1.0)
     - energy similarity (+2.850)
     - acoustic preference (+0.430)

3. Focus Flow - LoRoom
   Final score: 4.390
   Reasons:
     - genre match (+1.0)
     - energy similarity (+3.000)
     - acoustic preference (+0.390)

4. Spacewalk Thoughts - Orbit Bloom
   Final score: 4.100
   Reasons:
     - mood match (+1.0)
     - energy similarity (+2.640)
     - acoustic preference (+0.460)

5. Coffee Shop Stories - Slow Stereo
   Final score: 3.355
   Reasons:
     - energy similarity (+2.910)
     - acoustic preference (+0.445)
```

##### Deep Intense Rock

```text
============================================================
MUSIC RECOMMENDER | Deep Intense Rock
============================================================
Loaded songs: 18
Profile: genre=rock | mood=intense | energy=0.90 | likes_acoustic=False

Top 5 recommendations
------------------------------------------------------------
1. Storm Runner - Voltline
   Final score: 4.970
   Reasons:
     - genre match (+1.0)
     - mood match (+1.0)
     - energy similarity (+2.970)

2. Gym Hero - Max Pulse
   Final score: 3.910
   Reasons:
     - mood match (+1.0)
     - energy similarity (+2.910)

3. Brass Parade - Sol del Barrio
   Final score: 2.970
   Reasons:
     - energy similarity (+2.970)

4. Iron Horizon - Ashen Forge
   Final score: 2.760
   Reasons:
     - energy similarity (+2.760)

5. Sunrise City - Neon Echo
   Final score: 2.760
   Reasons:
     - energy similarity (+2.760)
```

##### High-Energy Sad Pop

```text
============================================================
MUSIC RECOMMENDER | High-Energy Sad Pop
============================================================
Loaded songs: 18
Profile: genre=pop | mood=sad | energy=0.90 | likes_acoustic=False

Top 5 recommendations
------------------------------------------------------------
1. Gym Hero - Max Pulse
   Final score: 3.910
   Reasons:
     - genre match (+1.0)
     - energy similarity (+2.910)

2. Sunrise City - Neon Echo
   Final score: 3.760
   Reasons:
     - genre match (+1.0)
     - energy similarity (+2.760)

3. Storm Runner - Voltline
   Final score: 2.970
   Reasons:
     - energy similarity (+2.970)

4. Brass Parade - Sol del Barrio
   Final score: 2.970
   Reasons:
     - energy similarity (+2.970)

5. Iron Horizon - Ashen Forge
   Final score: 2.760
   Reasons:
     - energy similarity (+2.760)
```

##### Unknown Labels, Zero Energy

```text
============================================================
MUSIC RECOMMENDER | Unknown Labels, Zero Energy
============================================================
Loaded songs: 18
Profile: genre=unknown | mood=unknown | energy=0.00 | likes_acoustic=False

Top 5 recommendations
------------------------------------------------------------
1. Quiet Cathedral - Elena Vale
   Final score: 2.430
   Reasons:
     - energy similarity (+2.430)

2. Spacewalk Thoughts - Orbit Bloom
   Final score: 2.160
   Reasons:
     - energy similarity (+2.160)

3. Desert Compass - Cedar Trail
   Final score: 2.070
   Reasons:
     - energy similarity (+2.070)

4. Velvet Goodbye - June Hollow
   Final score: 1.980
   Reasons:
     - energy similarity (+1.980)

5. Library Rain - Paper Lanterns
   Final score: 1.950
   Reasons:
     - energy similarity (+1.950)
```

##### Maximum-Energy Acoustic Rock

```text
============================================================
MUSIC RECOMMENDER | Maximum-Energy Acoustic Rock
============================================================
Loaded songs: 18
Profile: genre=rock | mood=intense | energy=1.00 | likes_acoustic=True

Top 5 recommendations
------------------------------------------------------------
1. Storm Runner - Voltline
   Final score: 4.780
   Reasons:
     - genre match (+1.0)
     - mood match (+1.0)
     - energy similarity (+2.730)
     - acoustic preference (+0.050)

2. Gym Hero - Max Pulse
   Final score: 3.815
   Reasons:
     - mood match (+1.0)
     - energy similarity (+2.790)
     - acoustic preference (+0.025)

3. Brass Parade - Sol del Barrio
   Final score: 2.980
   Reasons:
     - energy similarity (+2.670)
     - acoustic preference (+0.310)

4. Iron Horizon - Ashen Forge
   Final score: 2.950
   Reasons:
     - energy similarity (+2.940)
     - acoustic preference (+0.010)

5. Sunrise City - Neon Echo
   Final score: 2.550
   Reasons:
     - energy similarity (+2.460)
     - acoustic preference (+0.090)
```

##### Pop with Mixed Case and Spaces

```text
============================================================
MUSIC RECOMMENDER | Pop with Mixed Case and Spaces
============================================================
Loaded songs: 18
Profile: genre= POP  | mood= HaPpY  | energy=0.80 | likes_acoustic=False

Top 5 recommendations
------------------------------------------------------------
1. Sunrise City - Neon Echo
   Final score: 4.940
   Reasons:
     - genre match (+1.0)
     - mood match (+1.0)
     - energy similarity (+2.940)

2. Rooftop Lights - Indigo Parade
   Final score: 3.880
   Reasons:
     - mood match (+1.0)
     - energy similarity (+2.880)

3. Gym Hero - Max Pulse
   Final score: 3.610
   Reasons:
     - genre match (+1.0)
     - energy similarity (+2.610)

4. Concrete Crown - Verse Atlas
   Final score: 2.970
   Reasons:
     - energy similarity (+2.970)

5. Night Drive Loop - Neon Echo
   Final score: 2.850
   Reasons:
     - energy similarity (+2.850)
```

---

## 8. Future Work

**Additional features or preferences**

I would try using tempo and valence in the score.
This could help distinguish fast music from music that sounds happy.
I would ask listeners to compare results before choosing new weights.

**Better ways to explain recommendations**

I would explain both matches and missed preferences in everyday language.
For Gym Hero, I could say, "This matches your pop preference and energy level,
but its mood is intense rather than happy."
I would also tell users when their requested mood is missing from the catalog.

**Improving diversity among the top results**

I would expand the catalog with more songs in each genre and mood.
I would compare the current repeat penalties with stricter limits.
I would also try including one less familiar song that still fits some preferences.
I would check whether listeners enjoy this extra variety.

**Handling more complex user tastes**

I would let users choose several genres and moods instead of just one.
Users could set different preferences for studying, exercising, or relaxing.
They could also mark preferences as required or optional, so a mood mismatch
would not always be treated as acceptable.

---

## 9. Personal Reflection

**What I learned about recommender systems**

I learned that a recommender can use simple rules instead of learning from data.
The weights decide which preferences matter most.
Changing the energy and genre weights changed some rankings, but it did not
prove that the recommendations were better.

**Something unexpected or interesting I discovered**

I was surprised that Gym Hero appeared for someone asking for happy pop,
even though its mood is intense.
It still earned points for being pop and having similar energy.
This showed me that matching some preferences can outweigh missing another one.

**How this changed how I think about music recommendation apps**

I now see recommendations as choices shaped by the available songs and the
rules used to rank them.
A suggestion can feel personal even when it comes from a few simple comparisons.
I would look more closely at missing preferences and repeated songs before
assuming that an app understands someone's full taste in music.
