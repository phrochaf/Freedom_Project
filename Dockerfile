# Step 1: Start with an official Python base image.
# We choose a 'slim' version which is smaller and good for production.
FROM python:3.12-slim

# Step 2: Set the working directory inside the container.
# All subsequent commands will be run from /app.
WORKDIR /app

# Step 3: Copy the requirements file into the container.
# This is done first to leverage Docker's layer caching.
# If our requirements don't change, Docker won't need to reinstall them on every build.
COPY requirements.txt .

# Step 4: Install the Python dependencies inside the container.
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the rest of our application code into the container.
# This includes the 'src' folder, 'app.py', 'templates', etc.
COPY . .

# Step 6: Expose the port that Flask runs on.
# This is more for documentation; the actual port mapping is done when we run the container.
EXPOSE 5000

# Step 7: Define the command to run when the container starts.
# This will start the Flask development server.
# We use --host=0.0.0.0 to make the server accessible from outside the container.
CMD ["flask", "run", "--host=0.0.0.0"]