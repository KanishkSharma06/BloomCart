import numpy as np
import pickle
import tensorflow as tf
from tensorflow import keras
from keras import layers, models

# Load model & mappings
model = models.load_model('recommender.keras')

with open('mappings.pkl', 'rb') as f:
    data = pickle.load(f)
    user_map = data['user_map']
    prod_map = data['prod_map']

def get_recommendations(user_id, all_product_ids, top_n=3):
    if user_id not in user_map:
        return [] # Naye user ke liye default list
    
    u_idx = user_map[user_id]
    
    valid_p_ids = []
    p_idxs = []
    
    # Valid products ki list taiyar karein jo mapping mein hain
    for p_id in all_product_ids:
        if p_id in prod_map:
            valid_p_ids.append(p_id)
            p_idxs.append(prod_map[p_id])
            
    # Yahan 'p_idxs' check hoga (jo upar define kiya gaya hai)
    if not p_idxs:
        return []

    # Arrays banayein
    u_arr = np.array([u_idx] * len(p_idxs))
    p_arr = np.array(p_idxs)
    
    # Ek hi baar mein sabhi products ke liye predict karein
    scores = model.predict([u_arr, p_arr], verbose=0).flatten()
    
    # Product IDs aur unke scores ko pair karein
    product_scores = list(zip(valid_p_ids, scores))
    
    # Score ke basis par descending order mein sort karein
    product_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Top N product IDs return karein
    return [p_id for p_id, score in product_scores[:top_n]]