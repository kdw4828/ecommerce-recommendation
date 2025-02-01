from django.contrib import admin
from django.urls import path
from products import views

urlpatterns = [
    path('admin/', admin.site.urls),  # 관리자 페이지
    path('list/', views.product_list, name='product_list'),  # 모든 제품 리스트
    path('recommendations/<int:product_id>/', views.get_recommendations, name='get_recommendations'),  # 추천 페이지
    path('api/recommendations/<int:product_id>/', views.api_get_recommendations, name='api_get_recommendations'),  # 추천 API
    path('feedback/<int:product_id>/', views.submit_feedback, name='submit_feedback'),
]
