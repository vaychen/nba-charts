.PHONY: update-env env uv-lock jupyter-notebook

# === Python environment ===
update-env:
	uv lock --upgrade
	uv sync

uv.lock: pyproject.toml
	uv lock

env: uv.lock
	uv sync

jupyter-notebook:
	jupyter notebook
