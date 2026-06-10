from app.agent.memory import InProcessMemory


def test_load_caps_at_max_turns():
    mem = InProcessMemory(max_turns=2)
    for n in range(3):  # three Turns; only the last two should survive
        mem.append("s", "user", f"u{n}")
        mem.append("s", "assistant", f"a{n}")

    hist = mem.load("s")

    # The oldest Turn (u0, a0) is dropped; the last two Turns remain in order.
    assert [m.content for m in hist] == ["u1", "a1", "u2", "a2"]


def test_sessions_are_isolated():
    mem = InProcessMemory()
    mem.append("s1", "user", "hello from s1")
    mem.append("s2", "user", "hello from s2")

    assert [m.content for m in mem.load("s1")] == ["hello from s1"]
    assert [m.content for m in mem.load("s2")] == ["hello from s2"]
    assert mem.load("never-seen") == []
