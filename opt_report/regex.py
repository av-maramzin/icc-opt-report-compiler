#! /usr/bin/python3

import re

# [1] Regular expressions matching loop boundaries in the ICC compiler report
LOOP_BEGIN_re = re.compile("LOOP BEGIN at (.+)\(([0-9]+),([0-9]+)\)$")
LOOP_BEGIN_INLINED_re = re.compile("LOOP BEGIN at (.+)\(([0-9]+),([0-9]+)\) inlined into (.+)\(([0-9]+),([0-9]+)\)$")
LOOP_END_re = re.compile("LOOP END$")
LOOP_NAME_re = re.compile("(.+)\(([0-9]+)\)")

# [2] Regular expressions matching loop partitioning tags in the ICC compiler report
LOOP_DISTR_CHUNK_re = re.compile("<Distributed chunk([0-9]+)>")
LOOP_PEEL_re = re.compile("<Peeled loop for vectorization>")
LOOP_VECTOR_REMAINDER_re = re.compile("<Remainder loop for vectorization>")
LOOP_REMAINDER_re = re.compile("<Remainder>")
LOOP_DISTR_CHUNK_VECTOR_REMAINDER_re = re.compile("<Remainder loop for vectorization, Distributed chunk([0-9]+)>")

# [3] Regular expressions matching different sorts of loop remarks, provided by the Intel compiler in it's report
LOOP_REMARK_re = re.compile("remark #([0-9]+): (.+)$")

# [3.1] remarks identifying loop parallelizability status 
LOOP_PARALLEL_re = re.compile("LOOP WAS AUTO-PARALLELIZED")
LOOP_PARALLEL_POTENTIAL_re = re.compile("loop was not parallelized: inner loop")

# [3.2] remarks identifying vectorized loops 
LOOP_VECTOR_re = re.compile("LOOP WAS VECTORIZED")
LOOP_VECTOR_POTENTIAL_re = re.compile(": loop was not vectorized: inner loop was already vectorized")

LOOP_MAIN_re = re.compile("LOOP")
LOOP_DISTR_re = re.compile("DISTRIBUTED LOOP")
LOOP_FUSED_re = re.compile("FUSED LOOP")
LOOP_PARTIAL_re = re.compile("PARTIAL LOOP")

# [3.3] remarks identifying dependencies present in loops 
LOOP_PARALLEL_DEPENCENCE_re = re.compile(": loop was not parallelized: existence of parallel dependence")
LOOP_VECTOR_DEPENDENCE_re = re.compile(": loop was not vectorized: vector dependence prevents vectorization")

# [2.5] remarks identifying different sorts of applied 
# loop optimizations

# [2.5.0] (no loop optimizations reported)
LOOP_NO_OPTIMIZATIONS_RE = re.compile("No loop optimizations reported")

LOOP_FUSION_LOST_RE = re.compile("Loop lost in Fusion")

# [2.5.1] (loop-fusion)
FUSED_LOOPS_RE = re.compile("Fused loops: \((.*)\)")

# [2.5.2] (loop-distribution)
DISTRIBUTED_LOOP_RE = re.compile(": Loop Distributed \(([0-9]+) way\)")

# [2.1] ICC compiler OpenMP report
OPENMP_CONSTRUCT_RE = re.compile("OpenMP Construct at (.*)\((.*),.+")
OPENMP_PARALLEL_RE = re.compile("OpenMP DEFINED LOOP PARALLELIZED")

if __name__ == "__main__":
    pass
else:
    pass
