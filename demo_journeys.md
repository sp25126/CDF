# Demo Journeys: Shiksha Sahayak

These journeys are designed for a 3-minute hackathon walkthrough.

---

## Journey 1: The "Rasoi" Analogy (Science Explanation)
**Goal:** Show how the AI bridges the comprehension gap using local context.

1.  **Teacher Command:** "Explain Photosynthesis to Class 7."
2.  **System Behavior:** Processes the intent `explain` and retrieves the 'Kitchen' analogy.
3.  **On-Screen Result:** A card titled "Photosynthesis (Pedhon ki Rasoi)" appears with 3 simple bullets and a graphic/text description of a *Chulha*.
4.  **Spoken Result (Simulated):** "Bachon, jaise hamare ghar mein rasoi mein khana banta hai, waise hi patton mein dhoop se khana banta hai..."
5.  **Evaluator Notice:** The use of "Rasoi" and "Chulha" instead of "Chloroplast" or "Stomata".

---

## Journey 2: The "Kusti" Quick Check (Physics Quiz)
**Goal:** Show instant, relevant active recall generation.

1.  **Teacher Command:** "Quiz on Force for Class 9."
2.  **System Behavior:** Processes `quiz` intent and generates 3 MCQs based on Force.
3.  **On-Screen Result:** A "Quick Quiz" card showing 3 questions with large, clickable options.
4.  **Spoken Result (Simulated):** "Chalo dekhte hain kisko samajh aaya. Force pe teen sawal!"
5.  **Evaluator Notice:** How quickly the teacher can transition from teaching to testing without touching a blackboard.

---

## Journey 3: The "Full Loop" (Contextual Continuity)
**Goal:** Show that the AI maintains session state.

1.  **Teacher Command:** "Explain Evaporation."
2.  **System Behavior:** Shows explanation using drying clothes in the sun.
3.  **Teacher Command:** "Now take a quiz on this." (Note: No topic mentioned).
4.  **System Behavior:** Uses the previous session context (Evaporation) to generate a relevant quiz.
5.  **On-Screen Result:** Explanation card fades out, and a Quiz card about water vapor and heat appears.
6.  **Evaluator Notice:** The AI understands "this" refers to the topic just discussed.

---

## Evaluation Checklist for Demos
- [ ] **Hinglish Fluency:** Does it sound natural to a Haryana teacher?
- [ ] **UI Visibility:** Is the text large enough for a projector in a bright room?
- [ ] **Speed:** Is the response time under 2 seconds?
- [ ] **Relevance:** Are the analogies actually rural-friendly?
