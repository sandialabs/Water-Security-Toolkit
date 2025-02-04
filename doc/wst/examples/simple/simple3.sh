#!/bin/sh

bin=`pwd`/../../../bin
pythonpath=`pwd`/../../../python/bin
export PATH=$bin:$pythonpath:$PATH

mkdir simple3
cd simple3
cp ../Net3* .

if [ ! -e Net3.erd ]; then
# @tevasim:
tevasim --tsg Net3.tsg Net3.inp Net3.out Net3 > tevasim.out
# @:tevasim
fi
cp data/Net3.erd .
cp data/Net3.index.erd data/Net3-1.hyd.erd data/Net3-1.qual.erd .

# @tso2Impact:
tso2Impact --responseTime 60 --detectionLimit 0.1 --mc Net3 Net3.erd
# @:tso2Impact

cd ..
\rm -Rf simple3
