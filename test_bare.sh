#!/bin/bash

mkdir test-volume results

RW="read  write  randread  randwrite"

for NUM_JOBS in 1 2 3
do
    echo -e 'Jobs num: $NUM_JOBS\n'		
    for BS in 512 1024 2048 4096 8192 16384 32768 65536
    do
    	echo -e 'Block size: $BS\n'
        for FIO_RW in $RW
        do
            echo -e 'IO pattern: $FIO_RW\n'
            for i in 1 2 3
            do
                RUNTIME=30 FILESIZE=2G SIZE=2G NUM_JOBS=$NUM_JOBS FIO_RW=$FIO_RW \
                    fio fio_jobfile.fio \
                    --directory=/test-volume \
                    --output-format=json+ \
                    --blocksize=$BS \
                    --output=/results/$VOLUME-bare-$BS-$NUM_JOBS-$FIO_RW-$i.json
                rm -rf $DIR/*.dat
            done
        done
    done
done
