from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    # 편의기능 ③ : 작성자는 클라이언트가 보낸 값이 아니라 인증된 사용자(토큰)로 서버가 지정
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)
    thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = Post
        # 강의자료 p.9 의 필드 순서(author, title, text, created_date, published_date, image) 유지
        fields = ('author', 'title', 'text', 'created_date', 'published_date', 'image',
                  'id', 'author_name', 'thumbnail', 'updated_date')
        read_only_fields = ('id', 'updated_date')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # 썸네일이 없는 과거 게시물은 원본 URL 로 대체 → 클라이언트는 항상 thumbnail 사용 가능
        if not data.get('thumbnail'):
            data['thumbnail'] = data.get('image')
        return data
