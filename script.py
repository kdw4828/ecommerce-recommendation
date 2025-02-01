from products.models import Product

# 기존 데이터 가져오기
products = Product.objects.all()

# 모든 product의 image_url을 CloudFront URL로 변경
for product in products:
    if "s3.amazonaws.com" in product.image_url:
        product.image_url = product.image_url.replace(
            "john-ecommerce-bucket.s3.amazonaws.com",
            "dnr5lspes3u93.cloudfront.net"
        )
        product.save()
        print(f"Updated: {product.name} -> {product.image_url}")
