#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import exp
import os
import re
import sys

# This code implements the non-linear regression method described in:

# Jean Jacquelin 2009,
# Régressions et équations intégrales,
# sec. REGRESSIONS NON LINEAIRES des genres : PUISSANCE, EXPONENTIELLE, LOGARITHME, WEIBULL,
# pp. 16-18.

# http://www.scribd.com/doc/14674814/Regressions-et-equations-integrales

# Given n data points (x[1], y[1]), ... (x[n], y[n])
# it computes coefficients a, b, and c that minimize error in the fit equation:
# y = a + b exp(c*x)

# TODO: This regression is not very robust, and currently fails with division by
# zero if the regression matrix is singular.
def exponential_non_linear_regression(x, y, n):
    S = [0] * (n+1)
    S[1] = 0
    sum_xx = 0
    sum_xS = 0
    sum_SS = 0
    sum_yx = 0
    sum_yS = 0
    for k in range(2, n+1):
        S[k] = S[k-1] + 0.5 * (y[k] + y[k-1]) * (x[k] - x[k-1])
        sum_xx += (x[k] - x[1]) * (x[k] - x[1])
        sum_xS += (x[k] - x[1]) * S[k]
        sum_SS += S[k] * S[k]
        sum_yx += (y[k] - y[1]) * (x[k] - x[1])
        sum_yS += (y[k] - y[1]) * S[k]

    # ( A1 ) = ( sum_xx  sum_xS ) -1 ( sum_yx )
    # ( B1 )   ( sum_xS  sum_SS )    ( sum_yS )

    det_inv = sum_xx*sum_SS - sum_xS*sum_xS
    if (det_inv == 0.0):
        return None

    det = 1 / det_inv
    A1 = det * ( sum_SS*sum_yx - sum_xS*sum_yS)
    B1 = det * (-sum_xS*sum_yx + sum_xx*sum_yS)

    if (B1 == 0.0):
        a1 = 0.0
    else:
        a1 = - A1 / B1
    c1 = B1
    c2 = c1

    sum_theta = 0
    sum_thetatheta = 0
    sum_y = 0
    sum_ytheta = 0
    theta = [0] * (n+1)
    for k in range(1, n+1):
        theta[k] = exp(c2 * x[k])
        sum_theta += theta[k]
        sum_thetatheta += theta[k] * theta[k]
        sum_y += y[k]
        sum_ytheta += y[k] * theta[k]

    # ( a2 ) = ( n          sum_theta      ) -1 ( sum_y      )
    # ( b2 )   ( sum_theta  sum_thetatheta )    ( sum_ytheta )

    inv_det = n*sum_thetatheta - sum_theta*sum_theta
    if (inv_det == 0.0):
        det = 0.0
    else:
        det = 1 / inv_det
    a2 = det * ( sum_thetatheta*sum_y - sum_theta*sum_ytheta)
    b2 = det * (-sum_theta*sum_y + n*sum_ytheta)

    if (det != 0):
        return "%g + %g * exp(%g*x)" % (a2, b2, c2)
    else:
        return None

# Output a datafile to output_file in the following form:
#    # Load Value
#    0 0
#    40 15.7
#    90 31.9
# Returns a string representing the "curve of best fit"
def calculate_data(grinder_files, accumulate_callback, output_file, include_origin=True):
    Load = []
    Value = []
    stages = 0
    for file in grinder_files:
        threads = 0
        stage = int(os.path.basename(os.path.dirname(file))[6:])     # strip initial 'stage-'
        if (stages < stage + 1):
            stages = stage + 1
        while len(Value) <= stage:
            Load.append(0)
            Value.append(0)
        with open(file, 'r') as f:
            for line in f:
                # Count the threads in this Grinder logfile by looking at all the unique log messages.
                # This is to determine the load level empirically.
                # TODO: There is probably a more efficient way to communicate this from experiment execution.
                m = re.match(r'....-..-.. ..:..:..,... INFO  .*-0 thread-([0-9]*)', line)
                if m:
                    thread = int(m.group(1))
                    if (threads < thread + 1):
                        threads = thread + 1
                m = re.match(r'Test ', line)
                if m:
                    # grinder-0.log file format:
                    #   $1 = "Test"
                    #   $2 = "0"...
                    #   $3 = Tests
                    #   $4 = Errors
                    #   $5 = Mean Test Time (ms)
                    #   $6 = Test Time Standard Deviation (ms)
                    #   $7 = TPS
                    #   $8 = Mean response length
                    #   $9 = Response bytes per second
                    #   $10 = Response errors
                    #   $11 = Mean time to resolve host
                    #   $12 = Mean time to establish connection
                    #   $13 = Mean time to first byte
                    #   $14 = Description
                    #             Tests        Errors       Mean Test    Test Time    TPS          Mean         Response     Response     Mean time to Mean time to Mean time to
                    #                                       Time (ms)    Standard                  response     bytes per    errors       resolve host establish    first byte
                    #                                                    Deviation                 length       second                                 connection
                    #                                                    (ms)
                    #
                    #Test 0       1060         0            10224.49     7229.27      0.58         19.77        11.51        5            0.04         0.28         10221.48      "Status"
                    #Test 1       2408         0            10490.14     7157.16      1.32         16665.09     22049.02     8            0.04         0.30         10485.22      "Projects"
                    fields = re.split("[ \t]+", line)
                    agent_data = {
                        'tests': float(fields[2]),
                        'mean_test_time': float(fields[4]),
                        'tps': float(fields[6]),
                        'desc': line.split('"')[1]
                    }
                    accumulate_callback(Value, stage, agent_data)

        Load[stage] += threads

    Load = [0] + Load
    Value = [0.0] + Value
    if include_origin:
        # Inject a "fake" (0,0) stage in the Load,Value lists.
        Load = [0] + Load
        Value = [0.0] + Value
        fake_stages=1
    else:
        fake_stages=0

    with open(output_file, 'w') as f:
        f.write("Load Value\n")
        for stage in range(1+fake_stages, stages+1+fake_stages):
            f.write("%d %g\n" % (Load[stage], Value[stage]))

    return exponential_non_linear_regression(Load, Value, stages+fake_stages)
