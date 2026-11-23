# Reference research (niche channels, hooks, structures) - run on the PC (Gemini key there; this costs Gemini, not Claude)

1. Put public YouTube Shorts links in `research/refs.txt`, one per line (from Enes's "Refs" playlist).
2. For each link (PC session):
   `python tools/llm/gemini.py "$(cat research/hook_template.txt)" --youtube <link> --out research/notes/<id>.md`
3. Claude reads the notes and writes `research/refs_report.md`: patterns across all videos + what to copy / what to avoid. Commit + push.
Never download YouTube videos (terms of use). Keep the notes short; they are data for us, not content to publish.
