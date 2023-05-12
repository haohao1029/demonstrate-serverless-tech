FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

# Set up app directory
WORKDIR /app

# Copy app code
COPY . /app

# Install app dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Start app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]