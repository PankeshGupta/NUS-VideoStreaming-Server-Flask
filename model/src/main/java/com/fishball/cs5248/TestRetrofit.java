package com.fishball.cs5248;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.PropertyNamingStrategy;
import com.squareup.okhttp.OkHttpClient;
import retrofit.Callback;
import retrofit.RestAdapter;
import retrofit.RetrofitError;
import retrofit.client.OkClient;
import retrofit.client.Response;
import retrofit.converter.JacksonConverter;
import retrofit.mime.TypedFile;

import java.io.File;
import java.io.IOException;
import java.util.List;

/**
 * @author lpthanh
 */
public class TestRetrofit {


    static void testQueryVideos(TodoService service) throws IOException {
        service.listTodo(new Callback<List<Todo>>() {
            @Override
            public void success(List<Todo> todos, Response response) {
                for (Todo todo : todos) {
                    System.out.println("REPLIED: " + todo);
                }
            }

            @Override
            public void failure(RetrofitError retrofitError) {
                System.out.println("Error: " + retrofitError);
            }
        });

    }

    /*
    static void testPostNewVideo(TodoService service) throws IOException {
        for (int i = 0; i < 100; ++i) {
            Todo todo = new Todo(null, "Tony Thanh at the Pool - " + System.nanoTime(), null);
            service.createTodo(todo, new Callback<Todo>() {
                @Override
                public void success(Todo todo, Response response) {
                    System.out.println("POSTED: " + todo);
                }

                @Override
                public void failure(RetrofitError retrofitError) {
                    System.out.println("Error: " + retrofitError);
                }
            });
        }
    }

*/

    static void testPostNewVideo(TodoService service) throws IOException {
        for (int i = 0; i < 5; ++i) {
            Video video = new Video();
            video.setTitle("test " + i);
            service.createVideo(video, new Callback<Video>() {
                @Override
                public void success(Video video, Response response) {
                    System.out.println("POSTED: " + video);
                }

                @Override
                public void failure(RetrofitError retrofitError) {
                    System.out.println("Error: " + retrofitError);
                }
            });
        }
    }

    private static void testUploadFile(TodoService service) {
        TypedFile typedFile = new TypedFile("multipart/form-data", new File("/Users/lpthanh/Downloads/3.jpg"));
        String name = "hello, this is description speaking";

        service.uploadVideo(name, typedFile, new Callback<String>() {
            @Override
            public void success(String s, Response response) {
                System.out.println("Success: " + s);
            }

            @Override
            public void failure(RetrofitError error) {
                System.out.println("Error: " + error);
            }
        });


    }

    public static void main(String[] args) throws IOException {

        ObjectMapper mapper = new ObjectMapper();
        mapper.setPropertyNamingStrategy(new PropertyNamingStrategy.LowerCaseWithUnderscoresStrategy());

        RestAdapter.Builder builder = new RestAdapter.Builder()
                .setEndpoint("http://localhost:5000")
                .setConverter(new JacksonConverter(mapper))
                .setClient(new OkClient(new OkHttpClient()));

        RestAdapter adapter = builder.build();
        TodoService service = adapter.create(TodoService.class);

//        testPostNewVideo(service);
//        testQueryVideos(service);
//        testUploadFile(service);

        testPostNewVideo(service);
    }

}
