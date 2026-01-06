import os
import sys
import subprocess
import pytest


@pytest.fixture
def repo_root():
    # shopyo/api/tests/test_integration_startapp.py -> shopyo/api/tests -> shopyo/api -> shopyo -> root
    # Adjust based on actual file location
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def test_startapp_integration(tmp_path, repo_root):
    env = os.environ.copy()
    env["PYTHONPATH"] = repo_root + os.pathsep + env.get("PYTHONPATH", "")

    project_name = "testproj"

    # 1. Create new project
    # python -m shopyo.api.cli new testproj
    cmd_new = [sys.executable, "-m", "shopyo.api.cli", "new", project_name]
    result = subprocess.run(
        cmd_new, cwd=tmp_path, env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, f"shopyo new failed: {result.stdout} {result.stderr}"

    # The project is created at tmp_path/testproj/testproj
    project_dir = tmp_path / project_name / project_name
    assert project_dir.exists()

    # 2. Start App
    module_name = "testmod"
    # python -m shopyo.api.cli startapp testmod
    cmd_startapp = [sys.executable, "-m", "shopyo.api.cli", "startapp", module_name]
    result = subprocess.run(
        cmd_startapp, cwd=project_dir, env=env, capture_output=True, text=True
    )
    assert (
        result.returncode == 0
    ), f"shopyo startapp failed: {result.stdout} {result.stderr}"

    # 3. Verify Endpoint
    verify_script = f"""
import sys
import os
sys.path.insert(0, os.getcwd())

# We need to make sure the repo's shopyo is used for imports if the new project relies on it
# But the new project has its own copy of shopyo source?
# shopyo new copies: shopyo/shopyo/* to testproj/testproj/*
# So testproj/testproj has 'app.py', 'init.py', etc.
# But 'from shopyo.api.module import ModuleHelp' is used in view.py
# That refers to installed 'shopyo' package.

from app import create_app

try:
    app = create_app('testing')
    client = app.test_client()
    response = client.get('/{module_name}/')
    if response.status_code == 200:
        print("SUCCESS")
    else:
        print(f"FAILURE: Status {{response.status_code}}")
        print(response.data.decode('utf-8'))
except Exception as e:
    print(f"EXCEPTION: {{e}}")
    import traceback
    traceback.print_exc()
"""
    verify_script_path = project_dir / "verify_app.py"
    verify_script_path.write_text(verify_script)

    cmd_verify = [sys.executable, "verify_app.py"]
    result = subprocess.run(
        cmd_verify, cwd=project_dir, env=env, capture_output=True, text=True
    )

    assert (
        "SUCCESS" in result.stdout
    ), f"Verification failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
