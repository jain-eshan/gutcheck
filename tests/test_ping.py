import server


def test_ping_sends_only_with_consent(monkeypatch, tmp_path):
    sent = []
    monkeypatch.setattr(server, "_send_ping", sent.append)
    monkeypatch.setattr(server.threading, "Thread", lambda target, args, daemon: type("T", (), {"start": lambda self: target(*args)})())
    monkeypatch.setattr(server, "CONFIG_DIR", str(tmp_path))
    monkeypatch.delenv("GUTCHECK_TELEMETRY_ID", raising=False)
    monkeypatch.setattr(server, "ping_enabled", True)

    server.ping("news_coverage")
    assert sent == []  # no id saved means no consent

    (tmp_path / ".env").write_text("GUTCHECK_TELEMETRY_ID=abc\n")
    monkeypatch.setattr(server, "ping_enabled", False)
    server.ping("news_coverage")
    assert sent == []  # doctor, call and tests never ping

    monkeypatch.setattr(server, "ping_enabled", True)
    server.ping("news_coverage")
    assert sent[0]["distinct_id"] == "abc"
    assert sent[0]["properties"] == {"tool": "news_coverage", "version": server.VERSION, "$process_person_profile": False}
