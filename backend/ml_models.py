import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose
import joblib
import warnings
warnings.filterwarnings('ignore')

class ClaimsPredictionModel:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.data = None
        
    def load_data(self, csv_path):
        """Load and prepare claims data"""
        self.data = pd.read_csv(csv_path)
        self.data['date'] = pd.to_datetime(self.data['date'])
        return self.data
    
    def prepare_features(self, df):
        """Create time-based features"""
        df = df.copy()
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_year'] = df['date'].dt.dayofyear
        df['weekday'] = df['date'].dt.weekday
        df['is_weekend'] = (df['weekday'] >= 5).astype(int)
        
        # Cyclical features for seasonality
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365)
        
        return df
    
    def train_county_model(self, county, claim_type):
        """Train prediction model for specific county and claim type"""
        # Filter data
        county_data = self.data[
            (self.data['county'] == county) & 
            (self.data['claim_type'] == claim_type)
        ].copy().sort_values('date')
        
        if len(county_data) < 100:
            return None
            
        # Prepare features
        county_data = self.prepare_features(county_data)
        
        # Features for regression
        feature_cols = ['year', 'month', 'day_of_year', 'weekday', 'is_weekend',
                       'month_sin', 'month_cos', 'day_sin', 'day_cos']
        
        X = county_data[feature_cols]
        y_count = county_data['claim_count']
        y_cost = county_data['total_cost']
        
        # Train models
        # Volume prediction
        count_model = LinearRegression()
        count_model.fit(X, y_count)
        
        # Cost prediction
        cost_model = LinearRegression()
        cost_model.fit(X, y_cost)
        
        # Store models
        model_key = f"{county}_{claim_type}"
        self.models[model_key] = {
            'count_model': count_model,
            'cost_model': cost_model,
            'feature_cols': feature_cols,
            'county': county,
            'claim_type': claim_type
        }
        
        return model_key
    
    def train_all_models(self):
        """Train models for all county-claim type combinations"""
        counties = self.data['county'].unique()
        claim_types = self.data['claim_type'].unique()
        
        trained_models = []
        for county in counties:
            for claim_type in claim_types:
                model_key = self.train_county_model(county, claim_type)
                if model_key:
                    trained_models.append(model_key)
        
        print(f"Trained {len(trained_models)} models")
        return trained_models
    
    def predict_claims(self, county, claim_type, target_date):
        """Predict claims for specific county, type, and date"""
        # Validate inputs
        if self.data is not None:
            valid_counties = self.data['county'].unique()
            valid_claim_types = self.data['claim_type'].unique()
            
            if county not in valid_counties:
                return None
            if claim_type not in valid_claim_types:
                return None
        
        model_key = f"{county}_{claim_type}"
        
        if model_key not in self.models:
            return None
            
        model_info = self.models[model_key]
        
        # Prepare features for target date
        date_df = pd.DataFrame({'date': [pd.to_datetime(target_date)]})
        date_df = self.prepare_features(date_df)
        
        X_pred = date_df[model_info['feature_cols']]
        
        # Make predictions
        count_pred = model_info['count_model'].predict(X_pred)[0]
        cost_pred = model_info['cost_model'].predict(X_pred)[0]
        
        return {
            'county': county,
            'claim_type': claim_type,
            'date': str(target_date),  # Convert to string for JSON serialization
            'predicted_count': max(0, int(count_pred)),
            'predicted_cost': max(0, float(cost_pred)),
            'avg_cost_per_claim': float(cost_pred / max(1, count_pred)) if count_pred > 0 else 0.0
        }
    
    def predict_multiple_dates(self, county, claim_type, start_date, days=30):
        """Predict claims for multiple future dates"""
        predictions = []
        start = pd.to_datetime(start_date)
        
        for i in range(days):
            target_date = start + pd.Timedelta(days=i)
            pred = self.predict_claims(county, claim_type, target_date.strftime('%Y-%m-%d'))
            if pred:
                predictions.append(pred)
                
        return predictions
    
    def get_seasonal_insights(self, county, claim_type):
        """Get seasonal patterns for a county-claim type"""
        county_data = self.data[
            (self.data['county'] == county) & 
            (self.data['claim_type'] == claim_type)
        ].copy()
        
        if len(county_data) < 365:
            return None
            
        # Monthly averages
        monthly_avg = county_data.groupby(county_data['date'].dt.month).agg({
            'claim_count': 'mean',
            'total_cost': 'mean'
        }).round(2)
        
        # Day of week patterns
        dow_avg = county_data.groupby(county_data['date'].dt.weekday).agg({
            'claim_count': 'mean',
            'total_cost': 'mean'
        }).round(2)
        
        return {
            'monthly_patterns': monthly_avg.to_dict(),
            'day_of_week_patterns': dow_avg.to_dict()
        }
    
    def get_county_summary(self, county):
        """Get summary statistics for a county"""
        county_data = self.data[self.data['county'] == county]
        
        if len(county_data) == 0:
            return {}
        
        summary = county_data.groupby('claim_type').agg({
            'claim_count': ['sum', 'mean', 'std'],
            'total_cost': ['sum', 'mean', 'std']
        }).round(2)
        
        # Flatten the MultiIndex columns and convert to dict
        summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
        
        return summary.to_dict('index')
    
    def save_models(self, filepath):
        """Save trained models"""
        joblib.dump(self.models, filepath)
    
    def load_models(self, filepath):
        """Load trained models"""
        self.models = joblib.load(filepath)

# Usage example
if __name__ == "__main__":
    # Initialize and train models
    predictor = ClaimsPredictionModel()
    
    # Load data
    print("Loading data...")
    data = predictor.load_data('../data/kansas_claims_10years.csv')
    print(f"Loaded {len(data)} records")
    
    # Train models
    print("Training models...")
    trained = predictor.train_all_models()
    
    # Example predictions
    print("\nExample predictions:")
    pred = predictor.predict_claims('Johnson', 'emergency', '2025-01-15')
    if pred:
        print(f"Johnson County emergency claims on 2025-01-15:")
        print(f"  Count: {pred['predicted_count']}")
        print(f"  Cost: ${pred['predicted_cost']:,.2f}")
    
    # Save models
    predictor.save_models('../models/claims_models.pkl')
    print("Models saved!")