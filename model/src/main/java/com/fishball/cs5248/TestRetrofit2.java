package com.fishball.cs5248;

/*
import com.squareup.okhttp.MediaType;
import com.squareup.okhttp.OkHttpClient;
import com.squareup.okhttp.RequestBody;
import retrofit.Call;
import retrofit.JacksonConverterFactory;
import retrofit.Retrofit;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
*/

/**
 * @author lpthanh
 */
public class TestRetrofit2 {
    /*

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

    private static void testUploadFile(TodoService2 service) throws IOException {
        Map<String, RequestBody> map = new HashMap<>();
        map.put("id", RequestBody.create(MediaType.parse("text/plain"), "tony-123"));
        map.put("video\"; filename=\"3.jpg\"", RequestBody.create(MediaType.parse("image/jpeg"), new File("/Users/lpthanh/Downloads/3 (1).jpg")));

        Call<String> call = service.uploadVideo(map);
        call.execute();

    }

    public static void main(String[] args) throws IOException {

        Retrofit retrofit = new Retrofit.Builder()
                .addConverterFactory(JacksonConverterFactory.create())
                .baseUrl("http://localhost:5000")
                .client(new OkHttpClient())
                .build();

        TodoService2 service = retrofit.create(TodoService2.class);

//        testPostNewVideo(service);
//        testQueryVideos(service);
        testUploadFile(service);
    }

    */

}
