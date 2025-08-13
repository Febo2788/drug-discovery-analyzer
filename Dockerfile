
# 1. Use an official Python runtime as a parent image
FROM python:3.9-slim

# 2. Set the working directory in the container
WORKDIR /app

# 3. Copy the requirements file into the container
COPY requirements.txt .

# 4. Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the cache, which reduces the image size.
# --trusted-host pypi.python.org: Can help avoid SSL issues in some networks.
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# 5. Copy the rest of the application code into the container
COPY . .

# 6. Make port 8501 available to the world outside this container
EXPOSE 8501

# 7. Define environment variables for Streamlit
# This tells Streamlit to run in headless mode (without opening a browser) and on the correct port.
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501

# 8. Run app.py when the container launches
CMD ["streamlit", "run", "app.py"]
