import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Product  # Aapke Django Product model ke mutabiq

def get_recommendations(product_id):
    try:
        # Database se saare products fetch karein
        products = list(Product.objects.values('id', 'name', 'category', 'description'))
        if not products:
            return []
            
        df = pd.DataFrame(products)
        
        # Features ko combine karke text banayein (Category aur Name ke basis par)
        df['combined_features'] = df['category'].fillna('') + ' ' + df['name'].fillna('') + ' ' + df['description'].fillna('')
        
        # TF-IDF Vectorizer apply karein
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['combined_features'])
        
        # Cosine Similarity matrix nikalein
        cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        # Product ka index find karein
        matching_indices = df.index[df['id'] == product_id].tolist()
        if not matching_indices:
            return []
        idx = matching_indices[0]
        
        # Similar products ki list banayein
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Khud ko chhod kar top 4 products return karein
        sim_scores = sim_scores[1:5]
        product_indices = [i[0] for i in sim_scores]
        
        recommended_ids = df['id'].iloc[product_indices].tolist()
        
        # Django Queryset return karein
        recommended_products = Product.objects.filter(id__in=recommended_ids)
        return recommended_products
        
    except Exception as e:
        print(f"Recommendation Error: {e}")
        return []