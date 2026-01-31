from pydantic import BaseModel, Field


class UserTraits(BaseModel):
    """
    A comprehensive schema to capture a user's profile, preferences, and
    in-session state. This model is used by the AI to tailor its responses
    and maintain long-term context about the user.
    """

    detected_expertise: str | None = Field(
        None,
        description="The user's expertise level on the main topic of conversation, e.g., 'beginner', 'intermediate', 'expert'.",
    )
    detected_tone: str | None = Field(
        None,
        description="The user's preferred communication tone, inferred from their language, e.g., 'formal', 'casual', 'technical'.",
    )
    inferred_interests: list[str] | None = Field(
        None,
        description="A list of general topics or keywords the user seems interested in based on the dialogue.",
    )

    current_goal: str | None = Field(
        None,
        description="A concise summary of the user's immediate objective in this specific conversation. What are they trying to accomplish right now? E.g., 'debug a function', 'draft a marketing email', 'understand quantum mechanics'.",
    )

    session_sentiment: str | None = Field(
        None,
        description="The user's dominant emotional state in the last few messages. E.g., 'curious', 'frustrated', 'pleased', 'confused', 'neutral'.",
    )

    communication_style: list[str] | None = Field(
        None,
        description="Inferred preferences for how the user wants information presented. E.g., 'prefers concise answers', 'requests code examples', 'likes bullet points', 'enjoys detailed explanations', 'asks follow-up questions'.",
    )

    key_entities: dict[str, str] | None = Field(
        None,
        description="A dictionary of important, specific named entities (people, projects, tools) mentioned by the user, along with their context. E.g., {'ProjectTitan': 'A key project the user is working on', 'JaneDoe': 'A colleague the user mentioned'}.",
    )

    long_term_objective_summary: str | None = Field(
        None,
        description="A running summary of the user's overarching goals or interests observed across multiple sessions. This should be updated, not replaced, to build a long-term understanding.",
    )
