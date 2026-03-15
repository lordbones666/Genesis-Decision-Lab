from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompiledQuestion:
    question_id: str
    wording: str
    event_definition: str
    reference_class_key: str


def compile_vague_question(prompt: str, prefix: str = "Q") -> list[CompiledQuestion]:
    prompt_lower = prompt.lower()
    templates: list[CompiledQuestion] = []
    if "worse" in prompt_lower or "escalat" in prompt_lower:
        templates.extend(
            [
                CompiledQuestion(
                    question_id=f"{prefix}1",
                    wording="Will conflict casualties exceed 1000 by the horizon?",
                    event_definition="casualties > 1000",
                    reference_class_key="conflict_casualties_1000",
                ),
                CompiledQuestion(
                    question_id=f"{prefix}2",
                    wording="Will a new state actor enter the conflict by the horizon?",
                    event_definition="new_state_actor_enters = yes",
                    reference_class_key="conflict_new_state_actor",
                ),
                CompiledQuestion(
                    question_id=f"{prefix}3",
                    wording="Will a key trade chokepoint close by the horizon?",
                    event_definition="strategic_chokepoint_closed = yes",
                    reference_class_key="chokepoint_closure",
                ),
            ]
        )
    if not templates:
        templates.append(
            CompiledQuestion(
                question_id=f"{prefix}1",
                wording=f"Will the event in '{prompt}' occur by the horizon?",
                event_definition="binary_event_occurs = yes",
                reference_class_key="generic_binary_event",
            )
        )
    return templates
