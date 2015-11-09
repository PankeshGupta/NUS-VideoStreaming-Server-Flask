package com.fishball.cs5248.test;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategy;
import retrofit.RequestInterceptor;
import retrofit.RestAdapter;
import retrofit.converter.JacksonConverter;
import retrofit.mime.TypedFile;
import rx.Observable;

import java.io.File;
import java.util.List;
import java.util.concurrent.TimeUnit;

/**
 * This classes encapsulate the core API, and may provide other features such as adaptation between
 * server and client models, caching or network request intercepting.
 *
 * @author lpthanh
 */
public class StreamingService {

    private static final String WEB_SERVICE_BASE_URL = "http://localhost:5000";

    private static final long TIME_OUT = 20000;

    private final Api api;

    public StreamingService() {
        RequestInterceptor requestInterceptor = request -> {
            request.addHeader("Accept", "application/json");
        };

        ObjectMapper mapper = new ObjectMapper();
        mapper.setPropertyNamingStrategy(new PropertyNamingStrategy.LowerCaseWithUnderscoresStrategy());

        RestAdapter restAdapter = new RestAdapter.Builder()
                .setEndpoint(WEB_SERVICE_BASE_URL)
                .setConverter(new JacksonConverter(mapper))
                .setRequestInterceptor(requestInterceptor)
                .setLogLevel(RestAdapter.LogLevel.FULL)
                .build();

        api = restAdapter.create(Api.class);
    }

    public Api getApi() {
        return this.api;
    }

    public Observable<List<Video>> getOnDemandVideos() {
        return getApi()
                .getOnDemandVideos()
                .timeout(TIME_OUT, TimeUnit.MILLISECONDS);
    }

    public Observable<List<Video>> getLiveStreams() {
        return getApi()
                .getLiveStreams()
                .timeout(TIME_OUT, TimeUnit.MILLISECONDS);
    }


    public static void main(String[] args) throws Exception {

        StreamingService service = new StreamingService();
        Api api = service.getApi();

        Video video = new Video();
        video.setTitle("This is a video");

        video = api.createVideo(video).toBlocking().first();

        System.out.println("Created video. Id=" + video.getVideoId());

        long nextSegmentId = 0;

        File file = new File("model/src/main/resources/test_video.mp4");
        System.out.println("Path: " + file.getAbsolutePath());
        TypedFile videoFile = new TypedFile("multipart/form-data", file);
        VideoSegment segment = api.createSegment(video.getVideoId(), nextSegmentId, videoFile).toBlocking().first();

        System.out.println("Uploaded path: " + segment.getOriginalPath());
    }

}
