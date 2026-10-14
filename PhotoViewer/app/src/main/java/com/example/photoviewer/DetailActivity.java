package com.example.photoviewer;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.text.method.ScrollingMovementMethod;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;

import com.google.android.material.appbar.MaterialToolbar;

import java.io.IOException;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** 게시물 상세 : 원본 이미지는 이 화면에서만 내려받는다 (목록은 썸네일) + 핀치 줌 */
public class DetailActivity extends AppCompatActivity {
    public static final String EXTRA_TITLE = "title";
    public static final String EXTRA_TEXT = "text";
    public static final String EXTRA_META = "meta";
    public static final String EXTRA_IMAGE = "image";

    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler main = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_detail);
        SystemBars.applyPadding(findViewById(R.id.root));

        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        toolbar.setTitle(getIntent().getStringExtra(EXTRA_TITLE));
        toolbar.setNavigationIcon(R.drawable.ic_arrow_back);
        toolbar.setNavigationOnClickListener(v -> finish());

        ((TextView) findViewById(R.id.detailMeta)).setText(getIntent().getStringExtra(EXTRA_META));
        TextView body = findViewById(R.id.detailText);
        body.setText(getIntent().getStringExtra(EXTRA_TEXT));
        body.setMovementMethod(new ScrollingMovementMethod());

        ZoomImageView image = findViewById(R.id.detailImage);
        ProgressBar progress = findViewById(R.id.detailProgress);
        TextView info = findViewById(R.id.detailInfo);
        String url = getIntent().getStringExtra(EXTRA_IMAGE);

        executor.execute(() -> {
            long start = SystemClock.elapsedRealtime();
            try {
                ImageCache.Result r = ImageCache.get(this).load(url, ImageCache.ORIGINAL_MAX);
                long ms = SystemClock.elapsedRealtime() - start;
                main.post(() -> {
                    progress.setVisibility(View.GONE);
                    image.setImageBitmap(r.bitmap);
                    info.setText(String.format(Locale.KOREA, "원본 %d×%d · %s · %dms  (두 손가락 확대, 더블탭 확대/복귀)",
                            r.bitmap.getWidth(), r.bitmap.getHeight(),
                            r.fromCache ? "캐시" : "다운로드 " + Formats.bytes(r.networkBytes), ms));
                });
            } catch (IOException | RuntimeException e) {
                main.post(() -> {
                    progress.setVisibility(View.GONE);
                    info.setText("원본 이미지를 불러오지 못했습니다: " + e.getMessage());
                });
            }
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdownNow();
    }
}
