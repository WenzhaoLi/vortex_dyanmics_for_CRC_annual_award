# Vortex Dyanmics for CRC Annual Award

This is a page to showcase the details of my projects using the Work Queue APIs and the Condor pool at Notre Dame.
The first chapter gives a breif physics background on our research and the second chapter describes the parallel computing methods we use.

## Superconductivity and Vortex Dyanmics

Superconductivity is the quantum phenomenon where the electric resistance of the material disappears when being cooled to a very low temperature. Since it was discovered, superconductivity has attracted a lot of research attention because of the great potentials in applications such as dissipation-free electric transmission and high-performance electromagnets. 

Superconducting vortices are the intrinsic topological defects in superconductors and the behavior of them is critical to the applications of superconductivity.
Superconducting vortex dynamics can be described by Langevin type equations of motion and studied using molecular dynamics (MD) simulations. (I also attached my PhD thesis in this repo. Please refer to my thesis if you are interested in the physics details of the projcets.) 

With the paralell computing methods we adopted and the computing power provided by CRC, we managed to consume more than 8 million CPU-hours in 2020. 
One of our simulation projects has been accepted by the physics journal Applied Physics Letter (APL) and the other one is submitted to Physics Review B (PRB).
(These two projects are in collaboration with Los Alamos National Laboratory.)

Publication on Applied Physics Letter (APL):
https://aip.scitation.org/doi/10.1063/5.0045584

Submission to Physics Review B (PRB):
https://arxiv.org/abs/2012.09937

<img src="https://user-images.githubusercontent.com/19979625/116009251-6a55c880-a5e6-11eb-91d5-ca0b18f605a8.png" width="300">

(Vortices in a superconductor. The dynamics of superconducting vortex matter can be studied using molecular dynamics (MD) simulation.)

## Vortex Dynamics with Parallel Computing

In the past few years, I have been developing parallel computing algorithms on our Notre Dame Condor pool to study superconducting vortex dynamics using the Work Queue APIs. 
The general idea is, by using parallel computing we can simultaneously run different configurations and therefore accelerate the simulations. This can be easily fulfilled with simple Condor job submissions. 
However, some of our simulations require very complicated workflows and for this purpose we develop algorithms using the APIs provided by Work Queue. Here's how Work Queue applications work in short:

![image](https://user-images.githubusercontent.com/19979625/115816192-677c8d00-a3c6-11eb-8300-d36e7122d7c8.png)

(This is a snapshot obtained from the Cooperative Computing Lab (CCL) webside.)

Work Queue has the master-worker architecture. The master is responsible for distributing the jobs to the workers. Workers then find proper nodes in the computing pool to run the jobs. When the jobs are finished, the workers send the output back to the master and the master can decide what to do next. 

With this architecture, we are able to design complicated workflows along with the parallel computing manner. For example, in one of our simulation processes, we need to find the critical current of the superconducting systems and this can be done using binary search. Therefore, I developed a script to accommodate binary search and parallel computing at the same time. 

The idea is that we have thousands of different configurations running simultaneously and for each configuration, the master records the upper limit and the lower limit of the binary search. Depending on the outputs received from the workers, the master would adjust the limits and submit new jobs to the workers and finish binary searches of each configuration.

You may ask why not include the whole binary search process in one job submission. The reason is if we do that, one job submission may take up to days or even weeks to finish. Since the Condor pool is opportunistic, our jobs may be kicked out anytime and therefore we want to submit short or reasonably long jobs instead of very long jobs. (A long job may never get finished on Condor pool.)

Here in this repo, the binary search script is included for reference. Besides the binary search, I also developed a lot of other algorithms to include complicated workflows with parallel computing at the same time. Please let me know if you want to see more examples. With this method, we are able to generate a lot of useful simulation data and efficiently harness resources from the Condor pool. This snapshot was captured in early 2021. It roughly shows the Condor pool usage in 2020. In the past year, we have managed to generate 8 million CPU-hours’ worth of simulation data. 

<img src="https://user-images.githubusercontent.com/19979625/115816247-84b15b80-a3c6-11eb-9575-e4bac86e73a8.png" width="550">

