#! /usr/bin/python3

import re

# [1] Regular expressions matching loop boundaries in the ICC compiler report
LOOP_BEGIN_re = re.compile("LOOP BEGIN at (.+)\(([0-9]+),([0-9]+)\)")
LOOP_BEGIN_INLINED_re = re.compile("LOOP BEGIN at (.+)\(([0-9]+),([0-9]+)\) inlined into (.+)\(([0-9]+),([0-9]+)\)")
LOOP_END_re = re.compile("LOOP END$")
LOOP_NAME_re = re.compile("(.+)\(([0-9]+)\)")

# [2] Regular expressions matching loop partitioning tags in the ICC compiler report
LOOP_DISTR_CHUNK_re = re.compile("<Distributed chunk([0-9]+)>")
LOOP_PEEL_re = re.compile("<Peeled loop for vectorization>")
LOOP_VECTOR_REMAINDER_re = re.compile("<Remainder loop for vectorization>")
LOOP_REMAINDER_re = re.compile("<Remainder>")
LOOP_DISTR_CHUNK_VECTOR_REMAINDER_re = re.compile("<Remainder loop for vectorization, Distributed chunk([0-9]+)>")
LOOP_DISTR_CHUNK_REMAINDER_re = re.compile("<Remainder, Distributed chunk([0-9]+)>")

# [3] Regular expressions matching different sorts of loop remarks, provided by the Intel compiler in it's report
LOOP_REMARK_re = re.compile("remark #([0-9]+): (.+)$")

LOOP_MAIN_re = re.compile("LOOP")
LOOP_DISTR_re = re.compile("DISTRIBUTED LOOP")
LOOP_FUSED_re = re.compile("FUSED LOOP")
LOOP_PARTIAL_re = re.compile("PARTIAL LOOP")

# [3.1] remarks identifying loop parallelizability status 
LOOP_PARALLEL_re = re.compile("LOOP WAS AUTO-PARALLELIZED")
LOOP_PARALLEL_POTENTIAL_re = re.compile("loop was not parallelized: inner loop")
LOOP_PARALLEL_INSUFFICIENT_WORK_re = re.compile("loop was not parallelized: insufficient computational work")

# [3.2] remarks identifying vectorized loops 
LOOP_VECTOR_re = re.compile("LOOP WAS VECTORIZED")
LOOP_VECTOR_POTENTIAL_re = re.compile("loop was not vectorized: inner loop was already vectorized")

# [3.3] remarks identifying simplified/eliminated/etc parallel/vectorisible loops 
LOOP_MEMSET_GENERATED_re = re.compile("memset generated")
LOOP_TRANSFORMED_MEMSET_re = re.compile("loop was not vectorized: loop was transformed to memset or memcpy")

# [3.4] remarks identifying dependencies present in loops 
LOOP_PARALLEL_DEPENCENCE_re = re.compile("loop was not parallelized: existence of parallel dependence")
LOOP_PARALLEL_NOT_CANDIDATE_re = re.compile("loop was not parallelized: not a parallelization candidate")
LOOP_VECTOR_DEPENDENCE_re = re.compile("loop was not vectorized: vector dependence prevents vectorization")

# [3.5] Remarks identifying different sorts of applied loop transformations/optimizations

LOOP_NO_OPTIMIZATIONS_re = re.compile("No loop optimizations reported")

LOOP_FUSION_MAIN_re = re.compile("Fused Loops: \((.*)\)$")
LOOP_FUSION_LOST_re = re.compile("Loop lost in Fusion")

LOOP_DISTRIBUTION_MARK_re = re.compile("Loop Distributed \(([0-9]+) way\)")

LOOP_COLLAPSE_MAIN_re = re.compile("Collapsed with loop at line ([0-9]+)")
LOOP_COLLAPSE_ELIMINATED_re = re.compile("Loop eliminated in Collapsing")

# [2.1] ICC compiler OpenMP report
OPENMP_CONSTRUCT_RE = re.compile("OpenMP Construct at (.*)\((.*),.+")
OPENMP_PARALLEL_RE = re.compile("OpenMP DEFINED LOOP PARALLELIZED")

if __name__ == "__main__":
    pass
else:
    pass
