set dotenv-load := true

build:
    #!/bin/bash
    python -m pip install build
    python -m build --wheel

publish-test:
    twine upload \
        --repository-url "https://test.pypi.org/legacy/" \
        --username "$TEST_PYPI__TWINE_USERNAME" \
        --password "$TEST_PYPI__TWINE_PASSWORD" \
        dist/*

publish-prod:
    twine upload \
        --repository-url "https://upload.pypi.org/legacy/" \
        --username "$TWINE_USERNAME" \
        --password "$TWINE_PASSWORD" \
        dist/*

clean:
    rm -rf dist/
    