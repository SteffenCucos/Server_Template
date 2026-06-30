# test-scafold

This folder contains API tests that are run against a freshly generated scaffold app.

The GitHub Action installs the template CLI, runs `server-template new` into `test-scafold/app`, and then executes the tests in `test-scafold/tests` against both configured in-memory backends:

- `APP_DB_BACKEND=mongo` with `APP_DB_URI=memory://`
- `APP_DB_BACKEND=sqlite` with `APP_DB_URI=sqlite:///:memory:`

`test-scafold/app` is generated at CI/runtime and should not be committed.
