#!/usr/bin/env python

import os
import shutil
from subprocess import call

from video_repr import Constants as Repr
from video_repr import DefaultRepresentations


def prepare_target_dir(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        return

    # make sure the directory exists
    dir_name = os.path.dirname(os.path.realpath(file_path))
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def encode_x264(file_src, file_target, bitrate, fps, width, height, audio_asfq, audio_bitrate):
    prepare_target_dir(file_target)

    call('./tools/ix/convert.sh "%s" %d %s %dx%d %d %d "%s"' % (
        file_src,
        bitrate,
        str(fps),
        width, height,
        audio_asfq,
        audio_bitrate,
        file_target
    ), shell=True)

    # since convert.sh does not return a meaningful exit code,
    # we check the result file
    return os.path.exists(file_target) and os.path.getsize(file_target) > 0


def encode_x264_repr(file_src, file_target, video_repr):
    return encode_x264(file_src,
                       file_target,
                       video_repr.bandwidth / Repr.VIDEO_BIT_RATE_DIV,
                       Repr.VIDEO_FPS,
                       video_repr.width,
                       video_repr.height,
                       Repr.AUDIO_SAMPLE_FREQUENCY,
                       Repr.AUDIO_BITRATE)


def encode_mp42ts(file_src, file_target):
    prepare_target_dir(file_target)
    exit_code = call('mp42ts "%s" "%s"' % (file_src, file_target), shell=True)

    # success exit code
    return exit_code == 0


if __name__ == "__main__":
    # test run

    if os.path.exists('test_videos/output'):
        shutil.rmtree('test_videos/output')

    os.makedirs('test_videos/output/ORIGINAL')
    os.makedirs('test_videos/output/HIGH')
    os.makedirs('test_videos/output/MEDIUM')
    os.makedirs('test_videos/output/LOW')

    encode_x264_repr('test_videos/test_video.mp4',
                     'test_videos/output/LOW/test_video.mp4',
                     DefaultRepresentations.LOW)

    encode_x264_repr('test_videos/test_video.mp4',
                     'test_videos/output/MEDIUM/test_video.mp4',
                     DefaultRepresentations.MEDIUM)

    encode_x264_repr('test_videos/test_video.mp4',
                     'test_videos/output/HIGH/test_video.mp4',
                     DefaultRepresentations.HIGH)

    encode_mp42ts('test_videos/test_video.mp4',
                  'test_videos/output/ORIGINAL/test_video.ts')

    encode_mp42ts('test_videos/output/LOW/test_video.mp4',
                  'test_videos/output/LOW/test_video.ts')

    encode_mp42ts('test_videos/output/MEDIUM/test_video.mp4',
                  'test_videos/output/MEDIUM/test_video.ts')

    encode_mp42ts('test_videos/output/HIGH/test_video.mp4',
                  'test_videos/output/HIGH/test_video.ts')
