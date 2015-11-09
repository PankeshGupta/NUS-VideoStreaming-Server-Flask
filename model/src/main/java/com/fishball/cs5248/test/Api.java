package com.fishball.cs5248.test;

import retrofit.http.Body;
import retrofit.http.GET;
import retrofit.http.POST;
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


}
