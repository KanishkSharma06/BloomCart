import os
import sys
import numpy as np
import pickle
import django
import pandas as pd
import tensorflow as tf
from keras import layers, models, Model, Input

# Django environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloomcart_project.settings')
django.setup()

from store.models import OrderItem, Product

def train():
    # 1. Data load karein (yahan 'uniq_id' use kiya hai order__product__uniq_id ya product__uniq_id ke hisaab se)
    data = list(OrderItem.objects.values('order__user_id', 'product__uniq_id'))
    if not data:
        print("No data found to train!")
        return
    
    df = pd.DataFrame(data)
    df.columns = ['user_id', 'uniq_id'] # columns rename kar lete hain asani ke liye
    
    # 2. User/Product IDs ko index mein convert karein
    user_ids = df['user_id'].unique()
    prod_ids = list(Product.objects.values_list('uniq_id', flat=True)) # Yahan 'uniq_id' use kiya gaya hai
    
    user_map = {uid: i for i, uid in enumerate(user_ids)}
    prod_map = {pid: i for i, pid in enumerate(prod_ids)}
    
    # Save mappings for later use
    with open('mappings.pkl', 'wb') as f:
        pickle.dump({'user_map': user_map, 'prod_map': prod_map}, f)
    
    # Map dataset indices
    df = df[df['uniq_id'].isin(prod_map.keys())]
    df['u_idx'] = df['user_id'].map(user_map)
    df['p_idx'] = df['uniq_id'].map(prod_map)
    
    # 3. TensorFlow Model (Matrix Factorization)
    u_in = Input(shape=(1,), name='user_input')
    p_in = Input(shape=(1,), name='product_input')
    
    u_emb = layers.Embedding(len(user_ids), 32, name='user_embedding')(u_in)
    u_emb = layers.Flatten()(u_emb)
    
    p_emb = layers.Embedding(len(prod_map), 32, name='product_embedding')(p_in)
    p_emb = layers.Flatten()(p_emb)
    
    # Dot product calculation with a sigmoid layer for 0-1 range
    dot = layers.Dot(axes=1)([u_emb, p_emb])
    output = layers.Activation('sigmoid')(dot)
    
    model = Model([u_in, p_in], output)
    model.compile(optimizer='adam', loss='binary_crossentropy')
    
    print(f"Total training records found: {len(df)}")
    
    if len(df) == 0:
        print("Training dataframe is empty after filtering! Check if OrderItem has products.")
        return

    # 4. Train aur Save
    model.fit(
        [df['u_idx'].to_numpy(), df['p_idx'].to_numpy()], 
        np.ones(len(df)), 
        epochs=10,
        batch_size=32
    )
    
    model.save('recommender.keras')
    print("Model and Mappings Saved Successfully!")

if __name__ == "__main__":
    train()