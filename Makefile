VENV_DIR = .venv

dist:
	${VENV_DIR}/bin/hatch build

clean:
	rm -rf build
	rm -rf dist
	rm -rf thronescli.egg-info
	rm -rf __pycache__

upload:
	${VENV_DIR}/bin/twine upload dist/*

release: clean version dist upload

format:
	black thronescli.py

lint:
	black --check thronescli.py

venv:
	python3 -m venv ${VENV_DIR}
	${VENV_DIR}/bin/pip install hatch black
