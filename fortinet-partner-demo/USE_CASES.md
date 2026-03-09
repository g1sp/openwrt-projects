# Fortinet Partner Use Cases — What Partners Find Difficult

This document ties the current demos to real partner pain points and lists **additional use cases** that Fortinet partners (VARs, MSPs, MSSPs) commonly find difficult when serving small and midsize businesses (SMBs).

---

## Are the current demos typical partner pain points? **Yes.**

| Current demo | Why it’s a real pain point |
|--------------|-----------------------------|
| **Policy Translator** | SMBs and partners struggle with **architectural and policy complexity**: multiple consoles, inconsistent rules, and lack of expertise. Turning “what we want” into correct FortiOS CLI reduces errors and speeds deployment. ([Fortinet: Reducing complexity for SMB customers](https://www.fortinet.com/blog/partners/grow-your-business-by-reducing-complexity-for-smb-customers-)) |
| **Alert Triage Engine** | **Fractured visibility** and **troubleshooting difficulty** are called out as SMB pain points: identifying root cause across traffic, devices, and applications is time-consuming. Prioritizing alerts with plain-English explanations lets partners (and SMBs) act faster without deep FortiAnalyzer expertise. |
| **Customer Report Narrator** | **Lack of visibility and analytics** increases operational cost; SMBs and their boards want **simple narratives**, not raw logs. Partners need to produce executive-style reports for C-level and auditors without manual copy-paste. |

So the three demos (policy → CLI, logs → triage, telemetry → narrative) align with **reducing complexity**, **faster troubleshooting**, and **better reporting** — all cited as partner/SMB challenges.

---

## Additional use cases partners often find difficult

These are typical “hard” or time-consuming tasks that partners do for SMBs. They are good candidates for future demos or features on the mini-PC.

### 1. **VPN intent → config (remote access & site-to-site)**

- **Partner ask:** “Customer needs VPN for 20 remote workers” or “Connect our main office and two branches.”
- **Why it’s hard:** VPN setup involves user groups, IPsec/SSL, portal settings, firewall policies, and (often) AD/LDAP. Site-to-site adds tunnel interfaces, routing, and failover. Partners often follow long docs or wizards and still make mistakes.
- **Use case:** Natural-language or form-based intent (e.g. “Remote access VPN for 30 users, split tunnel, no guest access”) → suggested FortiOS CLI or step-by-step checklist (no auto-apply). Could extend Policy Translator to a “VPN wizard” mode.

### 2. **Compliance / audit summary from config or logs**

- **Partner ask:** “Customer needs a one-pager for the auditor” or “Proof we have firewall and logging for SOC2/HIPAA.”
- **Why it’s hard:** Compliance requires mapping controls to framework (e.g. SOC2, HIPAA, PCI). Partners often manually map FortiGate/FortiAnalyzer features to control language.
- **Use case:** Input: config snippet or log summary. Output: short “compliance summary” (e.g. “Access control: firewall policies and VPN; Logging: forwarded to FortiAnalyzer; Encryption: in place for VPN”) for inclusion in customer or auditor packs. ([Fortinet Trust Portal](https://trust.fortinet.com/) for official Fortinet compliance; partner tool would summarize *customer* posture.)

### 3. **Troubleshooting: “Why can’t X reach Y?”**

- **Partner ask:** “User in branch A can’t reach the ERP in the data center” or “VPN users can’t print.”
- **Why it’s hard:** “Fractured visibility” across firewall, VPN, routing, and app policies makes root-cause analysis slow. Partners run multiple CLI commands and correlate in their head.
- **Use case:** Input: short symptom description (and optionally paste of relevant logs/config). Output: **likely causes** and **suggested checks** (e.g. “Check firewall policy from VPN to LAN; check VPN split-tunnel includes ERP subnet; verify DNS for ERP hostname”). No auto-fix — suggest next steps only.

### 4. **Firewall rule cleanup / optimization**

- **Partner ask:** “This FortiGate has 200 rules; customer wants to simplify and harden.”
- **Why it’s hard:** Redundant, shadowed, or overly permissive rules are security and operations risks. Manual review is tedious and error-prone.
- **Use case:** Input: export of firewall policy (or paste). Output: **findings** (e.g. “Rule 12 shadows rule 5”, “Rule 20 allows ANY service”, “Duplicate object used in 8 rules”) and **suggested cleanup** (human applies). Could be rule-only (no logs) to keep scope small.

### 5. **New branch / zero-touch provisioning checklist**

- **Partner ask:** “We’re adding a new branch FortiGate next week; what do we need to do?”
- **Why it’s hard:** Initial provisioning and consistency across sites (policies, VPN, NTP, logging) require checklists and templates. Partners often maintain their own runbooks.
- **Use case:** Input: “New branch, 1 FortiGate, site-to-site to HQ, same policy template as branch 2.” Output: **provisioning checklist** (hardware, licenses, interfaces, VPN template, policy clone, backup) and optional **CLI snippets** for the template. Complements FortiGate Cloud zero-touch; useful when partner does manual or hybrid rollout.

### 6. **SD-WAN / multi-site intent**

- **Partner ask:** “Prioritize Zoom and Teams over general web for all branches” or “Add branch 4 to our SD-WAN.”
- **Why it’s hard:** SD-WAN rules, performance SLAs, and member selection are complex. Small mistakes can break connectivity or QoS.
- **Use case:** Intent (e.g. “Add branch 4 to existing SD-WAN” or “Prefer Zoom/Teams on all sites”) → **suggested CLI or FortiManager-style steps** and short explanation. Read-only suggestions; no auto-apply.

### 7. **Upgrade / patch planning**

- **Partner ask:** “Customer is on 7.2; we want to go to 7.6. What should we check?”
- **Why it’s hard:** Release notes are long; behavior changes and deprecated options vary by config. Partners need a short, customer-specific checklist.
- **Use case:** Input: current version + (optional) high-level config (e.g. “VPN, UTM, 3 VLANs”). Output: **upgrade checklist** (backup, known issues, config changes, test steps) in plain language. Could pull from public release notes or a curated knowledge base.

### 8. **Quoting / BOM from requirements (sales assist)**

- **Partner ask:** “Customer needs firewall + VPN + UTM for 50 users and 2 sites.”
- **Why it’s hard:** Choosing the right FortiGate model, licenses (FortiCare, FortiGuard, etc.), and optional FortiClient/EMS is a recurring partner task. Wrong SKU means re-quote or margin loss.
- **Use case:** Input: natural-language requirements (users, sites, features like VPN, UTM, SD-WAN). Output: **suggested SKUs and license bundles** with short rationale (e.g. “FortiGate 60F for &lt;50 users; add FortiClient for remote”). No pricing in doc; partner adds locally. More “sales enablement” than technical, but partners do this often.

---

## Summary

- **Current three demos** (Policy Translator, Alert Triage, Customer Report Narrator) map to **real** partner/SMB pain: policy complexity, alert overload, and reporting/visibility.
- **Additional use cases** that partners often find difficult include: **VPN config from intent**, **compliance/audit summaries**, **troubleshooting “why can’t X reach Y”**, **firewall rule cleanup**, **branch provisioning checklists**, **SD-WAN intent → steps**, **upgrade planning**, and **requirements → BOM/SKU suggestions**. Any of these can be prioritized next based on partner feedback or mini-PC scope.
