# H-reflex-velocity-calculator
Python code developed in June-July 2023 for UQ winter research project conducted at the School of Biomedical Sciences, Faculty of Medicine. All code belongs to Seijun Stokes.

The H-reflex and M-wave are electrical signals used to study the nervous system and muscles. The H-reflex assesses the integrity of reflex pathways by stimulating a sensory nerve illiciting a spinal reflex and recording the muscle's response. It helps diagnose conditions related to nerve compression, spinal cord injuries, or neurological disorders. On the other hand, the M-wave measures overall muscle response by directly stimulating a motor nerve and recording the muscle's electrical activity. It is valuable for assessing muscle health, neuromuscular disorders, and muscle fatigue. Both tests play crucial roles in neurophysiology and clinical neurology for evaluating different aspects of neuromuscular function.

After the nervous signal (H-reflex / M-wave) reach the neuromuscular junction, it travels along the muslce fibres. The velocity of which the signal travels across can be used as a designator for motor neuron recruitment. 

High Density surface Electro-Myography (HDsEMG) is a method of measuring the electric signal across a wide area of muslce fibre using a grid of electrodes, therefore enhancing the spatial resolution of the conduction pathway of the Action Potentials. OT Biolab is a software used to record and export data from HDsEMG. In this particular research, external electrical stimulations were applied in varying intensities in postural conditions.

Due to the difference in Action Potential threshold between peripheral sensory neurons and motor neurons, after a stimulus artifact there is an initial window for M-wave and H-reflex following. At smaller intensities there will be no M-wave, and at larger intensities the M wave will override the H-reflex, and may eventually result in a F-wave.

This Python code takes csv files exported from OT Biolab. The files must be single differential signals, which take the difference between signals from two adjacent columns. 
The main components of the code are:
Take the csv file (separated by semicolons for some reason) and convert to a Pandas DataFrame.
A seperate csv file is exported to produce a square wave when a external stiumuls is applied. Mask the timestamps file with original signal files to extract individual stimulus points.
Find key points in the waves, such as peaks and troughs, and their respective timestamps.
Calculate conduction velocities between two adjacent channels, by taking the time difference of the peaks at each channel, as well as the average between positive and negative peaks
Calculate other data such as latency of signals.
Output relevant data in csv format.

This code allows user to store all files to be read in a single folder, and automates all processes required for conduction velocity calculations.

