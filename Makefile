
install:
	python3 setup.py install

build:
	python3 setup.py build

deploy:
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*

clean:
	rm -rf build dist *egg*
