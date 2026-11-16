# Veloxa CXO Cockpit — Transcript Notes & Acoustic Hypotheses
**Assessment Phase:** Individual Hackathon (Day 1 Release — Mon 16 Nov 2026 10:00 IST)  
**Author:** Rivu Chattopadhyay  
**Standard:** Rigorous source criticism — mishearings treated as structured hypotheses with cross-system corroboration, not silently altered.

---

## 1. Executive Summary & Methodology

Day 1 files include two executive interview summaries produced by `MeetNotes AI`:
- **T1 · CEO Kickoff Call**: 38 minutes duration, audio quality rated **"fair"**. Speakers: Ananya Rao (CEO), Speaker 2 (unidentified board/advisor liaison).
- **T2 · CFO Call**: 26 minutes duration, audio quality rated **"poor (speakerphone)"**. Speakers: Meera Iyer (CFO), Ananya Rao (CEO).

Because automated speech-to-text (STT) models introduce acoustic distortions, phoneme substitutions, and truncation (especially on Indian English accents and noisy speakerphone recordings), all discrepancies are tracked as explicit hypotheses rather than silently edited in raw data.

---

## 2. Exhaustive Transcript Mishearing Inventory

| # | Transcript Text | File & Section | Hypothesized Entity / Term | Cross-System Grounding Evidence | Acoustic / Contextual Explanation | Confidence | Impact on Cockpit Logic |
|---|---|---|---|---|---|---|---|
| **TM-01** | *"Jeera board"* | T1 · Key points | **Jira** (Atlassian Issue Tracker) | `README.txt` engineering directory lists `engineering/ Jira (ATLAS), git history, PagerDuty, on-call rota`. | Phonetic substitution of "Jira" (/ˈdʒiː.rə/) to Hindi/Indian English culinary homophone "Jeera" (cumin). | **HIGH** | Engineering issue tracking queries map to Jira ATLAS board. |
| **TM-02** | *"Joho books"* | T2 · Key points | **Zoho Books** (SaaS Accounting Ledger) | `README.txt` finance directory: `Zoho Books general ledger`. `GL_Export_Apr-Sep_2026.xlsx` title: *"General ledger export, Zoho Books, Apr to Sep 2026"*. | STT voiceless/voiced affricate confusion (/z/ -> /dʒ/), rendering "Zoho" as "Joho". | **HIGH** | Financial transactions resolve to Zoho Books GL records. |
| **TM-03** | *"Kayka"* | T2 · Key points | **Keka** (HRMS & Payroll Platform) | `Employee_Master.xlsx` row 1: *"Keka HRMS export, employees only (contractors are not in Keka)"*. `README.txt`: `hr/ Keka HRMS`. | Phonetic spelling of software name "Keka" (/ˈkeɪ.kə/). | **HIGH** | Headcount, status, and reporting lines ground in Keka HRMS. |
| **TM-04** | *"Cult Amp"* | T1 · Key points | **Culture Amp** (Employee Engagement Tool) | `README.txt` hr directory lists `hr/ Culture Amp pulse`. | STT truncation/tokenization error splitting "Culture" into "Cult" and "Amp". | **HIGH** | Employee sentiment and pulse surveys resolve to Culture Amp. |
| **TM-05** | *"Linear, I think, or they moved back to the Jeera board"* | T1 · Key points | **Linear / Jira Migration** | `README.txt` lists Jira (ATLAS). No Linear folder in data room. | Ananya's casual recall reflects engineering tool evaluation: team experimented with Linear before returning to Jira. | **MEDIUM** | Cockpit notes Jira as authoritative active tracker. |
| **TM-06** | *"hub sport export"* | T1 · Action items | **HubSpot** (CRM / Inbound Marketing) | Speaker 2 promised export. CRM tool commonly used for B2B pipeline. | Acoustic split of compound noun "HubSpot" into "hub sport". | **HIGH** | Unfulfilled export flagged as missing data room asset. |
| **TM-07** | *"slag channel"* | T1 · Action items | **Slack channel** (`#engineering`) | Standard enterprise communication tool; engineering updates channel. | Voicing phoneme error replacing voiceless stop /k/ with voiced /g/ ("Slack" -> "Slag"). | **HIGH** | Communication channel reference logged for engineering sync. |
| **TM-08** | *"Vicky"* | T2 · Action items | **Vikram Menon** (VP Engineering, VX004) | Employee Master lists Vikram Menon as VP Engineering; Meera suggests checking freeze decision with him. | Common Indian diminutive/nickname for Vikram. | **HIGH** | Resolves entity reference to VX004. |
| **TM-09** | *"Kartik"* | T2 · Key points | **Karthik Subramanian** (FP&A Manager, VX010) | Email `01.eml` signed by "Karthik Subramanian"; Employee Master VX010. | Regional spelling variant (Kartik vs Karthik). | **HIGH** | Resolves entity reference to VX010. |
| **TM-10** | *"Pria"* | T1 · Key points | **Priya Nair** (Staff Engineer, VX007) | Employee Master VX007; architect of routing engine. | Phonetic spelling variant (Pria vs Priya). | **HIGH** | Identifies critical key-person dependency on Atlas v3. |
| **TM-11** | *"one-eighty, give or take"* | T1 · Summary | **Eighteen (18) or Contractor Pool (180)** | `Employee_Master.xlsx` lists 19 full-time employees (contractors excluded). Board reports 19. | **Dual Hypothesis:** (A) Acoustic stutter/mishearing: speaker said "eighteen, give or take" which STT rendered "one-eighty"; OR (B) CEO includes unlisted contractor/driver/field workforce. | **MEDIUM** | Cockpit states official FTE count as 19 and logs contractor ambiguity. |
| **TM-12** | *"two point two lakhs a month, sometimes two point five"* | T2 · Summary | **Net Burn (~2.2-2.5 L) vs Omitted 'Forty' (42.5 L)** | GL payroll alone is Rs. 31.75 L/mo; Board reports monthly burn Rs. 44-46 L. | **Dual Hypothesis:** (A) Audio dropped "forty" on poor speakerphone ("forty-two point five" -> "two point two to two point five"); OR (B) CFO quoted *Net Burn* (Gross burn 53 L - Monthly inflows 50.8 L = ~2.2 L net cash depletion). | **MEDIUM** | Cockpit flags CONF-002: reports audited board gross burn while noting net burn hypothesis. |

---

## 3. Grounding Rules for Cockpit Retrieval Engine

1. **Never Silently Overwrite Source Data:** Raw source text strings are preserved verbatim in evidence provenance.
2. **Deterministic Entity Resolution:** The engine maps aliases (`Vicky` -> `VX004`, `Pria` -> `VX007`, `Kartik` -> `VX010`) via explicit `Entity_Resolution` relational mappings.
3. **Transparent Uncertainty Notification:** Whenever a query hinges on an ambiguous transcript item (`one-eighty` vs `19`, or `2.2 L` vs `44 L`), the system returns the formal audited figure with a source conflict alert detailing the acoustic hypothesis.
