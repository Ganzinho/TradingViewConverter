# Start your image with a node base image
FROM python:3.9

# The /app directory should act as the main application directory
WORKDIR /app

# Copy the app requirements file
COPY requirements.txt requirements.txt

# Install node packages, install serve, build the app, and remove dependencies at the end
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

ENTRYPOINT [ "python" ]

# Start the app using serve command
CMD ["app.py"]