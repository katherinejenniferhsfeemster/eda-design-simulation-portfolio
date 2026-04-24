#!/usr/bin/env bash
set -e
mkdir -p out
ngspice -b ac_bode.cir     -o out/ac_bode.log
ngspice -b tran_step.cir   -o out/tran_step.log
ngspice -b monte_carlo.cir -o out/monte_carlo.log
ngspice -b noise.cir       -o out/noise.log
