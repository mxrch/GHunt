.PHONY: lint
lint:
	flake8 ./ --exclude .venv,*_pb2.py --max-line-length=150 --ignore=F403,F405,F541

.PHONY: format
format:
	autopep8 --in-place --aggressive --aggressive --recursive ./ --exclude .venv,*_pb2.py --max-line-length=150
	autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables ./ --exclude .venv
