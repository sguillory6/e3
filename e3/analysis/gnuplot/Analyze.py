#!/usr/bin/env python

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from common.Utils import open_with_external_tool

from analysis.gnuplot.AnalyzeCommon import *
from analysis.gnuplot.AnalyzeGantt import *
from analysis.gnuplot.AnalyzeTimes import *
from analysis.gnuplot.AnalyzeCollectd import *
from analysis.gnuplot.AnalyzeThroughput import *
from analysis.gnuplot.AnalyzeHistogram import *
from analysis.gnuplot.AnalyzeMeanTestTimes import *

throughput_image = os.path.join(analysis_dir, 'throughput.png')
histogram_images = [os.path.join(analysis_dir, image) for image in os.listdir(analysis_dir)
                    if image.startswith('histogram-') and image.endswith('.png')]
mean_test_time_images = [os.path.join(analysis_dir, image) for image in os.listdir(analysis_dir)
                         if image.startswith('mean-test-time-') and image.endswith('.png')]

output_images = [throughput_image] + histogram_images + mean_test_time_images

for thread in threads:
    for stage in stages_for_thread(thread):
        gantt_image = os.path.join(analysis_dir, 'gantt-' + thread + '-' + stage + '.png')
        times_image = os.path.join(analysis_dir, 'times-' + thread + '-' + stage + '.png')
        collectd_images = [os.path.join(analysis_dir, image) for image in os.listdir(analysis_dir)
                           if image.startswith('collectd-' + thread + '-' + stage + '-') and image.endswith('.png')]
        output_image = os.path.join(analysis_dir, 'all-' + thread + '-' + stage + '.png')
        input_images = [file for file in [gantt_image, times_image] if os.path.isfile(file)] + collectd_images
        if input_images:
            subprocess.call(['montage', '-mode', 'concatenate', '-tile', '1x'] + input_images + [output_image])
            output_images.append(output_image)

# Open results in OS specific viewer
open_with_external_tool(output_images)
