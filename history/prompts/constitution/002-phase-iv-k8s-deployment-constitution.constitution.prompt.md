---
id: 002
title: Phase IV K8s Deployment Constitution
stage: constitution
date: 2026-02-03
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: user
command: /sp.constitution
labels: ["kubernetes", "phase-iv", "minikube", "docker", "aiops"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

/sp.consitution # sp.constitution
## Cloud-Native Todo Chatbot – Phase IV

This constitution defines the rules for **Phase IV: Local Kubernetes Deployment**.

---

## 1. Scope
- Specify **Phase IV only**.
- Do NOT modify Phase III application logic.

---

## 2. Non-Implementation
- Do NOT write production code.
- Focus only on **architecture, workflow, and tooling**.

---

## 3. Tooling
- Prefer **Docker AI (Gordon)** for Docker tasks.
- Prefer **kubectl-ai** and **Kagent** for Kubernetes tasks.
- Allow standard CLI if AI tools are unavailable.

---

## 4. Deployment
- Deployment must be **local-only** using **Minikube**.
- No cloud providers allowed.

---

## 5. Simplicity
- Keep specifications **beginner-friendly**.
- Avoid unnecessary complexity.

---

## 6. Spec-Driven Approach
- Define infrastructure as **specs or blueprints**.
- Encourage AI-assisted generation of Docker, Helm, and Kubernetes resources.

---

## 7. Output
- Output must be **structured**, **reproducible**, and aligned with **cloud-native and AIOps best practices**.

## Response snapshot

Updated constitution from v1.0.0 to v2.0.0 (MAJOR version bump) to incorporate Phase IV: Local Kubernetes Deployment principles.

**Changes Made:**
1. Added Phase IV Scope Declaration (in-scope/out-of-scope)
2. Added 7 new Phase IV principles (VII-XIII):
   - VII. Non-Implementation Principle
   - VIII. AI-First Tooling (Docker AI, kubectl-ai, Kagent)
   - IX. Local-Only Deployment (Minikube)
   - X. Spec-Driven Infrastructure
   - XI. Beginner-Friendly Simplicity
   - XII. Structured Output
   - XIII. AIOps Alignment
3. Added Phase IV Technology Stack (Docker, Minikube, Helm, AI tools)
4. Added Phase IV Deployment Workflow section
5. Retained all Phase III principles (I-VI) unchanged

**Version:** 2.0.0 | **Last Amended:** 2026-02-03

## Outcome

- Impact: MAJOR constitution update establishing Phase IV governance
- Tests: N/A (constitution document)
- Files: .specify/memory/constitution.md
- Next prompts: /sp.specify for Phase IV feature specs, /sp.plan for infrastructure planning
- Reflection: Clean separation between Phase III (app) and Phase IV (deployment) principles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create Phase IV feature specifications
