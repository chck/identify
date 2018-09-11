FROM google/cloud-sdk:latest

RUN apt-get install -y \
        build-essential \
        zlib1g-dev \
        libssl-dev \
        libbz2-dev \
        libreadline-dev \
        libsqlite3-dev \
        libffi-dev && \
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
   
WORKDIR /app/seeking/

COPY seeking/ .

RUN /bin/bash -lc 'pip3 install -U pip setuptools==40.2.0 && \
    pip3 install -r requirements.txt'

CMD honcho start -f /app/seeking/procfile $PROCESSES