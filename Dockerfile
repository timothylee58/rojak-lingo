FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -e .
COPY data ./data
COPY configs ./configs
ENTRYPOINT ["python", "-m", "rojak.eval.runner"]
