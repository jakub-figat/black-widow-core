format:
	docker-compose run --rm app bash -c "isort . && black ."

build-dev:
	docker-compose build

unit-test:
	docker-compose run --rm app bash -c "./scripts/unit-test.sh"

integration-test:
	docker-compose run --rm app bash -c "./scripts/unit-test.sh"

cov-report:
	docker-compose run --rm app bash -c "coverage report"

cov-html:
	docker-compose run --rm app bash -c "coverage html"