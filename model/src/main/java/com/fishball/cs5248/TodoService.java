package com.fishball.cs5248;

import retrofit.Callback;
import retrofit.http.*;
import retrofit.mime.TypedFile;

import java.util.List;

/**
 * @author lpthanh
 */
public interface TodoService {

    @GET("/todos")
    void listTodo(Callback<List<Todo>> callback);

    @POST("/todos")
    void createTodo(@Body Todo todo, Callback<Todo> callback);

    @POST("/videos")
    void createVideo(@Body Video video, Callback<Video> callback);

    @Multipart
    @POST("/upload")
    void uploadVideo(@Part("name") String name,
                     @Part("video") TypedFile photo,
                     Callback<String> callback);
}
