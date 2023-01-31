FROM python:3.10

# Install poetry for dependency management
RUN pip install 'poetry'

WORKDIR /code

# Copy over the project files
COPY ./pyproject.toml /code/pyproject.toml
COPY ./poetry.lock /code/poetry.lock
COPY ./README.md /code/README.md
COPY ./python_rest_template /code/python_rest_template

# Install dependencies without creating a virtual environment (we're isolating dependencies in the container)
RUN poetry config virtualenvs.create false --local
RUN cd /code && poetry install

# Run the application. We'll deploy behind a reverse proxy so we don't need to worry about TLS (hence the --proxy-headers flag)
CMD ["uvicorn", "python_rest_template.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]

# Expose the http port
EXPOSE 80