import json
import sys
from datetime import datetime

import pytest

from log_parser import main
from log_parser.main import LogEntry


VALID_LINE = "2026-11-03 08:14:22 INFO Application started"
GARBAGE_LINE = "!!! truncated output from previous crash dump"


def sample_logs():
    return {
        "logs": [
            LogEntry(
                timestamp=datetime(2026, 11, 3, 8, 14, 22),
                loglevel="INFO",
                message="Application started",
            ),
            LogEntry(
                timestamp=datetime(2026, 11, 3, 9, 18, 17),
                loglevel="ERROR",
                message="Database connection timed out",
            ),
            LogEntry(
                timestamp=datetime(2026, 11, 3, 9, 18, 19),
                loglevel="INFO",
                message="Retrying database connection",
            ),
            LogEntry(
                timestamp=datetime(2026, 11, 4, 8, 3, 29),
                loglevel="ERROR",
                message="Database connection timed out",
            ),
            LogEntry(
                timestamp=datetime(2026, 11, 4, 14, 47, 2),
                loglevel="CRITICAL",
                message="Unhandled exception in payment worker",
            ),
        ],
        "garbage": ["bad line\n", "also bad\n"],
    }


def write_log(tmp_path, lines):
    log_file = tmp_path / "sample.log"
    log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return log_file


def test_parse_line_valid():
    result = main.parse_line(VALID_LINE)
    assert isinstance(result, LogEntry)
    assert result.loglevel == "INFO"
    assert result.message == "Application started"
    assert result.timestamp == datetime(2026, 11, 3, 8, 14, 22)


def test_parse_line_garbage():
    assert main.parse_line(GARBAGE_LINE) is None


def test_parse_line_empty():
    assert main.parse_line("") is None


def test_parse_line_unknown_level():
    assert main.parse_line("2026-11-03 08:14:22 FATAL boom") is None


def test_parse_line_invalid_datetime():
    assert main.parse_line("2026-13-99 99:99:99 INFO nope") is None


def test_parse_datetime_valid():
    assert main.parse_datetime("2026-11-03 08:14:22") == datetime(2026, 11, 3, 8, 14, 22)


def test_parse_datetime_invalid():
    assert main.parse_datetime("not-a-date") is None


def test_process_log_file_mix(tmp_path):
    log_file = write_log(
        tmp_path,
        [
            VALID_LINE,
            GARBAGE_LINE,
            "2026-11-03 09:18:17 ERROR Database connection timed out",
        ],
    )
    result = main.process_log_file(str(log_file))
    assert len(result["logs"]) == 2
    assert len(result["garbage"]) == 1
    assert isinstance(result["logs"][0], LogEntry)
    assert result["logs"][0].message == "Application started"


def test_process_log_file_missing():
    with pytest.raises(FileNotFoundError):
        main.process_log_file("this_file_does_not_exist.log")


def test_build_summary_counts():
    summary = main.build_summary(sample_logs())
    assert summary["total_valid"] == 5
    assert summary["skipped"] == 2
    assert summary["log_levels"] == {"INFO": 2, "ERROR": 2, "CRITICAL": 1}
    assert summary["first_timestamp"] == "2026-11-03 08:14:22"
    assert summary["last_timestamp"] == "2026-11-04 14:47:02"
    assert summary["top_messages"][0] == {
        "message": "Database connection timed out",
        "count": 2,
    }


def test_build_summary_no_valid_logs():
    assert main.build_summary({"logs": [], "garbage": ["bad line\n"]}) is None


def test_generate_report_has_text_and_json():
    report = main.generate_report(sample_logs())
    assert "LOGS REPORT" in report["text"]
    assert report["json"]["total_valid"] == 5
    assert "INFO : 2" in report["text"]
    assert "Database connection timed out : 2" in report["text"]


def test_generate_report_no_valid_logs():
    assert main.generate_report({"logs": [], "garbage": ["bad line\n"]}) is None


def test_write_report_txt(tmp_path, capsys):
    output = tmp_path / "report.txt"
    report = main.generate_report(sample_logs())
    main.write_report(str(output), report)
    contents = output.read_text(encoding="utf-8")
    assert "LOGS REPORT" in contents
    captured = capsys.readouterr()
    assert str(output) in captured.out


def test_write_report_json(tmp_path):
    output = tmp_path / "summary.json"
    report = main.generate_report(sample_logs())
    main.write_report(str(output), report)
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["total_valid"] == 5
    assert data["skipped"] == 2


def test_write_report_non_txt_writes_json(tmp_path, capsys):
    output = tmp_path / "report.csv"
    report = main.generate_report(sample_logs())
    main.write_report(str(output), report)
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["total_valid"] == 5
    captured = capsys.readouterr()
    assert str(output) in captured.out


def test_write_report_uses_suffix_not_substring(tmp_path):
    output = tmp_path / "notes.txt.json"
    report = main.generate_report(sample_logs())
    main.write_report(str(output), report)
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["total_valid"] == 5


def test_main_missing_log_exits(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    with pytest.raises(SystemExit) as exc:
        main.main()
    assert exc.value.code == 2


def test_main_missing_file_exits(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["main.py", "-l", "missing.log"])
    with pytest.raises(SystemExit) as exc:
        main.main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "missing.log" in captured.err
    assert captured.out == ""


def test_main_permission_error_exits(monkeypatch, capsys):
    def raise_permission_error(_path):
        raise PermissionError("Permission denied: 'locked.log'")

    monkeypatch.setattr(main, "process_log_file", raise_permission_error)
    monkeypatch.setattr(sys, "argv", ["main.py", "-l", "locked.log"])
    with pytest.raises(SystemExit) as exc:
        main.main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Permission denied" in captured.err
    assert captured.out == ""


def test_main_prints_and_writes_json(tmp_path, monkeypatch, capsys):
    log_file = write_log(tmp_path, [VALID_LINE, GARBAGE_LINE])
    output = tmp_path / "summary.json"
    monkeypatch.setattr(
        sys, "argv", ["main.py", "-l", str(log_file), "-o", str(output)]
    )
    main.main()
    captured = capsys.readouterr()
    assert "LOGS REPORT" in captured.out
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["total_valid"] == 1
    assert data["skipped"] == 1


def test_main_no_valid_data_skips_report(tmp_path, monkeypatch, capsys):
    log_file = write_log(tmp_path, [GARBAGE_LINE])
    output = tmp_path / "summary.json"
    monkeypatch.setattr(
        sys, "argv", ["main.py", "-l", str(log_file), "-o", str(output)]
    )
    main.main()
    captured = capsys.readouterr()
    assert "corrupted or has no valid data" in captured.err
    assert str(log_file) in captured.err
    assert captured.out == ""
    assert not output.exists()


def test_main_invalid_output_format(tmp_path, monkeypatch, capsys):
    log_file = write_log(tmp_path, [VALID_LINE])
    output = tmp_path / "report.csv"
    monkeypatch.setattr(
        sys, "argv", ["main.py", "-l", str(log_file), "-o", str(output)]
    )
    main.main()
    captured = capsys.readouterr()
    assert "LOGS REPORT" in captured.out
    assert "Invalid file format" in captured.err
    assert not output.exists()
