FROM google/cloud-sdk:latest

RUN apt-get install -y \
        build-essential \
        zlib1g-dev \
        libssl-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libffi-dev \
        locales \
        locales-all \
        mecab \
        libmecab-dev \
        mecab-ipadic-utf8 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/riywo/anyenv ~/.anyenv && \
    echo 'export PATH="$HOME/.anyenv/bin:$PATH"' >> ~/.bash_profile && \
    echo 'eval "$(anyenv init -)"' >> ~/.bash_profile

RUN /bin/bash -lc 'mkdir -p ~/.anyenv/plugins && \
    git clone https://github.com/znz/anyenv-update.git ~/.anyenv/plugins/anyenv-update'

RUN /bin/bash -lc 'anyenv install pyenv'

RUN /bin/bash -lc 'pyenv install 2.7.15 && \
    pyenv install 3.6.6 && \
    pyenv global 2.7.15 3.6.6'

RUN git clone --depth 1 https://github.com/chck/mecab-ipadic-neologd.git /tmp/neologd && \
    /tmp/neologd/bin/install-mecab-ipadic-neologd -n -u -y && \
    rm -rf /tmp/neologd

WORKDIR /app/identify/

COPY identify .

RUN /bin/bash -lc 'pip3 install -U pip setuptools==40.2.0 && \
    pip3 install -r requirements.txt'

ENV LANG="en_US.UTF-8" \
    LANGUAGE="en_US:en" \
    LC_ALL="en_US.UTF-8" \
    GOOGLE_APPLICATION_CREDENTIALS="/app/identify/identify/config/YOUR_GCLOUD_CREDENTIAL_JSON" \
    MECAB_DICDIR="/usr/lib/x86_64-linux-gnu/mecab/dic/mecab-ipadic-neologd"

CMD /bin/bash -lc "honcho start -f procfile $PROCESSES"
