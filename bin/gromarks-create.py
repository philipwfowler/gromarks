#! /usr/bin/env python

import argparse, pkg_resources
import yaml
import math, os

aparser = argparse.ArgumentParser()
aparser.add_argument("--id",default=None,help="the name of the YAML describing the machine configuration e.g. rescomp.F")
aparser.add_argument("--protein",default=None,help="the path to the benchmarking TPR file e.g. dhfr/rpob/peptst")
options = aparser.parse_args()

(tpr_folder,tpr_filename)=os.path.split(options.protein)

protein=tpr_filename.split('.tpr')[0]

resource_package = __name__
resource_path = '/'.join(('../config/machines/', options.id+".yaml"))  # Do not use os.path.join()
machine_file = pkg_resources.resource_filename(resource_package, resource_path)

# load the YAML file
with open(machine_file,'r') as f:
    machine=yaml.load(f)

assert machine["how-run"] in ["bash","scheduler"], "how-run not set correctly in YAML file, must be one of bash/scheduler"

output_folder=protein+"-"+options.id

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

                stem=protein+'_'+options.id+"_"+machine["gromacs"]["version"]+"_"+str(ntmpi)+"_"+str(ngpu)+"_"+str(ntomp)

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

                    if machine["gpu-number"]>0:
                        line=line.replace("-noconfout","-noconfout -nb cpu")

                if line!="":
                    line=line.replace("NTMPI",str(ntmpi))
                    line=line.replace("NTOMP",str(ntomp))
                    line=line.replace("TPRFILEPATH",options.protein)
                    line=line.replace("TPRFILE",str(stem))
                    line=line.replace("PROTEIN",protein)
                    OUTPUT.write(line+"\n")

                if machine["how-run"]=="scheduler" and line !="":
                    OUTPUT.close()

if machine["how-run"]=="bash":
    OUTPUT.close()
