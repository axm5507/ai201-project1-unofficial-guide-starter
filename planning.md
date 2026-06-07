# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
Things to do in Bryan/College Station, including events for every type of interest.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

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

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
For reddit posts and comments, a chunk size of 600-800 tokens will suffice. For event calendars, I will keep one event per chunk(200-500 tokens).

**Overlap:**
I will keep 100-150 tokens overlap for reddit posts, and no overlap is necessary for event calendars.

**Reasoning:**
Reddit posts are trickier because event information is buried in discussions, while calendars provide clear information about what events there are and when.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
all-MiniLM-L6-v2 via sentence-transformers

**Top-k:**
20-30 chunks, and after re-ranking, send 5-8 chunks to the LLM.

**Production tradeoff reflection:**
If cost wasn't a constraint, I would focus on retrieval accuracy with a stronger embedding model.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 |What nightlife is present in College Station? |College Station's historic Northgate district presents many nightlife opportunities. |
| 2 |Are there any scenic nature spots in Bryan? |Lake Bryan presents a beautiful scenic backdrop with restaurants and picturesque waters.|
| 3 |Is there anything in College Station for a history buff? |College Station boasts the George H.W. Bush Presidential Library and Museum and the Museum of the American G.I. |
| 4 |Where to exercise in College Station? |The A&M Campus has various Rec Centers. |
| 5 |Are there any organic food markets in College Station? |Yes, the Aggieland Farmers Market is open on these days. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Issues with splitting events into chunks may arise.

2. Old/irrelevant data may be present.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->
 Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->
I plan to use Claude to help me scrape and chunk data from the websites I've found.

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
