version := $(shell python -c 'from thronescli.thronescli import __version__; print __version__')

dist:
	python2 setup.py bdist_wheel bdist_egg
	python3 setup.py bdist_wheel

version:
	git add thronescli/thronescli.py
	git commit -m'Version ${version}'
	git tag ${version}
	git push --tags origin master

clean:
	rm -rf build
	rm -rf dist
	rm -rf thronescli.egg-info
	rm -rf thronescli/__pycache__

upload:
	twine upload dist/*

release: clean version dist upload
