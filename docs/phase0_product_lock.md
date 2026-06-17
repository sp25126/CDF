# Phase 0 Product Lock: Shiksha Sahayak (AI Teaching Assistant)

**Project:** Voice-Enabled AI Teaching Assistant for Haryana Government Schools  
**Stakeholder:** Haryana Education Department (MVP Hackathon)  
**Architect:** Senior Product Architect  
**Status:** Locked - Phase 0

---

## 1. Final Product Scope
The Phase 0 MVP focuses on a text-simulated "Voice" interface to assist teachers in standard classrooms. The system accepts text input (acting as a proxy for STT) and provides high-utility pedagogical support.

*   **Live Concept Simplification:** Converts complex NCERT syllabus topics into simple, relatable Haryanvi/Hindi/English (Hinglish) analogies.
*   **Voice-Triggered Quizzing:** Instant generation of 3-5 relevant MCQs or oral questions based on the current context to check student understanding.

## 2. Clear Non-Goals
*   **No Audio Processing:** No Speech-to-Text (STT) or Text-to-Speech (TTS) engines in this phase.
*   **No Persistence:** No database; state lives in the session/frontend.
*   **No User Management:** No logins for students or teachers.
*   **No Content Management:** No RAG or custom PDF uploading; uses LLM internal knowledge for NCERT standards.
*   **No Analytics:** No tracking of student performance or usage metrics.

## 3. User Personas
### Primary: Mr. Jaideep Singh
*   **Role:** TGT Science, Govt Senior Secondary School, Rohtak.
*   **Context:** Large classes (50+ students), limited time to prepare creative analogies.
*   **Need:** A tool that can "overhear" a topic and suggest a simple way to explain it using local examples (e.g., explaining 'Force' using a tractor pulling a trolley).

### Secondary: Preeti
*   **Role:** Class 9 Student.
*   **Context:** Understands Haryanvi/Hindi better than academic English.
*   **Need:** To be asked questions that don't feel like a scary "test."

## 4. Demo Journeys
1.  **The "Samajh Mein Aaya?" Journey:** Teacher inputs "Explain Photosynthesis." The AI returns a 3-sentence explanation comparing leaves to a "Rasoi" (kitchen) and sunlight to "Chulha" (stove).
2.  **The Instant Check:** Teacher inputs "/quiz Newton's Third Law." AI instantly generates 3 questions about real-world scenarios (e.g., jumping from a boat).
3.  **Language Bridge:** Teacher asks for a Haryanvi analogy for "Evaporation." AI provides an example involving drying clothes in the June heat.

## 5. Success Criteria
*   **Latency:** AI response generation under 2 seconds.
*   **Relevance:** Analogies must use rural/semi-urban Haryana context (farming, local sports, family structures).
*   **Simplicity:** Output text should be at a Grade 5-8 reading level regardless of the topic's complexity.

## 6. Failure Criteria
*   **Academic Jargon:** Using terms like "photosynthetic phosphorylation" instead of "making food."
*   **UI Complexity:** Anything requiring more than two clicks to get an answer.
*   **Hallucination:** Providing scientifically incorrect "simplifications."

## 7. MVP Architecture Summary
*   **Frontend:** Next.js 14 (App Router) + TailwindCSS. Single-page "Command Center" UI.
*   **Backend:** FastAPI (Python 3.11+). Stateless REST API.
*   **LLM Integration:** LiteLLM or direct OpenAI/Groq SDK for rapid inference.
*   **Deployment:** Localhost/Vercel (Frontend) + Render/Railroad (Backend).

## 8. Strategic Feature Selection
*   **Why Simplification?** Haryana government schools face a "comprehension gap" where students read English but think in local dialects. Simplification bridges this gap.
*   **Why Quizzing?** Active recall is the most effective learning tool for large classrooms. Voice-triggered quizzing allows the teacher to maintain "flow" without stopping to write on the blackboard.

## 9. Explicitly Out of Scope
*   Dockerization or Container Orchestration.
*   Authentication (JWT, Clerk, etc.).
*   Database (PostgreSQL, MongoDB).
*   History/Session logging.
*   Custom RAG pipelines.
*   Animations or CSS-heavy transitions.
*   Audio hardware integration.
