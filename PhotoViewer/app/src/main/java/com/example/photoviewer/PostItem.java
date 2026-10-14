package com.example.photoviewer;

import android.graphics.Bitmap;

import org.json.JSONObject;

/** GET /api_root/Post/ 응답의 게시물 1건 */
public class PostItem {
    public int id;
    public String title;
    public String text;
    public String author;
    public String publishedDate;
    public String imageUrl;
    public String thumbnailUrl;
    public Bitmap bitmap;

    public static PostItem fromJson(JSONObject json) {
        PostItem item = new PostItem();
        item.id = json.optInt("id", -1);
        item.title = json.optString("title", "");
        item.text = json.optString("text", "");
        item.author = json.optString("author_name", "user " + json.optInt("author"));
        item.publishedDate = json.isNull("published_date") ? "" : json.optString("published_date", "");
        item.imageUrl = json.optString("image", "");
        // 편의기능 ② : 서버가 제공하는 썸네일이 있으면 목록에서는 썸네일만 받는다
        String thumb = json.optString("thumbnail", "");
        item.thumbnailUrl = (thumb == null || thumb.isEmpty() || "null".equals(thumb)) ? item.imageUrl : thumb;
        return item;
    }

    /** "2026-10-14T12:03:55.12+09:00" → "2026-10-14 12:03" */
    public String displayDate() {
        if (publishedDate == null || publishedDate.length() < 16) {
            return publishedDate == null ? "" : publishedDate;
        }
        return publishedDate.substring(0, 16).replace('T', ' ');
    }
}
