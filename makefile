SHELL := /bin/fish

runserver:
	@echo "Running server..."
	@python3 manage.py runserver

test: ## Run tests.
	@echo "--> Running tests"
	@pipenv run coverage erase
	@-pipenv run coverage run manage.py test --parallel=$(shell nproc)
	@pipenv run coverage combine > /dev/null
	@pipenv run coverage html
	@pipenv run coverage xml
	@pipenv run coverage report