FROM alpine

RUN apk --no-cache add \
    	make \
	alpine-sdk \
	zlib-dev \
	libaio-dev \
	linux-headers \
	coreutils \
	libaio && \
    git clone https://github.com/axboe/fio && \
    cd fio && \
    ./configure && \
    make -j`nproc` && \
    make install && \
    cd .. && \
    rm -rf fio && \
    apk --no-cache del \
    	make \
	alpine-sdk \
	zlib-dev \
	libaio-dev \
	linux-headers \
	coreutils

COPY test.sh test.sh
COPY fio_jobfile.fio .
RUN mkdir results
RUN mkdir test-volume
ENTRYPOINT sh test.sh
#CMD sh test.sh
