import json

import pytest

from pqos.experiments.runner import evaluate, generate_dataset, train


def test_end_to_end_and_resume(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = {
        "scenario": {"n_ues": 2, "resources": 2, "duration": 50, "warmup": 10},
        "split": {"train": [1000, 3], "validation": [2000, 1], "test": [3000, 1]},
        "selection": {"urgencies": [2.0], "horizons": [4]},
        "profiles": {"quick": {"episodes": 1, "workers": 2, "grid": {"load": [1.0]}}},
    }
    generate_dataset(config)
    train(config)
    path = evaluate(config)
    manifest = json.loads((path / "manifest.json").read_text())
    assert manifest["status"] == "complete"
    assert manifest["episodes"] == 14
    before = (path / "episode_metrics.csv").read_bytes()
    assert evaluate(config) == path
    assert before == (path / "episode_metrics.csv").read_bytes()
    assert len(list((path / "figures").glob("*.png"))) == 7
    assert (path / "REPORT.md").exists()
    demo = evaluate(config, demo=True)
    assert (demo / "REPORT.md").exists()
    assert (demo / "figures" / "timeline.png").exists()
    with pytest.raises(ValueError):
        train(config)
    with pytest.raises(ValueError):
        generate_dataset({**config, "scenario": {**config["scenario"], "resources": 3}})
    bad = {**config, "profiles": {"quick": {"episodes": 1, "seed_start": 2000}}}
    with pytest.raises(ValueError):
        evaluate(bad)
    checkpoint = next((path / "episodes").glob("*.json"))
    data = json.loads(checkpoint.read_text())
    data["metrics"]["trace_hash"] = "tampered"
    checkpoint.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        evaluate(config)


def test_cli_help(capsys, monkeypatch):
    from pqos.cli import main

    monkeypatch.setattr("sys.argv", ["pqos", "--help"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    assert "evaluate" in capsys.readouterr().out


def test_unknown_command(monkeypatch):
    from pqos.cli import main

    monkeypatch.setattr("sys.argv", ["pqos", "nonsense"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
