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

assert machine["how-run"] in ["bash","scheduler"], "how-run not set correctly in JSON file, must be one of bash/scheduler"

output_folder=options.protein+"-"+options.id

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# source the relevant GMXRC
if machine["how-run"]=="bash":
    OUTPUT=open(output_folder+"/run.sh",'w')

    OUTPUT.write("#! /bin/bash\n")
    OUTPUT.write(""+"\n")

    line = "source "+ machine["gromacs"]["path"]
    OUTPUT.write(line+"\n")
    OUTPUT.write(""+"\n")


power_of_2=int(math.log(machine["core-number"])/math.log(2))
number_cores= [ 2**i for i in range(0,power_of_2+1) ]

if machine["gpu-number"]>0:
    number_gpus = range(machine["gpu-number-min"],machine["gpu-number"]+1)
else:
    number_gpus=[0]

# iterate over the number of GPUs
for ngpu in number_gpus:

    for ntmpi in number_cores:

        power_of_2=int(math.log(machine["core-number"]/ntmpi)/math.log(2))
        number_threads=[ 2**a for a in range(0,power_of_2+1) ]

        for ntomp in number_threads:

            if (ntmpi*ntomp)<=machine["core-number"]:

                stem=options.protein+'_'+options.id+"_"+machine["gromacs"]["version"]+"_"+str(ntmpi)+"_"+str(ngpu)+"_"+str(ntomp)

                line=""

                if ngpu>0 and ntmpi==ngpu:

                    if machine["how-run"]=="scheduler":
                        OUTPUT=open(output_folder+"/"+stem+".sh","w")
                        line=machine["gromacs"]["header"]
                        line+="\n"
                        line+=machine["gromacs"]["module-cmds"]
                        line+="\n"
                        line+=machine["gromacs"]["command"]

                    else:
                        line=""

                elif ngpu==0:

                    if machine["how-run"]=="scheduler":
                        OUTPUT=open(output_folder+"/"+stem+".sh","w")
                        line=machine["gromacs"]["header"]
                        line+="\n"
                        line+=machine["gromacs"]["module-cmds"]
                        line+="\n"
                        line+=machine["gromacs"]["command"]
                    else:
                        line+=machine["gromacs"]["command"]


                    # print ngpu, ntmpi, ntomp

                    if machine["gpu-number"]>0:
                        line += " -nb cpu"

                if line!="":
                    line=line.replace("NTMPI",str(ntmpi))
                    line=line.replace("NTOMP",str(ntomp))
                    line=line.replace("TPRFILE",str(stem))
                    line=line.replace("PROTEIN",options.protein)
                    print(line)
                    OUTPUT.write(line+"\n")

                if machine["how-run"]=="scheduler" and line !="":
                    OUTPUT.close()

if machine["how-run"]=="bash":
    OUTPUT.close()
