package com.example.photoviewer;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;
import java.util.List;

/** 강의자료 p.16~17 의 ImageAdapter : Bitmap 목록 → 게시물(PostItem) 카드 목록으로 확장 */
public class ImageAdapter extends RecyclerView.Adapter<ImageAdapter.ImageViewHolder> {

    public interface OnPostClickListener {
        void onPostClick(PostItem post);
    }

    private final List<PostItem> imageList = new ArrayList<>();
    private final OnPostClickListener listener;

    public ImageAdapter(List<PostItem> imageList, OnPostClickListener listener) {
        this.imageList.addAll(imageList);
        this.listener = listener;
    }

    public void setItems(List<PostItem> items) {
        imageList.clear();
        imageList.addAll(items);
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public ImageViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_image, parent, false);
        return new ImageViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull ImageViewHolder holder, int position) {
        PostItem post = imageList.get(position);
        holder.imageView.setImageBitmap(post.bitmap);
        holder.title.setText(post.title);
        holder.body.setText(post.text);
        holder.meta.setText(post.displayDate() + " · " + post.author);
        holder.itemView.setOnClickListener(v -> {
            if (listener != null) {
                listener.onPostClick(post);
            }
        });
    }

    @Override
    public int getItemCount() {
        return imageList.size();
    }

    public static class ImageViewHolder extends RecyclerView.ViewHolder {
        ImageView imageView;
        TextView title;
        TextView body;
        TextView meta;

        public ImageViewHolder(View itemView) {
            super(itemView);
            imageView = itemView.findViewById(R.id.imageViewItem); // item_image.xml 에 있는 ImageView
            title = itemView.findViewById(R.id.textTitle);
            body = itemView.findViewById(R.id.textBody);
            meta = itemView.findViewById(R.id.textMeta);
        }
    }
}
