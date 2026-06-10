from app.agent.memory import InProcessMemory


def test_load_caps_at_max_turns():
    mem = InProcessMemory(max_turns=2)
    for n in range(3):  # three Turns; only the last two should survive
        mem.append(session_id="s", user_id="u", role="user", content=f"u{n}")
        mem.append(session_id="s", user_id="u", role="assistant", content=f"a{n}")

    hist = mem.load(session_id="s", user_id="u")

    # The oldest Turn (u0, a0) is dropped; the last two Turns remain in order.
    assert [m.content for m in hist] == ["u1", "a1", "u2", "a2"]


def test_sessions_are_isolated():
    mem = InProcessMemory()
    mem.append(session_id="s1", user_id="u", role="user", content="hello from s1")
    mem.append(session_id="s2", user_id="u", role="user", content="hello from s2")

    assert [m.content for m in mem.load(session_id="s1", user_id="u")] == ["hello from s1"]
    assert [m.content for m in mem.load(session_id="s2", user_id="u")] == ["hello from s2"]
    assert mem.load(session_id="never-seen", user_id="u") == []


def test_preference_preamble_spans_conversations_per_user():
    mem = InProcessMemory()
    # User U speaks across two different Conversations (session ids).
    mem.append(session_id="A", user_id="U", role="user", content="quiet study spot with outlets")
    mem.append(session_id="A", user_id="U", role="assistant", content="...")
    mem.append(session_id="B", user_id="U", role="user", content="something cheap")

    preamble = mem.preference_preamble(user_id="U")
    assert preamble is not None
    assert "quiet study spot with outlets" in preamble
    assert "something cheap" in preamble


def test_preference_preamble_is_none_for_new_user():
    mem = InProcessMemory()
    assert mem.preference_preamble(user_id="nobody") is None


def test_preference_preamble_is_per_user():
    mem = InProcessMemory()
    mem.append(session_id="A", user_id="alice", role="user", content="alice wants tea")
    mem.append(session_id="B", user_id="bob", role="user", content="bob wants espresso")

    alice = mem.preference_preamble(user_id="alice")
    assert alice is not None
    assert "alice wants tea" in alice
    assert "bob wants espresso" not in alice


def test_get_memory_defaults_to_in_process(monkeypatch):
    from app.agent import memory as memmod

    # Default config selects the in-process implementation.
    assert isinstance(memmod.get_memory(), InProcessMemory)


def test_get_memory_falls_back_when_zep_selected_but_unavailable(monkeypatch):
    from app.agent import memory as memmod

    class _S:
        agent_memory_impl = "zep"
        zep_api_key = "zk_test"

    monkeypatch.setattr(memmod, "get_settings", lambda: _S())
    # ZepMemory is a stub that raises on construction, so get_memory must fall back.
    assert isinstance(memmod.get_memory(), InProcessMemory)
