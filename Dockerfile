# das image was ich haben will (latest)
FROM ubuntu:18.04

# ENV
ENV http_proxy 'http://www-cache.inf.h-brs.de:8080/'
ENV https_proxy 'http://www-cache.inf.h-brs.de:8080/'

# INSTALL PYTHON3.7 AND PIP3
RUN apt-get update && apt install -y python3-dev
RUN apt-get update && apt-get install -y --no-install-recommends \ 
    build-essential \
    python3-pip \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# INSTALL POSTGRES LIB 
RUN pip3 install --upgrade wheel
RUN apt-get update && apt-get install -y libpq-dev

# das stand noch unten als additional command 
#COPY . .

#----------------------------------------------------------------------------------------------
# INSTALL PACKAGES FOR PYTHON USING PIP3
# mein aktuelles Workingdirectory hiermit angeben (jeztt bin ich dort wo die Applikation liegt)
#WORKDIR /requirements

# diese file enthält die pip Downloads, die muss dann in /var/www/app liegen 
COPY /requirements/requirements.txt ./

# install pip packages in requirements.txt file 
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt 

# install neo4j package seperately (workaround to avoid an error) 
RUN pip3 install neo4j
RUN pip3 install psycopg2

#----------------------------------------------------------------------------------------------
# INSTALL JAVA 
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk && \
    apt-get install -y ant && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/oracle-jdk8-installer;

# Fix certificate issues, found as of 
# https://bugs.launchpad.net/ubuntu/+source/ca-certificates-java/+bug/983302
RUN apt-get update && \
	apt-get install -y ca-certificates-java && \
	apt-get clean && \
	update-ca-certificates -f;

# set environment variable 
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
# export variable and set git_python_refresh to warn, since an exception was raised when executing otherwise 
RUN export JAVA_HOME && \
    export GIT_PYTHON_REFRESH=warn

#---------------------------------------------------------------------------
# install git 
RUN apt-get update && \
    apt-get install -y git-core
#----------------------------------------------------------------------------------------------

# copy app into /usr/iasa/getProjectData
# source[Leerzeichen]destination
COPY /getProjectForTraceability /usr/iasa/getProjectDataForTraceability

# COPY boot.sh /usr/iasa

EXPOSE 5000

RUN useradd -ms /bin/bash iasa_user
USER iasa_user

# set current working directory 
WORKDIR /usr/iasa/getProjectDataForTraceability/control

CMD ["python3", "projectRestAPI.py"]





