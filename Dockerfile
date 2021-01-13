# set base image (host OS)
FROM python:3.8

# set the working directory in the container
RUN mkdir /django
WORKDIR /django



# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY djangoserver/ ./djangoserver/
COPY socialnetwork/ ./socialnetwork/
COPY testbot/ ./testbot/
COPY manage.py .

# command to run on container start
RUN python ./manage.py makemigrations
RUN python ./manage.py migrate

EXPOSE 8000
CMD [ "python", "./manage.py", "runserver", "0.0.0.0:8000"]
