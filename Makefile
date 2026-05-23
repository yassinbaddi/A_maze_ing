
NAME = a_maze_ing.py
CONFIG_FILE = config.txt


run:
	@python3 $(NAME) $(CONFIG_FILE)


install:
	pip install getch
	pip install mlx-*.whl


debug:
	python3 -m pdb $(NAME)


lint:
	flake8 .
	mypy . --explicit-package-bases

build:
# 	@python3 -m pip install --quiet --upgrade build
	@python3 -m build


clean:
	rm -rf */__pycache__ 
	rm -rf .mypy_cache


.PHONY: install run debug lint build clean