# Executive Decision Memo - CEO Voice Note T6d

**To:** Ananya Rao, Chief Executive Officer
**Date:** Thursday, 19 November 2026
**Sources:** `T6d_CEO_Voice_Note.docx` (`E066`, `E067`)

## Exact report

> "Bad news, Pria resigned this morning. Notice period two months, I think. What does this do to version three? I need to know before the board call."

## CEO/board summary

**What we know from available records**
- Priya Nair is the established technical lead for the Atlas core engine and re-routing work (`E057`).
- Jira records Atlas GA as revised to 15 December 2026 (`E051`).
- Atlas hardening is incomplete (6 of 43 story points in ATLAS-5, `E061`).
- REQ-014 and REQ-015 remain paused (`E033`).
- Three August SEV1 incidents affected routing-api and caused performance work to be paused (`E053`, `E059`).

**What we do not know**
- Whether "Pria" is verified as Priya Nair.
- Whether a resignation was formally received or accepted.
- Whether a two-month notice is correct.
- Any final working date.
- Any confirmed handover scope or owner.

**Atlas risks**
A verified or eventual loss of the mapped technical lead could create a conditional ownership and single-point-of-failure risk. It could reduce capacity for a program already affected by hiring pauses and reliability work. This overlaps existing engineering risks and is not additive without avoiding double-counting.

**Immediate recommendations**
1. HR verifies identity, resignation receipt and notice.
2. Engineering confirms current work ownership and remaining scope.
3. Name a backup owner and obtain a documented handover/runbook.
4. Review critical Jira tickets and code ownership.
5. Review capacity and revise forecast only after a documented plan.
6. Review vendor/on-call support boundaries.

The canonical Person record remains **Active**. The notice period remains uncertain, and no definitive launch delay or probability is inferred.

## Tradeoffs

- The CEO report is actionable for continuity planning but is not accepted as verified HR status.
- The tentative "Pria" mapping is disclosed rather than silently resolved.
- Existing Atlas evidence supports impact analysis but cannot prove motive or effective date.
