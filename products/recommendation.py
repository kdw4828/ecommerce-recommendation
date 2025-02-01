import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from sklearn.metrics.pairwise import cosine_similarity
from .models import UserPurchase, Product
import numpy as np
from collections import Counter

# 콘텐츠 기반 추천 함수
def content_based_recommendations(product_id, top_n=5):
    # 모든 제품 데이터 가져오기
    products = Product.objects.all()
    product_data = [
        {
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            # 'description' 필드가 없으므로 'category'를 대체로 사용
            "description": product.category,  
        }
        for product in products
    ]

    # 데이터프레임 생성
    df = pd.DataFrame(product_data)

    # 추천을 위한 기준 제품 가져오기
    product = Product.objects.get(id=product_id)

    # TF-IDF 계산 (description 대신 category 사용)
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['description'])

    # 유사도 계산
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # 선택한 제품의 인덱스 찾기
    idx = df.index[df['id'] == product.id][0]

    # 유사도 점수 가져오기
    similarity_scores = list(enumerate(cosine_sim[idx]))

    # 유사도 점수로 정렬
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # 상위 N개 제품 추천 (자신 제외)
    recommended_indices = [i[0] for i in similarity_scores[1:top_n + 1]]

    # 추천 제품 반환
    recommended_products = df.iloc[recommended_indices]
    return Product.objects.filter(id__in=recommended_products['id'])

def collaborative_filtering_recommendations(user_id, top_n=5):
    purchases = UserPurchase.objects.all()
    purchase_data = pd.DataFrame(list(purchases.values()))

    if purchase_data.empty:
        return []

    # 사용자-상품 행렬 생성
    user_product_matrix = purchase_data.pivot(index='user_id', columns='product_id', values='purchase_date').fillna(0)

    # 코사인 유사도 계산 (사용자 간 유사도)
    user_similarity = cosine_similarity(user_product_matrix)
    user_similarities_df = pd.DataFrame(user_similarity, index=user_product_matrix.index, columns=user_product_matrix.index)

    # 현재 사용자와 가장 유사한 사용자 찾기
    similar_users = user_similarities_df[user_id].sort_values(ascending=False).index[1:top_n+1]
    
    # 유사한 사용자가 구매한 상품 추천
    recommended_products = purchase_data[purchase_data['user_id'].isin(similar_users)]['product_id'].unique()

    return Product.objects.filter(id__in=recommended_products.tolist())

# 자주 함께 구매된 제품 추천 함수
def frequently_bought_together(product_id, top_n=5):
    # 간단히 동일한 카테고리 제품 반환
    product = Product.objects.get(id=product_id)
    return Product.objects.filter(category=product.category).exclude(id=product_id)[:top_n]