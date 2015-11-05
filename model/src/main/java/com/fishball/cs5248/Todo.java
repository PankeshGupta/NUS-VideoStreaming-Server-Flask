package com.fishball.cs5248;

/**
 * @author lpthanh
 */
public class Todo {

    private String id;

    private String task;

    private String uri;

    public Todo(String uri, String task, String id) {
        this.uri = uri;
        this.task = task;
        this.id = id;
    }

    public Todo() {
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getTask() {
        return task;
    }

    public void setTask(String task) {
        this.task = task;
    }

    public String getUri() {
        return uri;
    }

    public void setUri(String uri) {
        this.uri = uri;
    }

    @Override
    public String toString() {
        return "Todo{" +
                "id='" + id + '\'' +
                ", task='" + task + '\'' +
                ", uri='" + uri + '\'' +
                '}';
    }
}