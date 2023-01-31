This is a template repository for building containerized REST API services in python using fastapi, postgres and docker.

Dependencies are managed using poetry and docker-compose.

# Usage
1. Clone this repository
2. Install dependencies: `make install`
3. Run the project locally: `make run`
## Development
1. To start the database and development server, run: `make dev`
2. To run tests interactively on file changes, run: `make watch`
3. To run tests once, run: `make test`
4. To run a particular test, run: `make this test=test_name`
5. To add a new database migration, run: `make add-migration name=migration_name`