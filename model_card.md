# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

This is a working CLI-first simulation: the listener runs it in a terminal to
see ranked songs, scores, and the reasons behind each recommendation. It uses
fixed rules chosen for this project rather than learning from listening history.

The simulation loads 18 songs from a CSV file and converts their numerical
attributes into numbers it can compare. It considers the listener's favorite
genre, favorite mood, preferred energy level, and optional preference for
acoustic music. Each song starts with zero points:

- A matching genre earns 2 points.
- A matching mood earns 1 point.
- Energy earns up to 1.5 points. An exact match earns all 1.5 points, and the
  reward decreases in proportion to the distance from the preferred energy.
- If the listener prefers acoustic music, acousticness adds up to 0.5 points,
  with more acoustic songs earning a larger bonus. Otherwise, it adds no points.

Genre and mood comparisons ignore capitalization and surrounding spaces.
Energy and acousticness must be between zero and one. The highest possible
score is 5 points with the acoustic preference enabled, or 4.5 without it.
Tempo, valence, and danceability are loaded but do not affect this scoring rule.

Every song receives a score and a list of reasons explaining its points. The
simulation ranks the entire catalog from highest to lowest score, breaks equal
scores by choosing the lower song ID first, and returns the requested number
of recommendations (five by default). It preserves the catalog's original order
and uses full precision when ranking; only the displayed numbers are rounded.

For the default pop/happy profile with target energy 0.80, Sunrise City ranks
first with 4.470 points: 2 for pop, 1 for happy, and 1.470 for energy close to the
target. This makes the result easy to trace back to the listener's preferences.

The starter's functional placeholders have been replaced with CSV loading,
explainable scoring, and ranking, connected to formatted terminal output. The
separate object-oriented Recommender methods remain starter placeholders;
the CLI uses the implemented functions.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
