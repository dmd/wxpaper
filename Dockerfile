FROM python:3.9

RUN curl -sL https://particle.io/install-cli | bash
RUN ln -s /root/bin/particle /usr/local/bin/particle

ARG PARTICLE_TOKEN
RUN /root/bin/particle login --token $PARTICLE_TOKEN
RUN unset PARTICLE_TOKEN

COPY darksky-master.zip .
COPY forecast.patch .
COPY pirate-secret .

RUN unzip darksky-master.zip
RUN patch -p0 < forecast.patch
RUN cd darksky-master && python setup.py install

RUN pip install sh

COPY pushmeplease.py wxpaper.py .

ENTRYPOINT /pushmeplease.py
