#! /usr/bin/env python

import argparse
import json
import math, os

aparser = argparse.ArgumentParser()
aparser.add_argument("--id",default=None,help="the name of the input csv file")
aparser.add_argument("--protein",default=None,help="the name of the input csv file")
options = aparser.parse_args()

# standard_options=" -resethway -maxh 0.1 -noconfout -pin on"

# load the JSON file
with open("machines/"+options.id+".json",'r') as f:
    machine=json.load(f)

output_folder=options.protein+"-"+options.id

power_of_2=int(math.log(machine["core-number"])/math.log(2))
number_cores= [ 2**i for i in range(0,power_of_2+1) ]

number_gpus = range(0,machine["gpu-number"]+1)

for ngpu in number_gpus:
    if ngpu>0:
        gpu_type="%i x %s" % (ngpu,machine["gpu-type"])
    else:
        gpu_type="-"

    for ntmpi in number_cores:
        power_of_2=int(math.log(machine["core-number"]/ntmpi)/math.log(2))
        number_threads=[ 2**a for a in range(0,power_of_2+1) ]

        output_line="%15s, %7i, %12s, %10s, %3i, %3i," % (machine['id'],machine['core-number'],gpu_type,machine['gromacs']['version'],ntmpi,ngpu)
        print_line=False
        for ntomp in number_threads:
            log_file = output_folder+"/"+options.protein+'_'+options.id+"_"+machine["gromacs"]["version"]+"_"+str(ntmpi)+"_"+str(ngpu)+"_"+str(ntomp)+".log"
            if os.path.exists(log_file):
                with open(log_file,'r') as file:
                    for line in file:
                        if line:
                            cols=line.split()
                            if cols and cols[0]=="Performance:":
                                print_line=True
                                output_line+= " %7.2f, " % (float(cols[1]))

        if print_line:
            print(output_line)

                # print ngpu, ntmpi, ntomp
            #     tpr_file=options.protein+'_'+options.id+"_"+machine["gromacs"]["version"]+"_"+str(ntmpi)+"_"+str(ngpu)+"_"+str(ntomp)
            #     print >> OUTPUT, "cp ../tpr-files/"+options.protein+".tpr "+tpr_file+".tpr"
            #     line = "mpirun -np "+str(ntmpi)+" mdrun_mpi -deffnm "+tpr_file+" -ntomp "+str(ntomp)+standard_options+"\n"
            #     print >> OUTPUT, line
            # elif ngpu==0:
            #     # print ngpu, ntmpi, ntomp
            #     tpr_file=options.protein+'_'+options.id+"_"+machine["gromacs"]["version"]+"_"+str(ntmpi)+"_"+str(ngpu)+"_"+str(ntomp)
            #     print >> OUTPUT, "cp ../tpr-files/"+options.protein+".tpr "+tpr_file+".tpr"
            #     if machine["gpu-number"]>0:
            #         line = "mpirun -np "+str(ntmpi)+" mdrun_mpi -deffnm "+tpr_file+" -ntomp "+str(ntomp)+" -nb cpu"+standard_options+"\n"
            #     else:
            #         line = "mpirun -np "+str(ntmpi)+" mdrun_mpi -deffnm "+tpr_file+" -ntomp "+str(ntomp)+standard_options+"\n"
            #     print >> OUTPUT, line
