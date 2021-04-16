#!/bin/bash
set -ea

# Build configuration script.
echo "# config_test.job" > config_test.job
echo ". r.load.dot comm/eccc/all/opt/intelcomp/intelpsxe-cluster-19.0.3.199" >> config_test.job
#if [ $(echo $1 | grep -ic mpi) -ne 0 ]
#then
#    echo ". ssmuse-sh -x hpco/exp/openmpi/openmpi-3.1.2--hpcx-2.4.0-mofed-4.6--intel-19.0.3.199" >> config_test.job
#    echo ". ssmuse-sh -x hpco/exp/openmpi-setup/openmpi-setup-0.1" >> config_test.job
#else
    echo ". r.load.dot comm/eccc/all/opt/intelcomp/intelpsxe-cluster-19.0.3.199" >> config_test.job
#fi
#if [ $(echo $1 | grep -ic netcdf) -ne 0 ]
#then
#    echo ". ssmuse-sh -d eccc/cmd/cmds/ext/master" >> config_test.job
#fi
#echo "$(pwd -P)/run_test.sh $1 $2 $(pwd -P)" >> config_test.job

echo ". r.load.dot rpn/libs/19.3" >> config_test.job
echo ". r.load.dot rpn/utils/19.3" >> config_test.job
echo ". ssmuse-sh -d eccc/mrd/rpn/MIG/ENV/x/rpnpy/2.1-u1.rc2" >> config_test.job

echo "cd $(pwd -P)" >> config_test.job
#echo "python extract_points_rdps-11950_2004-05-19.py" >> config_test.job
#echo "python extract_points_rdps-12000_2011-09-30.py" >> config_test.job
echo "python extract_points_rdpa_2002-01-01.py" >> config_test.job
#echo "python extract_points_rdrs_2000-01-01.py" >> config_test.job

# Submit job.
#if [ $(echo $1 | grep -ic mpi) -ne 0 ]
#then
#    ord_soumet $(pwd -P)/config_test.job -mail -cpus 14 -cm 2G -t 3600 -mach eccc-ppp3
#else
    ord_soumet $(pwd -P)/config_test.job -mail -cpus 1 -cm 2G -t 21600 -mach eccc-ppp3
#fi
