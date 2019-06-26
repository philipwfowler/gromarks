#! /usr/bin/env python

import argparse, pkg_resources
import json
import math, os

aparser = argparse.ArgumentParser()
aparser.add_argument("--machine",default=None,help="the name of the JSON describing the machine configuration e.g. rescomp.F")
aparser.add_argument("--protein",default=None,help="the name of the benchmarking TPR file e.g. dhfr/rpob/peptst")
options = aparser.parse_args()

protein=options.protein

resource_package = __name__
resource_path = '/'.join(('../config/machines/', options.machine+".json"))  # Do not use os.path.join()
machine_file = pkg_resources.resource_filename(resource_package, resource_path)

# load the JSON file
with open(machine_file,'r') as f:
    machine=json.load(f)

output_folder=options.protein+"-"+options.machine

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

    for ngpu in list_number_gpus:

        if ngpu>0:
            gpu_type="%i x %s" % (ngpu,machine["gpu-type"])
        else:
            gpu_type="-"

        for ntcore in list_number_cores:

            output_line="%15s, %7i, %12s, %10s, %3i, %3i," % (machine['id'],machine['core-number'],gpu_type,machine['gromacs']['version'],ntnode,ntcore,ngpu)
            print_line=False

            for ntomp in list_number_cores:

                log_file =options.protein+'_'+options.machine+"_"+machine_description["gromacs"]["version"]+"_"+str(nnode)+"_"+str(ntcore)+"_"+str(ngpu)+"_"+str(ntomp)

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
