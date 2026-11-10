# Slate Citation Lab report: carousel post

**Attach:** `slate-citation-lab-report.pdf` (13 slides). Document title: "Slate Citation Lab: how AI engines pick sources (1,000-query study)"
**First comment:** methodology summary or full-study link, plus a tag for Akilan.

---

We asked ChatGPT, Perplexity, Claude and Gemini the same 1,000 B2B software questions.

They agreed on 29 sources. Out of 31,128.

This is the first Slate Citation Lab report. 13 slides, swipe through. The short version:

→ Citation is a product decision. Perplexity shows 19 links per answer, Claude 12.5, AI Overview 9.4, ChatGPT 3.1.

→ Engines almost never cite the same page. Only 0.09% of query–URL citations came from all three link-showing engines.

→ But they name the same vendors. Any two engines share 35–42% of the vendors they recommend.

→ 74% of cited URLs aren't in Google's top 10 or AI Overview at all.

→ 546 Reddit, Quora and Stack Overflow pages ranked on page one. Perplexity quoted 405. Claude quoted 0. ChatGPT and Claude cited reddit.com zero times in 1,000 answers.

→ ChatGPT shows links on 91% of bottom-funnel queries and 8% of top-funnel ones. A third of them go to pricing pages.

→ Rank is the one rule every engine follows. Perplexity cites the #1 result 87% of the time. Claude, 35%.

→ We tested 19 page attributes on 6,881 ranking pages. For Perplexity and AI Overviews, none cleared a negligible effect size. Only rank did. Claude is the exception: it leans toward deeper, more structured pages.

→ Definition pages are top-two in every citing engine. Pricing pages are Perplexity's most-cited format and AI Overview's least.

My read:
"AI visibility" isn't one channel. It's four engines with different retrieval, different source policies and almost no shared evidence. The stable outcome is whether your product gets named. Track that per engine, and be sceptical of page-level "AI optimisation" this data can't find.

Method (slide 2): API with web search (gpt-5.4-mini, sonar-pro, claude-sonnet-4.6, gemini-2.5-flash), one run per query on 3 Aug 2026, every URL normalised and joined per query to Google's top 10 and AI Overview. Mann-Whitney + Cliff's δ for effect sizes.

Limits (slide 13): this is API, not the consumer apps. Malte Landwehr's UI vs API work shows they retrieve differently, so read the levels as API-side.

Akilan on our team designed and ran the study.

Next Citation Lab: the 74% of cited pages that never show up in Google.

Which finding surprised you most?
