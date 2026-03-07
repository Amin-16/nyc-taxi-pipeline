FROM apache/airflow:2.9.3-python3.11

USER root
RUN apt-get update && apt-get install -y gcc python3-dev curl && apt-get clean

# Install uv as root
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set PYTHONPATH permanently
ENV PYTHONPATH=/opt/airflow

# Install dependencies as root with uv
COPY requirements.txt .
RUN UV_LINK_MODE=copy uv pip install --system --no-cache -r requirements.txt

USER airflow
