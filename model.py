import pickle
import pandas as pd
import numpy as np

# Initialize machine learning models and datasets
class RecommendationEngine:
    def __init__(self):
        self.sentiment_classifier = self._load_pickle_file('logistic_regression_model.pkl')
        self.text_vectorizer = self._load_pickle_file('tfidf_vectorizer.pkl')
        self.collaborative_predictions = self._load_pickle_file('item_based_predictions.pkl')
        self.user_rating_matrix = self._load_pickle_file('user_based_predictions.pkl')
        self.product_dataset = pd.read_csv('cleaned_reviews_dataset.csv')
    
    def _load_pickle_file(self, filename):
        with open(filename, 'rb') as file:
            return pickle.load(file)
    
    def fetch_user_list(self, search_term=None):
        available_users = self.user_rating_matrix.index.tolist()
        
        if search_term:
            normalized_search = search_term.lower()
            available_users = [
                user for user in available_users 
                if normalized_search in user.lower()
            ]
        
        return sorted(available_users)
    
    def generate_product_candidates(self, target_user, candidate_limit=20):
        if target_user not in self.collaborative_predictions.index:
            print(f"Warning: User '{target_user}' not found in prediction matrix")
            return pd.Series(dtype=float)
        
        user_prediction_scores = self.collaborative_predictions.loc[target_user]
        filtered_scores = user_prediction_scores.dropna()
        
        if filtered_scores.empty:
            print(f"Warning: No valid predictions available for '{target_user}'")
            return pd.Series(dtype=float)
        
        top_candidates = filtered_scores.sort_values(ascending=False).head(candidate_limit)
        
        return top_candidates
    
    def calculate_sentiment_metric(self, product_identifier):
        product_feedback = self.product_dataset[
            self.product_dataset['name'] == product_identifier
        ]
        
        if product_feedback.empty:
            return 0.0
        
        text_features = self.text_vectorizer.transform(
            product_feedback['combined_reviews']
        )
        
        sentiment_predictions = self.sentiment_classifier.predict(text_features)
        positive_proportion = np.mean(sentiment_predictions == 'Positive')
        
        return positive_proportion
    
    def build_recommendation_set(self, username, recommendation_count=5):
        try:
            candidate_products = self.generate_product_candidates(
                username, 
                candidate_limit=20
            )
            
            if candidate_products.empty:
                print(f"No candidate products available for user: {username}")
                return []
            
            product_sentiment_map = {}
            for product_name in candidate_products.index:
                sentiment_score = self.calculate_sentiment_metric(product_name)
                product_sentiment_map[product_name] = sentiment_score
            
            ranked_products = pd.Series(product_sentiment_map)
            final_selections = (
                ranked_products
                .sort_values(ascending=False)
                .head(recommendation_count)
                .index
                .tolist()
            )
            
            detailed_recommendations = []
            for selected_product in final_selections:
                product_info = self._extract_product_details(selected_product)
                if product_info:
                    detailed_recommendations.append(product_info)
            
            print(f"Successfully generated {len(detailed_recommendations)} recommendations for {username}")
            return detailed_recommendations
        
        except Exception as error:
            print(f"Error during recommendation generation for {username}: {error}")
            import traceback
            traceback.print_exc()
            return []
    
    def _extract_product_details(self, product_name):
        product_records = self.product_dataset[
            self.product_dataset['name'] == product_name
        ]
        
        if product_records.empty:
            return None
        
        mean_rating = product_records['reviews_rating'].mean()
        positive_count = (product_records['user_sentiment'] == 'Positive').sum()
        total_feedback = len(product_records)
        positive_percentage = (positive_count / total_feedback) * 100
        
        brand_name = product_records['brand'].iloc[0]
        brand_display = brand_name if pd.notna(brand_name) else 'N/A'
        
        return {
            'product_name': product_name,
            'brand': brand_display,
            'avg_rating': round(mean_rating, 2),
            'positive_ratio': round(positive_percentage, 1),
            'total_reviews': total_feedback
        }

recommendation_system = RecommendationEngine()

def get_recommendations(username, data_file=None, top_n=5):
    return recommendation_system.build_recommendation_set(username, top_n)

def get_all_users(query=None):
    return recommendation_system.fetch_user_list(query)