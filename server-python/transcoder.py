#!/usr/bin/env python

import subprocess

from video_repr import Constants as Repr


def encode_x264(file_src, file_target, bitrate, fps, width, height, audio_asfq, audio_bitrate):
    subprocess.Popen([
        './tools/ix/convert.sh',
        file_src,
        str(bitrate),
        str(fps),
        "%dx%d" % (width, height),
        str(audio_asfq),
        str(audio_bitrate),
        file_target
    ], shell=True)


def encode_x264_repr(file_src, file_target, video_repr):
    encode_x264(file_src,
                file_target,
                video_repr.bandwidth / Repr.VIDEO_BIT_RATE_DIV,
                Repr.VIDEO_FPS,
                video_repr.width,
                video_repr.height,
                Repr.AUDIO_SAMPLE_FREQUENCY,
                Repr.AUDIO_BITRATE)


def encode_mp42ts(file_src, file_target):
    subprocess.Popen(['./tools/ix/mp42ts', file_src, file_target], shell=True)


if __name__ == "__main__":
    # test run

    from video_repr import DefaultRepresentations

    encode_x264_repr('test_videos/test_video.mp4', 'test_videos/LOW/test_video.mp4', DefaultRepresentations.LOW)
    # encode_x264_repr('test_videos/test_video.mp4', 'test_videos/MEDIUM/test_video.mp4', DefaultRepresentations.MEDIUM)
    # encode_x264_repr('test_videos/test_video.mp4', 'test_videos/HIGH/test_video.mp4', DefaultRepresentations.HIGH)
    #
    # encode_mp42ts('test_videos/LOW/test_video.mp4', 'test_videos/LOW/test_video.ts')
    # encode_mp42ts('test_videos/MEDIUM/test_video.mp4', 'test_videos/MEDIUM/test_video.ts')
    # encode_mp42ts('test_videos/HIGH/test_video.mp4', 'test_videos/HIGH/test_video.ts')
