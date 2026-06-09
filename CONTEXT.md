# CoffeeCompass

A conversational coffee-shop finder for the USC / Los Angeles area. A user describes the vibe or use case they want; the system grounds every answer in a real, retrievable set of cafes and shows them on a map.

## Language

### Cafes & search

**Cafe**:
A coffee shop in the curated USC/LA set, with a location, attributes (outlets, noise, price), and an ambience description used for semantic matching. The only kind of place this product knows about.
_Avoid_: Shop, coffee shop, store, venue, place.

**Recommendation**:
A Cafe the agent explicitly declares it is suggesting in response to a turn. A strict subset of the cafes considered during that turn — only Recommendations are spoken about in the answer and pinned on the map. A cafe that was merely retrieved or considered is **not** a Recommendation.
_Avoid_: Result, hit, match, suggestion (when you mean the declared subset).

**Ambience**:
The free-text description of a cafe's vibe and use case (e.g. "quiet, good for reading") that the system embeds and matches against, as distinct from its hard attributes (price, outlets, hours). Captured per cafe as its ambience text.
_Avoid_: Vibe, mood, description (when you mean the embedded text specifically).

### Conversation & memory

**Conversation**:
One continuous chat thread, identified by a `session_id` and scoped to a single browser tab. An ordered list of Turns over which follow-ups ("anything cheaper?") stay on topic. Short-lived.
_Avoid_: Session, thread, chat (as nouns for this concept), dialogue.

**Turn**:
One user message paired with the agent's response to it. The unit a Conversation is composed of.
_Avoid_: Message, exchange, round.

**User**:
The person using CoffeeCompass, identified by a `user_id` and persisting across Conversations. Owns a Preference Summary. Distinct from a Conversation: one User may have many Conversations over time.
_Avoid_: Account, customer, visitor, client.

**Preference Summary**:
A long-lived, cross-Conversation distillation of what a User tends to want (e.g. "usually wants cheap, quiet, near USC"). Belongs to a User, not a Conversation. Deferred in v1 (introduced with Zep behind the Memory protocol).
_Avoid_: Profile, history, memory (unqualified), context.
