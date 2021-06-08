#!/bin/bash

mkdir $HOME/test-volume $HOME/results

RW="read  write  randread  randwrite"

for NUM_JOBS in 1 2 3
do
    echo -e "Jobs num: $NUM_JOBS\n"
    for BS in 512 2048 8192 32768 65536
    do
    	echo -e "Block size: $BS\n"
        for FIO_RW in $RW
        do
            echo -e "IO pattern: $FIO_RW\n"
            for i in 1 2 3
            do
                RUNTIME=30 FILESIZE=4G SIZE=4G NUM_JOBS=$NUM_JOBS FIO_RW=$FIO_RW \
                    taskset -c 0 fio fio_jobfile.fio \
                    --directory=$HOME/test-volume \
                    --output-format=json+ \
                    --blocksize=$BS \
                    --output=$HOME/results/bare-bare-$BS-$NUM_JOBS-$FIO_RW-$i.json
                rm $HOME/test-volume/*.dat
            done
        done
    done
done
