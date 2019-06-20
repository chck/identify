FROM google/cloud-sdk:slim

RUN apt-get update && apt-get install -y \
        python3-tk \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/identify/

COPY identify .

RUN /bin/bash -lc 'pip3 install -U pip setuptools && \
    pip3 install -r requirements.txt'

ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US:en" \
    LC_ALL="en_US.UTF-8" \
    GOOGLE_APPLICATION_CREDENTIALS="/app/identify/identify/config/YOUR_GCLOUD_CREDENTIAL_JSON" \

CMD /bin/bash -lc "honcho start -f procfile $PROCESSES"
