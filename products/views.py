from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes
from .recommendation import content_based_recommendations, frequently_bought_together

from .models import Feedback, Product, RecommendationLog

import boto3

from rest_framework.renderers import JSONRenderer
# REST API: JSON 응답 반환
@api_view(['GET'])
@renderer_classes([JSONRenderer])
def api_get_recommendations(request, product_id):
    content_based = content_based_recommendations(product_id)
    frequently_bought = frequently_bought_together(product_id)
    return Response({
        'content_based': [p.name for p in content_based],
        'frequently_bought': [p.name for p in frequently_bought],
    })

# 웹 인터페이스: HTML 템플릿 반환
def get_recommendations(request, product_id):
    content_based = content_based_recommendations(product_id)
    frequently_bought = frequently_bought_together(product_id)
    return render(request, 'products/recommendations.html', {
        'content_based': content_based,
        'frequently_bought': frequently_bought,
    })

# 제품 리스트 뷰
def product_list(request):
    products = Product.objects.all()
    return render(request, "products/product_list.html", {"products": products})

def upload_image_to_s3(file_name, file_content):
    if not file_name.startswith("2025"):
        s3 = boto3.client("s3")
        bucket_name = "john-ecommerce-bucket"
        s3.put_object(
            Bucket=bucket_name,
            Key=f"media/{file_name}",
            Body=file_content,
            ContentType="image/jpeg",
        )
    
    # CloudFront URL 반환
    return f"https://dnr5lspes3u93.cloudfront.net/media/{file_name}"

import subprocess
from django.http import JsonResponse

def invalidate_cloudfront_cache(distribution_id, paths="/*"):
    command = [
        "aws", "cloudfront", "create-invalidation",
        "--distribution-id", distribution_id,
        "--paths", paths
    ]
    subprocess.run(command)

def product_upload(request):
    if request.method == "POST":
        # 파일 업로드 로직
        file_name = "example.jpg"  # 실제 업로드된 파일 이름 사용
        file_content = request.FILES["file"].read()
        
        # S3 업로드 로직 호출 (생략)
        uploaded_url = upload_image_to_s3(file_name, file_content)

        # CloudFront 캐시 무효화
        invalidate_cloudfront_cache(distribution_id="E3AA2AFV9RFR4J", paths=f"/media/{file_name}")
        
        return JsonResponse({"uploaded_url": uploaded_url})
    
def submit_feedback(request, product_id):
    if request.method == "POST":
        user = request.user
        rating = int(request.POST.get("rating", 0))  # 1: Like, 0: Dislike
        product = Product.objects.get(id=product_id)

        # 기존 피드백 업데이트 또는 새로 생성
        feedback, created = Feedback.objects.update_or_create(
            user=user, product=product,
            defaults={"rating": rating}
        )
        return JsonResponse({"status": "success", "message": "Feedback submitted."})
    return JsonResponse({"status": "error", "message": "Invalid request."})

def log_recommendation_click(user, product):
    RecommendationLog.objects.create(user=user, product=product, clicked=True)