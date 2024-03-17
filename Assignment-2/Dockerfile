FROM  python:alpine

# Set the working directory
WORKDIR /

# Copy the src folder to the working directory
COPY src/ /src

# Install python dependencies
RUN pip install --no-cache-dir -r /src/requirements.txt

CMD [ "python" , "/src/raft.py"]

