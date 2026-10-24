from pathlib import Path

from typer.testing import CliRunner

from pagelens import __version__
from pagelens.cli import app


def test_init_and_status_do_not_load_models(tmp_path: Path) -> None:
    runner = CliRunner()
    data_dir = tmp_path / "collection"

    initialized = runner.invoke(app, ["init", "--data-dir", str(data_dir)])
    status = runner.invoke(app, ["status", "--data-dir", str(data_dir)])

    assert initialized.exit_code == 0
    assert (data_dir / "index.sqlite3").is_file()
    assert status.exit_code == 0
    assert "Documents: 0" in status.stdout


def test_version() -> None:
    result = CliRunner().invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout
