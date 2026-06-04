---
name: validate-problem
description: >
  Run a full problem validation before any discovery or solution work.
  Stage 0 — run this before /discover, /strategy, or /write-prd.
  Sharpens the problem statement, classifies pain level, surfaces the 5 
  riskiest assumptions, defines an evidence plan, and delivers a 
  GO / PAUSE / STOP verdict.
argument-hint: "[your raw product idea or problem statement]"
---

Load the `validate-problem` skill and run the full 5-stage framework 
on the problem the user has described.

Work through all 5 stages in order:
1. Sharpen the Problem Statement
2. Classify the Problem (Painkiller / Vitamin / Candy + awareness level)
3. Map the Top 5 Assumptions (ranked by risk)
4. Define the Evidence Plan for the top 2 assumptions
5. Deliver a GO / PAUSE / STOP verdict with clear reasoning

Produce the full Problem Validation Report as the output.

At the end, based on the verdict, suggest the exact next command to run.
