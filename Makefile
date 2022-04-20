format:
	docker-compose run --rm app bash -c "isort . && black ."

check:
	docker-compose run --rm app bash -c "prospector ."

build-dev:
	docker-compose build

app-bash:
	docker-compose run --rm app bash

unit-test:
	docker-compose run --rm app bash -c "./scripts/unit-test.sh"

integration-test:
	docker-compose run --rm app bash -c "./scripts/integration-test.sh"

cov-report:
	docker-compose run --rm app bash -c "coverage report"

cov-html:
	docker-compose run --rm app bash -c "coverage html"