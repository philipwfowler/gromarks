#! /usr/bin/env python

import argparse
import json
import math, os

aparser = argparse.ArgumentParser()
aparser.add_argument("--id",default=None,help="the name of the JSON describing the machine configuration e.g. rescomp.F")
aparser.add_argument("--protein",default=None,help="the name of the benchmarking TPR file e.g. dhfr/rpob/peptst")
options = aparser.parse_args()

standard_options=" -resethway -maxh 0.1 -noconfout -pin on"

# load the JSON file
with open("config/machines/"+options.id+".json",'r') as f:
    machine=json.load(f)

output_folder=options.protein+"-"+options.id

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

OUTPUT=open(output_folder+"/run.sh",'w')

OUTPUT.write("#! /bin/bash\n")
OUTPUT.write(""+"\n")

# source the relevant GMXRC
line = "source "+ machine["gromacs"]["path"]
OUTPUT.write(line+"\n")
OUTPUT.write(""+"\n")

power_of_2=int(math.log(machine["core-number"])/math.log(2))
number_cores= [ 2**i for i in range(0,power_of_2+1) ]

number_gpus = range(0,machine["gpu-number"]+1)

for ngpu in number_gpus:
    for ntmpi in number_cores:
        if (ntmpi*ngpu)<=machine["core-number"]:

            power_of_2=int(math.log(machine["core-number"]/ntmpi)/math.log(2))
            number_threads=[ 2**a for a in range(0,power_of_2+1) ]

            for ntomp in number_threads:
                line=""
                tpr_file=None
                if ngpu>0 and ntmpi==ngpu:
                    # print ngpu, ntmpi, ntomp
                    tpr_file=options.protein+'_'+options.id+"_"+machine["gromacs"]["version"]+"_"+str(ntmpi)+"_"+str(ngpu)+"_"+str(ntomp)
                    OUTPUT.write("cp ../config/tpr-files/"+options.protein+".tpr "+tpr_file+".tpr"+"\n")
                    line = "mpirun -np "+str(ntmpi)+" mdrun_mpi -deffnm "+tpr_file+" -ntomp "+str(ntomp)+standard_options+"\n"
                    OUTPUT.write(line+"\n")
                elif ngpu==0:
                    # print ngpu, ntmpi, ntomp
                    tpr_file=options.protein+'_'+options.id+"_"+machine["gromacs"]["version"]+"_"+str(ntmpi)+"_"+str(ngpu)+"_"+str(ntomp)
                    OUTPUT.write("cp ../config/tpr-files/"+options.protein+".tpr "+tpr_file+".tpr"+"\n")
                    if machine["gpu-number"]>0:
                        line = "mpirun -np "+str(ntmpi)+" mdrun_mpi -deffnm "+tpr_file+" -ntomp "+str(ntomp)+" -nb cpu"+standard_options+"\n"
                    else:
                        line = "mpirun -np "+str(ntmpi)+" mdrun_mpi -deffnm "+tpr_file+" -ntomp "+str(ntomp)+standard_options+"\n"
                    OUTPUT.write(line+"\n")


OUTPUT.close()
