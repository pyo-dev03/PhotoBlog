import logging

from django.conf import settings
from django.db import models
from django.utils import timezone

from .imaging import make_thumbnail, thumbnail_name
from .validators import validate_photo

logger = logging.getLogger(__name__)


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='blog_image/%Y/%m/%d/',
                              default='blog_image/default_error.png',
                              validators=[validate_photo])
    # 편의기능 ① : 서버가 자동 생성하는 목록용 썸네일
    thumbnail = models.ImageField(upload_to='blog_thumb/%Y/%m/%d/', blank=True,
                                  editable=False)
    # 편의기능 ① : 증분 동기화(since / ETag) 판단 기준
    updated_date = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['-published_date', '-id']

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)
        instance._loaded_image_name = instance.image.name if instance.image else ''
        return instance

    def _image_changed(self):
        return self.image.name != getattr(self, '_loaded_image_name', None)

    def save(self, *args, **kwargs):
        if self.image and (not self.thumbnail or self._image_changed()):
            try:
                thumb = make_thumbnail(self.image)
                self.thumbnail.save(thumbnail_name(self.image.name), thumb, save=False)
            except (OSError, ValueError) as exc:  # 썸네일 실패가 게시를 막지는 않음
                logger.warning('thumbnail generation failed for %s: %s', self.image.name, exc)
                self.thumbnail = None
        super().save(*args, **kwargs)
        self._loaded_image_name = self.image.name if self.image else ''

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title
