import hashlib

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.http import quote_etag
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .forms import PostForm
from .models import Post
from .serializers import PostSerializer


# --------------------------------------------------------------------------
# 웹 페이지 (ch03)
# --------------------------------------------------------------------------
def post_list(request):
    posts = (Post.objects.filter(published_date__lte=timezone.now())
             .select_related('author').order_by('-published_date'))
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


@login_required
def post_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form, 'is_new': True})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # 편의기능 ③ : 본인 글만 수정 가능
    if post.author_id != request.user.id and not request.user.is_staff:
        return render(request, 'blog/forbidden.html', status=403)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form, 'is_new': False})


def js_test(request):
    return render(request, 'blog/js_test.html', {})


# --------------------------------------------------------------------------
# REST API (강의자료 p.5 : BlogImages)
# --------------------------------------------------------------------------
class IsOwnerOrReadOnly(permissions.BasePermission):
    """편의기능 ③ : 수정/삭제는 작성자 본인(또는 관리자)만 가능"""
    message = '본인이 작성한 게시물만 수정/삭제할 수 있습니다.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author_id == request.user.id or request.user.is_staff


class BlogImages(viewsets.ModelViewSet):
    """포토 블로그 API

    GET  /api_root/Post/            게시물 목록(JSON Array)
         ?search=키워드              제목/본문 검색
         ?since=2026-10-14T12:00:00+09:00   이 시각 이후 변경된 게시물만 (편의기능 ① 증분 동기화)
         If-None-Match: "<etag>"    변경이 없으면 304 Not Modified (편의기능 ①)
    POST /api_root/Post/            게시물 업로드 (multipart : title, text, image ...)
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = Post.objects.select_related('author').order_by('-published_date', '-id')
        params = self.request.query_params
        keyword = params.get('search', '').strip()
        if keyword:
            qs = qs.filter(Q(title__icontains=keyword) | Q(text__icontains=keyword))
        since = params.get('since')
        if since:
            since_dt = parse_datetime(since.replace(' ', '+'))
            if since_dt is None:
                raise ValidationError({'since': 'ISO 8601 형식이어야 합니다. 예) 2026-10-14T12:00:00+09:00'})
            if timezone.is_naive(since_dt):
                since_dt = timezone.make_aware(since_dt)
            qs = qs.filter(updated_date__gt=since_dt)
        return qs

    # ---- 편의기능 ① : ETag 기반 조건부 GET ---------------------------------
    def _list_etag(self, queryset):
        agg = queryset.aggregate(n=Count('id'), last=Max('updated_date'), top=Max('id'))
        total = Post.objects.count()  # 삭제 감지를 위해 전체 개수도 포함
        raw = '|'.join(str(v) for v in (
            agg['n'], agg['last'], agg['top'], total,
            self.request.get_host(), self.request.get_full_path(),
            self.request.accepted_renderer.format if hasattr(self.request, 'accepted_renderer') else '',
        ))
        return quote_etag(hashlib.sha1(raw.encode()).hexdigest()[:20])

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        etag = self._list_etag(queryset)
        if_none_match = request.headers.get('If-None-Match', '')
        if etag in [t.strip() for t in if_none_match.split(',') if t.strip()]:
            response = Response(status=status.HTTP_304_NOT_MODIFIED)
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)
            response['X-Total-Count'] = str(len(serializer.data))
        response['ETag'] = etag
        response['Cache-Control'] = 'no-cache'
        return response

    # ---- 편의기능 ③ : 작성자 위조 방지 --------------------------------------
    def perform_create(self, serializer):
        published = serializer.validated_data.get('published_date') or timezone.now()
        serializer.save(author=self.request.user, published_date=published)

    def perform_update(self, serializer):
        if serializer.instance.author_id != self.request.user.id and not self.request.user.is_staff:
            raise PermissionDenied(IsOwnerOrReadOnly.message)
        serializer.save()
