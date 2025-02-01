from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()  # Django의 사용자 모델 가져오기

class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(max_length=1024)  # CloudFront URL 저장

    def save(self, *args, **kwargs):
        # 이미지 URL을 CloudFront 경로로 저장
        if "s3.amazonaws.com" in self.image_url:
            self.image_url = self.image_url.replace(
                "john-ecommerce-bucket.s3.amazonaws.com",
                "dnr5lspes3u93.cloudfront.net"
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class UserPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # 제품
    rating = models.IntegerField(choices=[(1, "Like"), (0, "Dislike")])  # 좋아요/싫어요
    timestamp = models.DateTimeField(auto_now_add=True)  # 작성 시간

    def __str__(self):
        return f"{self.user} - {self.product} - {self.rating}"
    
class RecommendationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    recommended_at = models.DateTimeField(auto_now_add=True)
    clicked = models.BooleanField(default=False)  # 사용자가 클릭했는지 여부