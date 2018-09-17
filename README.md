# gromarks
Simple python package for creating scripts to run GROMACS benchmarks.

## Installation

There are no package dependencies so on your local machine simply clone the repository 

    $ git clone https://github.com/philipwfowler/gromarks.git
    $ cd gromarks/

## Usage

The configuration of the machine you wish to benchmark on is described in a JSON file e.g. the new F RESCOMP nodes are here

    $ cat config/machines/rescomp.F.json 
    { "id":"rescomp.F",
      "gpu-number": 0,
      "core-number": 40,
      "core-simd": "AVX512",
      "gromacs":
        {
          "version": "2018.2",
          "path": "/apps/well/gromacs/2018.2-avx512-gcc5.4.0/bin/GMXRC",
          "mpi": 1
        }
      }

This will create a `run.sh` script to run a series of short GROMACS 2018.2 benchmark simulations up to 40 cores in size. There are no GPUs on these nodes.

Three different TPR files are included. These are `dhfr.tpr`, `rpob.tpr` and `peptst.tpr`. They all refer to protein names and are different sizes.

At present the package has two scripts

    $ gromarks-create.py --help
    usage: gromarks-create.py [-h] [--id ID] [--protein PROTEIN]

    optional arguments:
      -h, --help         show this help message and exit
      --id ID            the name of the JSON describing the machine configuration
                         e.g. rescomp.F
      --protein PROTEIN  the name of the benchmarking TPR file e.g.
                         dhfr/rpob/peptst

and 

    $ gromarks-analyse.py --help
    usage: gromarks-analyse.py [-h] [--id ID] [--protein PROTEIN]
    
    optional arguments:
      -h, --help         show this help message and exit
      --id ID            the name of the JSON describing the machine configuration
                         e.g. rescomp.F
      --protein PROTEIN  the name of the b

Running the first will create a folder inside the repository (I know, bad practice, but will fix this later to keep the package separate) which contains a single `run.sh` that will copy in the specified TPR file and then run GROMACS. No batch queueing system files are created at present - this will also be fixed later!

    $ gromarks-create.py --id rescomp.F --protein dhfr
    $ ls dhfr-rescomp.F/
    run.sh
    $ head dhfr-rescomp.F/run.sh 
    #! /bin/bash
  
    source /apps/well/gromacs/2018.2-avx512-gcc5.4.0/bin/GMXRC
    
    cp ../config/tpr-files/dhfr.tpr dhfr_rescomp.F_2018.2_1_0_1.tpr
    mpirun -np 1 mdrun_mpi -deffnm dhfr_rescomp.F_2018.2_1_0_1 -ntomp 1 -resethway -maxh 0.1 -noconfout -pin on
    
    cp ../config/tpr-files/dhfr.tpr dhfr_rescomp.F_2018.2_1_0_2.tpr
    mpirun -np 1 mdrun_mpi -deffnm dhfr_rescomp.F_2018.2_1_0_2 -ntomp 2 -resethway -maxh 0.1 -noconfout -pin on

The `-resethway` flag is short for reset timers at halfway which prevents the launch cycle influencing the timing. `-noconfout` stops GROMACS writing out a GRO file when the simulation terminates as this can also affect the timing. Finally, `-maxh 0.1` specifies that each sim will only run for 6 minutes before dying, 3 minutes of which is timed and recorded at the end of the LOG file. The collection of log files is then analysed using the other command





