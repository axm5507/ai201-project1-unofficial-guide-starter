# The Unofficial Guide — Project 1

> This is my first project for the CodePath AI201 course. I built a simple RAG-based chatbot that provides you with information about different events in the Bryan/College Station area. I designed a planning guide that helped me implement each feature one-by-one, including building a webscraper, chunking data, vectorizing it, giving it to an LLM,and then retrieving it for a coherent output.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->
This chatbot provides the user with help on finding things to do in the Bryan/College staiton area. 

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 |Reddit|A thread of places in Bryan/College Station that students recommend. |https://www.reddit.com/r/aggies/comments/13znhx2/what_are_some_things_to_doplaces_to_go_in_bryan/ |
| 2 |Reddit |A thread of things to do in Bryan specifically |https://www.reddit.com/r/aggies/comments/1clpu1l/is_there_anything_to_do_in_bryan/ |
| 3 |Destination Bryan |Official website of Bryan, Texas detailing the things to do there |destinationbryan.com/things-to-do/ |
| 4 |Visit College Station |Official website of College Station, Texas detailing the things to do there |https://visit.cstx.gov/things-to-do/ |
| 5 |TripAdvisor |List of things to do in the Bryan area |https://www.tripadvisor.com/Attractions-g55543-Activities-Bryan_Texas.html |
| 6 |Texas A&M University |Official University Calendar of events |https://getinvolved.tamu.edu/events|
| 7 |Reddit |Thread detailing nightlife in College Station |https://www.reddit.com/r/CollegeStation/comments/1iryy2y/night_life/ |
| 8 | Visit College Station|Official College Station website detailing nightlife options there |https://visit.cstx.gov/things-to-do/nightlife/ |
| 9 |Visit College Station |Official College Station events calendar |https://visit.cstx.gov/events/ |
| 10 |Destination Bryan |Official Bryan events calendar |https://www.destinationbryan.com/events/ |


FULL DISCLOSURE: I was not able to webscrape Reddit and TripAdvisor. I ommitted those websites, but am still keeping them here.
---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->


**Chunk size:**
A target of **80 tokens** with a hard cap of **256 tokens**. "Tokens" are counted with the *actual* all-MiniLM-L6-v2 tokenizer (`transformers.AutoTokenizer`), so the count is exactly what the embedding model sees. Chunking is segment-aware: each cleaned document is split into paragraphs; any paragraph longer than the target is further split on sentence boundaries; segments are then greedily packed up to the 80-token target. The result is small, focused chunks (typically a single venue/event or a couple of related lines).

**Overlap:**
**No overlap (0 tokens).** All of the documents that survived scraping are *listings* — event calendars and attraction/venue lists — where each item is self-contained, so carrying text across boundaries would just duplicate one venue into a neighbor's chunk and blur retrieval. (Overlap would matter for the planned Reddit discussion threads, where an idea spans several sentences, but those sources were blocked by anti-bot protection and are not in the corpus.)

**Why these choices fit your documents:**
1. **256-token cap = the model's real limit.** all-MiniLM-L6-v2 truncates input at 256 word-piece tokens, so anything larger would be silently cut off at embed time. The cap guarantees every chunk is fully embedded.
2. **80-token target because the sources are listings, not prose.** A single attraction or event is short (name + address + date ≈ 30–80 tokens). Small chunks keep one or two items per vector, which sharpens retrieval precision for specific queries (e.g. "live music in downtown Bryan") instead of returning a paragraph where the relevant line is diluted.

**Preprocessing before chunking:**
- **HTML stripped** with BeautifulSoup (lxml): removed `script/style/noscript/nav/footer/header/form/svg/iframe/aside`, then extracted text from the `main`/`article`/`body` container.
- **Encoding fixed** by parsing the raw response bytes so BeautifulSoup detects each page's own charset (some sites otherwise produced mojibake like `cafés`/`â€¦`).
- **Whitespace normalized** (collapsed runs of spaces, paragraph breaks preserved).
- **Boilerplate removed** with a filter that drops nav/call-to-action junk lines ("Details", "Map", "Save", "Open in Google Maps", "Learn More", "Continue Reading", "Submit Your Event", "Results 1-12 of …", e-newsletter prompts) and collapses immediately-duplicated lines (listing pages echo each venue name twice).

**Final chunk count:**
**50 chunks** across **6 documents** (Destination Bryan ×2, Visit College Station ×3, Texas A&M events). Chunk sizes range 25–80 tokens (avg ~67), all within the 256-token model limit.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

**Production tradeoff reflection:**

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

**How source attribution is surfaced in the response:**

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

**What the system returned:**

**Root cause (tied to a specific pipeline stage):**

**What you would change to fix it:**

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
