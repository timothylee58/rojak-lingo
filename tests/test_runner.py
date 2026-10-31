import json

from typer.testing import CliRunner

from rojak.eval.runner import app

runner = CliRunner()


def test_mock_run_scores_perfect_on_gold(tmp_path):
    result = runner.invoke(app, ["--mock", "--out-dir", str(tmp_path)])
    assert result.exit_code == 0, result.output
    summary = json.loads((tmp_path / "summary" / "oracle.json").read_text(encoding="utf-8"))
    metrics = summary["metrics"]
    assert metrics["intent"]["accuracy"] == 1.0
    assert metrics["instruct"]["pass_rate"] == 1.0
    assert metrics["normalize"]["chrf"] > 0.99
    assert metrics["translate"]["chrf"] > 0.99
