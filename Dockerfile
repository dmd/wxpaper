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
# darksky-weather pins aiohttp==3.5.4, whose easy_install dependency resolution
# (used by setup.py install) ignores Requires-Python and grabs the latest yarl,
# which dropped Python 3.9 support. Pin a yarl that still ships a 3.9 wheel.
RUN pip install 'yarl<1.10' 'multidict<6.1'
RUN cd darksky-master && python setup.py install

RUN pip install sh

COPY pushmeplease.py wxpaper.py .

ENTRYPOINT /pushmeplease.py
