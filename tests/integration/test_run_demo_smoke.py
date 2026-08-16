def test_main_runs_to_completion(monkeypatch, capsys):
    import matplotlib.pyplot as plt

    monkeypatch.setattr(plt, "show", lambda *args, **kwargs: None)

    from scripts.run_demo import main

    main()

    captured = capsys.readouterr()
    assert "Complete" in captured.out
