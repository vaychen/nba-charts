# === Python environment ===
env: uv.lock
	uv sync

update-env:
	uv lock --upgrade
	uv sync

uv.lock: pyproject.toml
	uv lock
