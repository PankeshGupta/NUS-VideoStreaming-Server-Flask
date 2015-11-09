package com.fishball.cs5248.test;

import retrofit.http.*;
import retrofit.mime.TypedFile;
import rx.Observable;

import java.util.List;

/**
 * @author lpthanh
 */
public interface Api {

    @POST("/videos")
    Observable<Video> createVideo(@Body Video video);

    @GET("/videos")
    Observable<List<Video>> getOnDemandVideos();

    @GET("/livestreams")
    Observable<List<Video>> getLiveStreams();

    @Multipart
    @POST("/video")
    Observable<VideoSegment> createSegment(@Part("video_id") Long videoId,
                                           @Part("segment_id") Long segmentId,
                                           @Part("data") TypedFile segmentFile);

}
