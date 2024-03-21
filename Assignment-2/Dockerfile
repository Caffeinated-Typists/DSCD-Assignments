FROM  python:alpine

ENV NODES=10.0.1.1,10.0.1.2,10.0.1.3,10.0.1.4,10.0.1.5
ENV RAFT_PORT=4444
ENV DB_PORT=5555
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /

# Copy the src folder to the working directory
COPY src/ /src

# Install python dependencies
RUN pip install --no-cache-dir -r /src/requirements.txt
