FROM pytorch/pytorch:2.6.0-cuda12.4-cudnn9-runtime

# Install system dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y apt-utils build-essential curl wget zip unzip git make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /workspace/code

# Install pip and setuptools
RUN pip install --upgrade pip setuptools

# Copy Repo
COPY pyproject.toml .
COPY src ./src

# Install the dependencies from pyproject.toml
RUN pip install -e .[dev]

# Expose any ports the app is expected to run on
EXPOSE 8880 6006

# Define the command to run the application or start a Jupyter notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8880", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
