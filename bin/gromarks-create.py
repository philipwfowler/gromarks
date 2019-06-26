#! /usr/bin/env python

import argparse, pkg_resources, pathlib, os
import yaml
import math

aparser = argparse.ArgumentParser()
aparser.add_argument("--machine",default=None,help="the name of the YAML describing the machine configuration e.g. rescomp.F")
aparser.add_argument("--protein",default=None,help="the path to the benchmarking TPR file e.g. dhfr/rpob/peptst")
options = aparser.parse_args()

# since we've been given a relative path to the benchmarking TPR, split it and find out the name of the protein
(tpr_folder,tpr_filename)=os.path.split(options.protein)
protein=tpr_filename.split('.tpr')[0]

# now find and then load the YAML file
resource_package = __name__
resource_path = '/'.join(('../config/machines/', options.machine+".yaml"))  # Do not use os.path.join()
machine_file = pkg_resources.resource_filename(resource_package, resource_path)
with open(machine_file,'r') as f:
    machine_description=yaml.load(f)

# create the output path if it doesn't already exist
output_folder=""
for i in [protein, options.machine,machine_description["gromacs"]["version"]]:
    output_folder+=str(i)+"/"
    pathlib.Path(output_folder).mkdir(parents=True, exist_ok=True)

if 'list' in machine_description["cpu"].keys():
    list_number_cores=machine_description["cpu"]["list"]
else:
    # create a list containing the number of cores to consider as a doubling series
    power_of_2=int(math.log(machine_description["cpu"]["cores"])/math.log(2))
    list_number_cores= [ 2**i for i in range(0,power_of_2+1) ]

if machine_description["gpu"]["present"]:
    list_number_gpus = range(machine_description["gpu"]["min"],machine_description["gpu"]["max"])
else:
    # if no GPU create a list holding zero
    list_number_gpus=[0]

if 'list' in machine_description["node"].keys():
    list_number_nodes=machine_description["node"]["list"]
else:
    list_number_nodes=[1]

for nnode in list_number_nodes:

    # iterate over the number of GPUs
    for ngpu in list_number_gpus:

        for ntcore in list_number_cores:

            ntmpi=nnode*ntcore

            if machine_description["cpu"]["threads"]:
                power_of_2=int(math.log(machine_description["cpu"]["cores"]/ntmpi)/math.log(2))
                list_number_threads=[ 2**a for a in range(0,power_of_2+1) ]

            else:
                list_number_threads=[1]

            for ntomp in list_number_cores:

                if (ntmpi*ntomp)<=nnode*machine_description["cpu"]["cores"]:

                    stem=protein+'_'+options.machine+"_"+machine_description["gromacs"]["version"]+"_"+str(nnode)+"_"+str(ntcore)+"_"+str(ngpu)+"_"+str(ntomp)

                    line=""

                    if ngpu>0 and ntmpi==ngpu:
                        line=machine_description["gromacs"]["command"]

                    elif ngpu==0:

                        line=machine_description["gromacs"]["command"]

                        # if the machine has GPUs but we aren't using them, add flags to stop GROMACS automatically using any detected GPUs
                        if machine_description["gpu"]["present"] and machine_description["gpu"]["max"]>0:
                            line=line.replace("-noconfout","-noconfout -nb cpu")

                    if line!="":
                        OUTPUT=open(output_folder+"/"+stem+".sh","w")
                        line=line.replace("NTNODES",str(nnode))
                        line=line.replace("NTCORES",str(ntcore))
                        line=line.replace("NTGPU",str(ngpu))
                        line=line.replace("NTMPI",str(ntmpi))
                        line=line.replace("NTOMP",str(ntomp))
                        line=line.replace("TPRFILEPATH",options.protein)
                        line=line.replace("TPRFILE",str(stem))
                        line=line.replace("PROTEIN",protein)
                        OUTPUT.write(line+"\n")
                        OUTPUT.close()
