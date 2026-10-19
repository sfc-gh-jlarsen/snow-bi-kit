"""Offline tests for snow-bi-kit (no Snowflake connection needed).

    python -m pytest tests -q
"""

import json
import os
import sys

import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "plugin", "runtime"))
sys.path.insert(0, os.path.join(ROOT, "plugin", "scripts"))

import bi_kit_runtime as bi  # noqa: E402
import scan_secrets  # noqa: E402
import standards  # noqa: E402
import verify_app  # noqa: E402

FIX = os.path.join(ROOT, "tests", "fixtures")


# ----------------------------------------------------------------- fake Snowflake session

class FakeCursor:
    def __init__(self, frames, log):
        self.frames, self.log, self.sfqid = frames, log, None

    def execute(self, sql, params=None):
        self.log.append((sql, params))
        self.sfqid = f"qid-{len(self.log)}"
        self._df = self.frames(sql, params)

    def fetch_pandas_all(self):
        return self._df.copy()

    def close(self):
        pass


class FakeConnection:
    def __init__(self, frames, log):
        self.frames, self.log = frames, log

    def cursor(self):
        return FakeCursor(self.frames, self.log)


class FakeSession:
    def __init__(self, frames):
        self.log = []
        self.connection = FakeConnection(frames, self.log)


def sales_frame(sql, params):
    return pd.DataFrame({"MONTH": ["2025-01", "2025-02", "2025-03"], "NET_SALES": [100.0, 120.0, 90.0]})


@pytest.fixture(autouse=True)
def fresh_runtime(monkeypatch):
    monkeypatch.delenv("BI_KIT_DEBUG", raising=False)
    bi.configure(FakeSession(sales_frame), debug=True)
    yield


# ----------------------------------------------------------------- runtime

def rolling(df):
    df["ROLL"] = df["NET_SALES"].rolling(2, min_periods=1).mean()
    return df


def test_run_visual_records_sql_params_transform_and_query_id():
    run = bi.run_visual("Trend", "  SELECT 1  ", params=["NA"], transform=rolling, library_entry="line", sources=["S"])
    assert run.sql == "SELECT 1"
    assert run.params == ["NA"]
    assert run.query_id == "qid-1"
    assert "def rolling" in run.transform_source
    assert list(run.data.columns) == ["MONTH", "NET_SALES", "ROLL"]
    assert run.raw_rows == 3 and len(run.data) == 3
    assert run in bi.runs()


def test_self_check_passes_for_deterministic_data_even_if_row_order_changes():
    calls = {"n": 0}

    def shuffled(sql, params):
        calls["n"] += 1
        df = sales_frame(sql, params)
        return df.iloc[::-1].reset_index(drop=True) if calls["n"] > 1 else df

    bi.configure(FakeSession(shuffled), debug=True)
    run = bi.run_visual("Trend", "SELECT 1")
    assert bi.self_check(run) is True


def test_self_check_catches_changed_results():
    calls = {"n": 0}

    def drifting(sql, params):
        calls["n"] += 1
        df = sales_frame(sql, params)
        df["NET_SALES"] += calls["n"]  # different every run, like CURRENT_TIMESTAMP or RANDOM()
        return df

    bi.configure(FakeSession(drifting), debug=True)
    run = bi.run_visual("Trend", "SELECT 1")
    assert bi.self_check(run) is False


def test_tie_out_matches_within_tolerance_and_flags_differences():
    run = bi.run_visual("Total", "SELECT 1")
    assert bi.tie_out(run, "NET_SALES", expected=310.0)["status"] == "matches"
    t = bi.tie_out(run, "NET_SALES", expected=400.0)
    assert t["status"] == "differs" and t["diff"] == pytest.approx(-90.0)


def test_env_var_turns_debug_off_for_production(monkeypatch):
    monkeypatch.setenv("BI_KIT_DEBUG", "0")
    bi.configure(FakeSession(sales_frame), debug=True)
    run = bi.run_visual("Trend", "SELECT 1")
    assert bi.debug_enabled() is False
    assert bi.html_details(run) == ""


def test_html_details_escapes_and_includes_python_step():
    run = bi.run_visual("<Trend>", "SELECT '<b>' AS x", transform=rolling)
    out = bi.html_details(run)
    assert out.startswith("<details")
    assert "&lt;b&gt;" in out and "'<b>'" not in out
    assert "&lt;Trend&gt;" in out
    assert "Python processing" in out


def test_manifest_has_no_data_values(tmp_path):
    bi.run_visual("Trend", "SELECT 1", transform=rolling)
    path = bi.write_manifest(str(tmp_path / "runs.json"))
    payload = json.load(open(path))
    assert payload[0]["sql"] == "SELECT 1"
    assert "100.0" not in json.dumps(payload)


def test_configure_required():
    bi._STATE["session"] = None
    with pytest.raises(RuntimeError):
        bi.run_visual("x", "SELECT 1")


# ----------------------------------------------------------------- verify_app

def test_verifier_flags_direct_rendering_and_raw_sql():
    findings = verify_app.check_file(os.path.join(FIX, "leaky_app", "streamlit_app.py"))
    text = "\n".join(findings)
    assert "st.metric()" in text and "st.bar_chart()" in text and "session.sql()" in text


def test_verifier_passes_clean_app():
    assert verify_app.check_file(os.path.join(FIX, "clean_app", "streamlit_app.py")) == []


def test_verifier_passes_gallery():
    assert verify_app.check_file(os.path.join(ROOT, "gallery", "streamlit_app.py")) == []


# ----------------------------------------------------------------- secret scan

def test_scan_catches_seeded_password_admin_role_and_user():
    findings = scan_secrets.scan(os.path.join(FIX, "leaky_app"))
    rules = {f["rule"] for f in findings if not f["rule"].startswith("gitleaks")}
    assert {"hardcoded-password", "admin-role-in-code", "hardcoded-user"} <= rules
    assert all("Tr1ck" not in json.dumps(f) for f in findings), "findings must never echo the secret"


def test_scan_clean_app_has_no_findings():
    assert scan_secrets.scan(os.path.join(FIX, "clean_app")) == []


def test_scan_ignores_secrets_read_from_environment(tmp_path):
    (tmp_path / "app.py").write_text('password = os.environ["SF_PASSWORD"]\ntoken = st.secrets["tok"]\n')
    assert scan_secrets.scan(str(tmp_path)) == []


def test_scan_flags_env_file(tmp_path):
    (tmp_path / ".env").write_text("NOTHING=1\n")
    assert any(f["rule"] == "env-file" for f in scan_secrets.scan(str(tmp_path)))


# ----------------------------------------------------------------- standards

def test_template_reports_required_keys_missing():
    doc = standards.load(os.path.join(ROOT, "plugin", "standards", "company-standards.template.yaml"))
    assert set(standards.missing(doc)) == set(standards.REQUIRED)


def test_example_is_complete():
    doc = standards.load(os.path.join(ROOT, "plugin", "standards", "company-standards.example.yaml"))
    assert standards.missing(doc) == []


def test_project_standards_take_precedence(tmp_path):
    (tmp_path / "bi-kit").mkdir()
    p = tmp_path / "bi-kit" / "company-standards.yaml"
    p.write_text("company: {name: X}\n")
    assert standards.find(str(tmp_path)) == str(p)


def test_gallery_brand_matches_example_standards():
    doc = standards.load(os.path.join(ROOT, "plugin", "standards", "company-standards.example.yaml"))
    gallery = json.load(open(os.path.join(ROOT, "gallery", "bi_kit_brand.json")))
    for k, v in gallery.items():
        assert doc["brand"][k] == v, k
