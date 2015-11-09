package com.fishball.cs5248.test;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

import java.util.Date;

/**
 * @author lpthanh
 */
public class Video {

    @Getter
    @Setter
    private Long videoId;

    @Getter
    @Setter
    private String title;

    @Getter
    @Setter
    private VideoStatus status;

    @Getter
    @Setter
    private VideoType type;

    @Setter
    @Getter
    private Date createdAt;

    @Setter
    @Getter
    private long segmentCount;

    @Setter
    @Getter
    private long segmentDuration;

    @Setter
    @Getter
    @JsonProperty("repr_1_name")
    private String repr1Name;

    @Setter
    @Getter
    @JsonProperty("repr_1_bandwidth")
    private String repr1Bandwidth;

    @Setter
    @Getter
    @JsonProperty("repr_1_width")
    private String repr1Width;

    @Setter
    @Getter
    @JsonProperty("repr_1_height")
    private String repr1Height;

    @Setter
    @Getter
    @JsonProperty("repr_2_name")
    private String repr2Name;

    @Setter
    @Getter
    @JsonProperty("repr_2_bandwidth")
    private String repr2Bandwidth;

    @Setter
    @Getter
    @JsonProperty("repr_2_width")
    private String repr2Width;

    @Setter
    @Getter
    @JsonProperty("repr_2_height")
    private String repr2Height;

    @Setter
    @Getter
    @JsonProperty("repr_3_name")
    private String repr3Name;

    @Setter
    @Getter
    @JsonProperty("repr_3_bandwidth")
    private String repr3Bandwidth;

    @Setter
    @Getter
    @JsonProperty("repr_3_width")
    private String repr3Width;

    @Setter
    @Getter
    @JsonProperty("repr_3_height")
    private String repr3Height;

    @Setter
    @Getter
    private String uriMpd;

    @Setter
    @Getter
    private String uriM3u8;

}
