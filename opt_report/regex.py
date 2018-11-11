#! /usr/bin/python3

import re

class IccOptReportLoopType(Enum):
    MAIN = 0
    DISTRIBUTED_CHUNK = 1
    PEEL = 2
    REMAINDER = 3
    UNKNOWN = 4

# [1] Regular expressions identifying loop boundaries in ICC compiler report
LOOP_BEGIN_re = re.compile("LOOP BEGIN at (.+)\(([0-9]+),([0-9]+)\)$")
LOOP_BEGIN_INLINED_re = re.compile("LOOP BEGIN at (.+)\(([0-9]+),([0-9]+)\) inlined into (.+)\(([0-9]+),([0-9]+)\)$")
LOOP_END_re = re.compile("LOOP END")
LOOP_NAME_re = re.compile("(.+)\(([0-9]+)\)")

# [2] Regular expressions identifying transformed structure of loops and loop nests 
# (loop remainders, peeled off parts of loops, fused loops, distributed loops, etc.)
LOOP_PEEL_re = re.compile("<Peeled loop for vectorization>")
LOOP_VECTOR_REMAINDER_re = re.compile("<Remainder loop for vectorization>")
LOOP_REMAINDER_re = re.compile("<Remainder>")
LOOP_DISTR_CHUNK_re = re.compile("<Distributed chunk([0-9]+)>")
LOOP_DISTR_CHUNK_VECTOR_REMAINDER_re = re.compile("<Remainder loop for vectorization, Distributed chunk([0-9]+)>")

LOOP_REMAINDER_1_RE = re.compile("Remainder")
LOOP_FUSION_LOST_RE = re.compile("Loop lost in Fusion")

# [3] Regular expressions for different sorts of loop remarks, 
# provided by the Intel compiler in it's report

# [3.1] remarks identifying loop parallelizability status 
LOOP_PARALLEL_re = re.compile("LOOP WAS AUTO-PARALLELIZED")
LOOP_PARALLEL_POTENTIAL_re = re.compile(": loop was not parallelized: inner loop")

LOOP_WHOLE_PARALLELIZED_RE = re.compile(": LOOP WAS AUTO-PARALLELIZED")
LOOP_DISTR_PARALLELIZED_RE = re.compile(": DISTRIBUTED LOOP WAS AUTO-PARALLELIZED")
LOOP_FUSED_PARALLELIZED_RE = re.compile(": FUSED LOOP WAS AUTO-PARALLELIZED")
LOOP_PARTIAL_PARALLELIZED_RE = re.compile(": PARTIAL LOOP WAS AUTO-PARALLELIZED")
LOOP_INNER_PAR_POTENTIAL_RE = re.compile("loop was not parallelized: inner loop")

# [3.2] remarks identifying vectorized loops 
LOOP_VECTOR_re = re.compile("LOOP WAS VECTORIZED")
LOOP_VECTOR_POTENTIAL_re = re.compile(": loop was not vectorized: inner loop was already vectorized")

LOOP_COMMON_VECTORIZED_re = re.compile(": LOOP WAS VECTORIZED")
LOOP_DISTR_VECTORIZED_re = re.compile(": DISTRIBUTED LOOP WAS VECTORIZED")
LOOP_FUSED_VECTORIZED_re = re.compile(": FUSED LOOP WAS VECTORIZED")
LOOP_PARTIAL_VECTORIZED_re = re.compile(": PARTIAL LOOP WAS VECTORIZED")

# [3.3] remarks identifying dependencies present in loops 
LOOP_PARALLEL_DEPENCENCE_re = re.compile(": loop was not parallelized: existence of parallel dependence")
LOOP_VECTOR_DEPENDENCE_re = re.compile(": loop was not vectorized: vector dependence prevents vectorization")

# [2.5] remarks identifying different sorts of applied 
# loop optimizations

# [2.5.0] (no loop optimizations reported)
LOOP_NO_OPTIMIZATIONS_RE = re.compile("No loop optimizations reported")

# [2.5.1] (loop-fusion)
FUSED_LOOPS_RE = re.compile("Fused loops: \((.*)\)")

# [2.5.2] (loop-distribution)
DISTRIBUTED_LOOP_RE = re.compile(": Loop Distributed \(([0-9]+) way\)")

# [2.1] ICC compiler OpenMP report
OPENMP_CONSTRUCT_RE = re.compile("OpenMP Construct at (.*)\((.*),.+")
OPENMP_PARALLEL_RE = re.compile("OpenMP DEFINED LOOP PARALLELIZED")

if __name__ != "__main__":
    
    re_loop_identification = {}
    re_loop_identification["begin"] = LOOP_BEGIN_RE
    re_loop_identification["end"] = LOOP_END_RE
    re_loop_identification["loop-name"] = LOOP_NAME_RE

