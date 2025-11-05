# Module 2: CRM Data Integration & Analysis
*Duration: 10 hours | Weeks 3-4*

## 🎯 Learning Objectives

By the end of this module, participants will:
- Master data collection and preparation techniques from multiple sources
- Implement AI-powered customer segmentation and analysis
- Create comprehensive performance metrics and analytics
- Build automated data processing pipelines
- Generate actionable insights from CRM data

---

## 📚 Module Content

### 2.1 Data Collection and Preparation (4 hours)

#### 2.1.1 Data Sources Integration

**Primary CRM Data Sources**

**Contact and Lead Data**
```python
# Example: Comprehensive contact data extraction
import pandas as pd
import requests
from datetime import datetime, timedelta

class CRMDataExtractor:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def extract_contacts(self, limit=1000, properties=None):
        """
        Extract contact data from CRM
        """
        if properties is None:
            properties = [
                'firstname', 'lastname', 'email', 'phone', 'company',
                'industry', 'lifecyclestage', 'leadstatus', 'createdate',
                'lastmodifieddate', 'hs_lead_score', 'num_conversion_events'
            ]
        
        url = f"{self.base_url}/crm/v3/objects/contacts"
        params = {
            'limit': limit,
            'properties': ','.join(properties)
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            contacts = []
            for contact in data.get('results', []):
                contact_data = {
                    'id': contact.get('id'),
                    'created_at': contact.get('createdAt'),
                    'updated_at': contact.get('updatedAt'),
                    'properties': contact.get('properties', {})
                }
                contacts.append(contact_data)
            
            return pd.DataFrame(contacts)
        else:
            print(f"Error extracting contacts: {response.status_code}")
            return None

# Example usage
extractor = CRMDataExtractor('your_api_key', 'https://api.hubspot.com')
contacts_df = extractor.extract_contacts(limit=5000)
```

**Campaign Performance Data**
```python
def extract_campaign_data(self, start_date, end_date):
    """
    Extract marketing campaign performance data
    """
    url = f"{self.base_url}/marketing/v3/campaigns"
    params = {
        'startDate': start_date,
        'endDate': end_date,
        'limit': 1000
    }
    
    response = requests.get(url, headers=self.headers, params=params)
    
    if response.status_code == 200:
        campaigns = response.json().get('results', [])
        campaign_data = []
        
        for campaign in campaigns:
            campaign_info = {
                'id': campaign.get('id'),
                'name': campaign.get('name'),
                'type': campaign.get('type'),
                'status': campaign.get('status'),
                'created_at': campaign.get('createdAt'),
                'start_date': campaign.get('startDate'),
                'end_date': campaign.get('endDate'),
                'num_recipients': campaign.get('numRecipients', 0),
                'num_opens': campaign.get('numOpens', 0),
                'num_clicks': campaign.get('numClicks', 0),
                'num_conversions': campaign.get('numConversions', 0)
            }
            campaign_data.append(campaign_info)
        
        return pd.DataFrame(campaign_data)
    else:
        print(f"Error extracting campaigns: {response.status_code}")
        return None
```

**Sales Pipeline Data**
```python
def extract_deals_data(self, pipeline_id=None):
    """
    Extract sales deals and pipeline data
    """
    url = f"{self.base_url}/crm/v3/objects/deals"
    params = {
        'limit': 1000,
        'properties': 'dealname,amount,dealstage,closedate,createdate,hs_deal_stage_probability'
    }
    
    if pipeline_id:
        params['filter'] = f'pipeline={pipeline_id}'
    
    response = requests.get(url, headers=self.headers, params=params)
    
    if response.status_code == 200:
        deals = response.json().get('results', [])
        deals_data = []
        
        for deal in deals:
            deal_info = {
                'id': deal.get('id'),
                'name': deal.get('properties', {}).get('dealname'),
                'amount': float(deal.get('properties', {}).get('amount', 0)),
                'stage': deal.get('properties', {}).get('dealstage'),
                'probability': float(deal.get('properties', {}).get('hs_deal_stage_probability', 0)),
                'close_date': deal.get('properties', {}).get('closedate'),
                'created_at': deal.get('createdAt')
            }
            deals_data.append(deal_info)
        
        return pd.DataFrame(deals_data)
    else:
        print(f"Error extracting deals: {response.status_code}")
        return None
```

**External Data Sources Integration**

**Google Analytics Integration**
```python
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

class GoogleAnalyticsExtractor:
    def __init__(self, property_id):
        self.property_id = property_id
        self.client = BetaAnalyticsDataClient()
    
    def extract_website_data(self, start_date, end_date):
        """
        Extract website analytics data
        """
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="date"),
                Dimension(name="source"),
                Dimension(name="medium"),
                Dimension(name="campaign")
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="users"),
                Metric(name="pageviews"),
                Metric(name="conversions"),
                Metric(name="conversionRate")
            ],
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
        )
        
        response = self.client.run_report(request)
        
        data = []
        for row in response.rows:
            data.append({
                'date': row.dimension_values[0].value,
                'source': row.dimension_values[1].value,
                'medium': row.dimension_values[2].value,
                'campaign': row.dimension_values[3].value,
                'sessions': int(row.metric_values[0].value),
                'users': int(row.metric_values[1].value),
                'pageviews': int(row.metric_values[2].value),
                'conversions': int(row.metric_values[3].value),
                'conversion_rate': float(row.metric_values[4].value)
            })
        
        return pd.DataFrame(data)
```

**Social Media Data Integration**
```python
import tweepy
from facebook_business import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

class SocialMediaExtractor:
    def __init__(self, twitter_credentials, facebook_credentials):
        self.twitter_auth = tweepy.OAuthHandler(
            twitter_credentials['consumer_key'],
            twitter_credentials['consumer_secret']
        )
        self.twitter_auth.set_access_token(
            twitter_credentials['access_token'],
            twitter_credentials['access_token_secret']
        )
        self.twitter_api = tweepy.API(self.twitter_auth)
        
        FacebookAdsApi.init(
            facebook_credentials['app_id'],
            facebook_credentials['app_secret'],
            facebook_credentials['access_token']
        )
        self.ad_account = AdAccount(f"act_{facebook_credentials['ad_account_id']}")
    
    def extract_twitter_data(self, hashtags, limit=1000):
        """
        Extract Twitter engagement data
        """
        tweets_data = []
        for hashtag in hashtags:
            tweets = tweepy.Cursor(
                self.twitter_api.search_tweets,
                q=f"#{hashtag}",
                lang="en",
                tweet_mode="extended"
            ).items(limit)
            
            for tweet in tweets:
                tweets_data.append({
                    'id': tweet.id,
                    'text': tweet.full_text,
                    'created_at': tweet.created_at,
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count,
                    'hashtag': hashtag
                })
        
        return pd.DataFrame(tweets_data)
    
    def extract_facebook_ads_data(self, start_date, end_date):
        """
        Extract Facebook ads performance data
        """
        insights = self.ad_account.get_insights(
            fields=[
                'campaign_name',
                'impressions',
                'clicks',
                'spend',
                'conversions',
                'cost_per_conversion'
            ],
            params={
                'time_range': {
                    'since': start_date,
                    'until': end_date
                },
                'level': 'campaign'
            }
        )
        
        ads_data = []
        for insight in insights:
            ads_data.append({
                'campaign_name': insight.get('campaign_name'),
                'impressions': int(insight.get('impressions', 0)),
                'clicks': int(insight.get('clicks', 0)),
                'spend': float(insight.get('spend', 0)),
                'conversions': int(insight.get('conversions', 0)),
                'cost_per_conversion': float(insight.get('cost_per_conversion', 0))
            })
        
        return pd.DataFrame(ads_data)
```

#### 2.1.2 Data Cleaning and Standardization

**Data Quality Assessment**
```python
def assess_data_quality(df, data_type='contacts'):
    """
    Assess data quality and identify issues
    """
    quality_report = {
        'total_records': len(df),
        'missing_values': df.isnull().sum().to_dict(),
        'duplicate_records': df.duplicated().sum(),
        'data_types': df.dtypes.to_dict(),
        'unique_values': df.nunique().to_dict()
    }
    
    # Calculate completeness percentage
    completeness = (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    quality_report['completeness_percentage'] = completeness
    
    # Identify potential issues
    issues = []
    if completeness < 80:
        issues.append("Low data completeness - consider data enrichment")
    
    if quality_report['duplicate_records'] > 0:
        issues.append(f"Found {quality_report['duplicate_records']} duplicate records")
    
    quality_report['issues'] = issues
    
    return quality_report

# Example usage
quality_report = assess_data_quality(contacts_df, 'contacts')
print(f"Data completeness: {quality_report['completeness_percentage']:.2f}%")
```

**Data Cleaning Functions**
```python
def clean_contact_data(df):
    """
    Clean and standardize contact data
    """
    # Remove duplicates
    df_clean = df.drop_duplicates(subset=['id'])
    
    # Clean email addresses
    if 'email' in df_clean.columns:
        df_clean['email'] = df_clean['email'].str.lower().str.strip()
        df_clean = df_clean[df_clean['email'].str.contains('@', na=False)]
    
    # Standardize phone numbers
    if 'phone' in df_clean.columns:
        df_clean['phone'] = df_clean['phone'].str.replace(r'[^\d+]', '', regex=True)
    
    # Clean company names
    if 'company' in df_clean.columns:
        df_clean['company'] = df_clean['company'].str.strip().str.title()
    
    # Standardize industry names
    if 'industry' in df_clean.columns:
        industry_mapping = {
            'tech': 'Technology',
            'it': 'Technology',
            'software': 'Technology',
            'fintech': 'Financial Technology',
            'healthcare': 'Healthcare',
            'health': 'Healthcare',
            'education': 'Education',
            'edu': 'Education'
        }
        df_clean['industry'] = df_clean['industry'].str.lower().map(industry_mapping).fillna(df_clean['industry'])
    
    # Convert date columns
    date_columns = ['created_at', 'updated_at', 'close_date']
    for col in date_columns:
        if col in df_clean.columns:
            df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
    
    return df_clean

def clean_campaign_data(df):
    """
    Clean and standardize campaign data
    """
    # Remove campaigns with no data
    df_clean = df[df['num_recipients'] > 0]
    
    # Calculate derived metrics
    df_clean['open_rate'] = (df_clean['num_opens'] / df_clean['num_recipients'] * 100).round(2)
    df_clean['click_rate'] = (df_clean['num_clicks'] / df_clean['num_recipients'] * 100).round(2)
    df_clean['conversion_rate'] = (df_clean['num_conversions'] / df_clean['num_recipients'] * 100).round(2)
    
    # Standardize campaign types
    type_mapping = {
        'email': 'Email Marketing',
        'social': 'Social Media',
        'paid': 'Paid Advertising',
        'organic': 'Organic Marketing',
        'content': 'Content Marketing'
    }
    df_clean['type'] = df_clean['type'].str.lower().map(type_mapping).fillna(df_clean['type'])
    
    return df_clean
```

**Data Validation**
```python
def validate_data(df, validation_rules):
    """
    Validate data against business rules
    """
    validation_results = {
        'passed': True,
        'errors': [],
        'warnings': []
    }
    
    for rule in validation_rules:
        column = rule['column']
        rule_type = rule['type']
        value = rule['value']
        
        if rule_type == 'not_null':
            null_count = df[column].isnull().sum()
            if null_count > 0:
                validation_results['errors'].append(f"Column {column} has {null_count} null values")
                validation_results['passed'] = False
        
        elif rule_type == 'min_value':
            below_min = (df[column] < value).sum()
            if below_min > 0:
                validation_results['warnings'].append(f"Column {column} has {below_min} values below {value}")
        
        elif rule_type == 'max_value':
            above_max = (df[column] > value).sum()
            if above_max > 0:
                validation_results['warnings'].append(f"Column {column} has {above_max} values above {value}")
        
        elif rule_type == 'email_format':
            invalid_emails = df[column].str.contains(r'^[^@]+@[^@]+\.[^@]+$', regex=True, na=False)
            invalid_count = (~invalid_emails).sum()
            if invalid_count > 0:
                validation_results['errors'].append(f"Column {column} has {invalid_count} invalid email formats")
                validation_results['passed'] = False
    
    return validation_results

# Example validation rules
contact_validation_rules = [
    {'column': 'email', 'type': 'not_null'},
    {'column': 'email', 'type': 'email_format'},
    {'column': 'hs_lead_score', 'type': 'min_value', 'value': 0},
    {'column': 'hs_lead_score', 'type': 'max_value', 'value': 100}
]

validation_results = validate_data(contacts_df, contact_validation_rules)
```

### 2.2 AI-Powered Data Analysis (4 hours)

#### 2.2.1 Customer Segmentation with AI

**RFM Analysis Implementation**
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np

class RFMAnalyzer:
    def __init__(self, df):
        self.df = df
        self.rfm_df = None
    
    def calculate_rfm(self, customer_id_col, date_col, value_col):
        """
        Calculate RFM (Recency, Frequency, Monetary) scores
        """
        # Calculate recency (days since last interaction)
        max_date = self.df[date_col].max()
        self.df['recency'] = (max_date - self.df[date_col]).dt.days
        
        # Calculate frequency (number of interactions)
        frequency = self.df.groupby(customer_id_col)[date_col].count().reset_index()
        frequency.columns = [customer_id_col, 'frequency']
        
        # Calculate monetary value (total value)
        monetary = self.df.groupby(customer_id_col)[value_col].sum().reset_index()
        monetary.columns = [customer_id_col, 'monetary']
        
        # Merge data
        self.rfm_df = self.df.groupby(customer_id_col).agg({
            'recency': 'min',
            'frequency': 'count',
            'value_col': 'sum'
        }).reset_index()
        
        # Rename columns
        self.rfm_df.columns = [customer_id_col, 'recency', 'frequency', 'monetary']
        
        return self.rfm_df
    
    def calculate_rfm_scores(self):
        """
        Calculate RFM scores (1-5 scale)
        """
        # Recency score (lower is better)
        self.rfm_df['recency_score'] = pd.qcut(
            self.rfm_df['recency'], 
            q=5, 
            labels=[5, 4, 3, 2, 1]
        ).astype(int)
        
        # Frequency score (higher is better)
        self.rfm_df['frequency_score'] = pd.qcut(
            self.rfm_df['frequency'], 
            q=5, 
            labels=[1, 2, 3, 4, 5]
        ).astype(int)
        
        # Monetary score (higher is better)
        self.rfm_df['monetary_score'] = pd.qcut(
            self.rfm_df['monetary'], 
            q=5, 
            labels=[1, 2, 3, 4, 5]
        ).astype(int)
        
        # Calculate RFM score
        self.rfm_df['rfm_score'] = (
            self.rfm_df['recency_score'].astype(str) +
            self.rfm_df['frequency_score'].astype(str) +
            self.rfm_df['monetary_score'].astype(str)
        )
        
        return self.rfm_df
    
    def segment_customers(self):
        """
        Segment customers based on RFM scores
        """
        segment_map = {
            '555': 'Champions',
            '554': 'Champions',
            '544': 'Champions',
            '545': 'Champions',
            '454': 'Loyal Customers',
            '455': 'Loyal Customers',
            '445': 'Loyal Customers',
            '444': 'Loyal Customers',
            '543': 'Potential Loyalists',
            '542': 'Potential Loyalists',
            '541': 'Potential Loyalists',
            '533': 'Potential Loyalists',
            '532': 'Potential Loyalists',
            '531': 'Potential Loyalists',
            '522': 'New Customers',
            '521': 'New Customers',
            '515': 'New Customers',
            '514': 'New Customers',
            '513': 'New Customers',
            '512': 'New Customers',
            '511': 'New Customers',
            '435': 'Promising',
            '434': 'Promising',
            '433': 'Promising',
            '432': 'Promising',
            '431': 'Promising',
            '425': 'Promising',
            '424': 'Promising',
            '423': 'Promising',
            '422': 'Promising',
            '421': 'Promising',
            '415': 'Promising',
            '414': 'Promising',
            '413': 'Promising',
            '412': 'Promising',
            '411': 'Promising',
            '355': 'Need Attention',
            '354': 'Need Attention',
            '353': 'Need Attention',
            '352': 'Need Attention',
            '351': 'Need Attention',
            '345': 'Need Attention',
            '344': 'Need Attention',
            '343': 'Need Attention',
            '342': 'Need Attention',
            '341': 'Need Attention',
            '335': 'Need Attention',
            '334': 'Need Attention',
            '333': 'Need Attention',
            '332': 'Need Attention',
            '331': 'Need Attention',
            '325': 'Need Attention',
            '324': 'Need Attention',
            '323': 'Need Attention',
            '322': 'Need Attention',
            '321': 'Need Attention',
            '315': 'Need Attention',
            '314': 'Need Attention',
            '313': 'Need Attention',
            '312': 'Need Attention',
            '311': 'Need Attention',
            '255': 'About to Sleep',
            '254': 'About to Sleep',
            '253': 'About to Sleep',
            '252': 'About to Sleep',
            '251': 'About to Sleep',
            '245': 'About to Sleep',
            '244': 'About to Sleep',
            '243': 'About to Sleep',
            '242': 'About to Sleep',
            '241': 'About to Sleep',
            '235': 'About to Sleep',
            '234': 'About to Sleep',
            '233': 'About to Sleep',
            '232': 'About to Sleep',
            '231': 'About to Sleep',
            '225': 'About to Sleep',
            '224': 'About to Sleep',
            '223': 'About to Sleep',
            '222': 'About to Sleep',
            '221': 'About to Sleep',
            '215': 'About to Sleep',
            '214': 'About to Sleep',
            '213': 'About to Sleep',
            '212': 'About to Sleep',
            '211': 'About to Sleep',
            '155': 'At Risk',
            '154': 'At Risk',
            '153': 'At Risk',
            '152': 'At Risk',
            '151': 'At Risk',
            '145': 'At Risk',
            '144': 'At Risk',
            '143': 'At Risk',
            '142': 'At Risk',
            '141': 'At Risk',
            '135': 'At Risk',
            '134': 'At Risk',
            '133': 'At Risk',
            '132': 'At Risk',
            '131': 'At Risk',
            '125': 'At Risk',
            '124': 'At Risk',
            '123': 'At Risk',
            '122': 'At Risk',
            '121': 'At Risk',
            '115': 'At Risk',
            '114': 'At Risk',
            '113': 'At Risk',
            '112': 'At Risk',
            '111': 'At Risk',
            '055': 'Cannot Lose Them',
            '054': 'Cannot Lose Them',
            '053': 'Cannot Lose Them',
            '052': 'Cannot Lose Them',
            '051': 'Cannot Lose Them',
            '045': 'Cannot Lose Them',
            '044': 'Cannot Lose Them',
            '043': 'Cannot Lose Them',
            '042': 'Cannot Lose Them',
            '041': 'Cannot Lose Them',
            '035': 'Cannot Lose Them',
            '034': 'Cannot Lose Them',
            '033': 'Cannot Lose Them',
            '032': 'Cannot Lose Them',
            '031': 'Cannot Lose Them',
            '025': 'Cannot Lose Them',
            '024': 'Cannot Lose Them',
            '023': 'Cannot Lose Them',
            '022': 'Cannot Lose Them',
            '021': 'Cannot Lose Them',
            '015': 'Cannot Lose Them',
            '014': 'Cannot Lose Them',
            '013': 'Cannot Lose Them',
            '012': 'Cannot Lose Them',
            '011': 'Cannot Lose Them',
            '005': 'Lost',
            '004': 'Lost',
            '003': 'Lost',
            '002': 'Lost',
            '001': 'Lost'
        }
        
        self.rfm_df['segment'] = self.rfm_df['rfm_score'].map(segment_map).fillna('Unknown')
        
        return self.rfm_df

# Example usage
rfm_analyzer = RFMAnalyzer(interactions_df)
rfm_df = rfm_analyzer.calculate_rfm('customer_id', 'interaction_date', 'value')
rfm_df = rfm_analyzer.calculate_rfm_scores()
rfm_df = rfm_analyzer.segment_customers()
```

**AI-Powered Customer Clustering**
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

class CustomerClustering:
    def __init__(self, df):
        self.df = df
        self.scaler = StandardScaler()
        self.model = None
        self.clusters = None
    
    def prepare_features(self, feature_columns):
        """
        Prepare features for clustering
        """
        # Select and clean features
        features = self.df[feature_columns].fillna(0)
        
        # Handle categorical variables
        categorical_cols = features.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            features[col] = pd.Categorical(features[col]).codes
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        return features_scaled, features.columns.tolist()
    
    def find_optimal_clusters(self, features, max_clusters=10):
        """
        Find optimal number of clusters using elbow method and silhouette score
        """
        inertias = []
        silhouette_scores = []
        
        for k in range(2, max_clusters + 1):
            kmeans = KMeans(n_clusters=k, random_state=42)
            kmeans.fit(features)
            
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(features, kmeans.labels_))
        
        # Find optimal k (elbow point)
        optimal_k = 2
        for i in range(1, len(inertias) - 1):
            if inertias[i] - inertias[i+1] < inertias[i-1] - inertias[i]:
                optimal_k = i + 2
                break
        
        return optimal_k, inertias, silhouette_scores
    
    def cluster_customers(self, feature_columns, n_clusters=None):
        """
        Cluster customers using K-means
        """
        features_scaled, feature_names = self.prepare_features(feature_columns)
        
        if n_clusters is None:
            n_clusters, _, _ = self.find_optimal_clusters(features_scaled)
        
        # Fit K-means model
        self.model = KMeans(n_clusters=n_clusters, random_state=42)
        self.clusters = self.model.fit_predict(features_scaled)
        
        # Add cluster labels to dataframe
        self.df['cluster'] = self.clusters
        
        # Calculate cluster characteristics
        cluster_summary = self.df.groupby('cluster')[feature_columns].mean()
        
        return self.df, cluster_summary

# Example usage
clustering = CustomerClustering(contacts_df)
feature_columns = ['hs_lead_score', 'num_conversion_events', 'days_since_last_activity']
clustered_df, cluster_summary = clustering.cluster_customers(feature_columns)
```

**Predictive Customer Scoring**
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

class CustomerScoring:
    def __init__(self, df):
        self.df = df
        self.model = None
        self.feature_importance = None
    
    def prepare_training_data(self, target_column, feature_columns):
        """
        Prepare data for model training
        """
        # Clean and prepare features
        features = self.df[feature_columns].fillna(0)
        
        # Handle categorical variables
        categorical_cols = features.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            features[col] = pd.Categorical(features[col]).codes
        
        # Prepare target variable
        target = self.df[target_column]
        
        return features, target
    
    def train_model(self, target_column, feature_columns, test_size=0.2):
        """
        Train Random Forest model for customer scoring
        """
        features, target = self.prepare_training_data(target_column, feature_columns)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, target, test_size=test_size, random_state=42
        )
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = self.model.predict(X_test)
        
        # Calculate feature importance
        self.feature_importance = pd.DataFrame({
            'feature': features.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        # Evaluate model
        print("Model Performance:")
        print(classification_report(y_test, y_pred))
        
        return self.model, self.feature_importance
    
    def predict_customer_score(self, customer_data):
        """
        Predict customer score for new data
        """
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Prepare customer data
        features = customer_data[self.model.feature_names_in_].fillna(0)
        
        # Make prediction
        score = self.model.predict_proba(features)[0][1]  # Probability of positive class
        
        return score

# Example usage
scoring = CustomerScoring(contacts_df)
feature_columns = ['hs_lead_score', 'num_conversion_events', 'days_since_last_activity', 'industry']
target_column = 'converted'  # Binary target variable

model, importance = scoring.train_model(target_column, feature_columns)
```

#### 2.2.2 Performance Metrics Analysis

**Campaign Performance Analysis**
```python
class CampaignAnalyzer:
    def __init__(self, campaigns_df, contacts_df):
        self.campaigns_df = campaigns_df
        self.contacts_df = contacts_df
        self.analysis_results = {}
    
    def calculate_campaign_metrics(self):
        """
        Calculate comprehensive campaign metrics
        """
        metrics = {}
        
        # Basic metrics
        metrics['total_campaigns'] = len(self.campaigns_df)
        metrics['total_recipients'] = self.campaigns_df['num_recipients'].sum()
        metrics['total_opens'] = self.campaigns_df['num_opens'].sum()
        metrics['total_clicks'] = self.campaigns_df['num_clicks'].sum()
        metrics['total_conversions'] = self.campaigns_df['num_conversions'].sum()
        
        # Calculated metrics
        metrics['overall_open_rate'] = (metrics['total_opens'] / metrics['total_recipients'] * 100).round(2)
        metrics['overall_click_rate'] = (metrics['total_clicks'] / metrics['total_recipients'] * 100).round(2)
        metrics['overall_conversion_rate'] = (metrics['total_conversions'] / metrics['total_recipients'] * 100).round(2)
        
        # Performance by campaign type
        type_performance = self.campaigns_df.groupby('type').agg({
            'num_recipients': 'sum',
            'num_opens': 'sum',
            'num_clicks': 'sum',
            'num_conversions': 'sum'
        }).reset_index()
        
        type_performance['open_rate'] = (type_performance['num_opens'] / type_performance['num_recipients'] * 100).round(2)
        type_performance['click_rate'] = (type_performance['num_clicks'] / type_performance['num_recipients'] * 100).round(2)
        type_performance['conversion_rate'] = (type_performance['num_conversions'] / type_performance['num_recipients'] * 100).round(2)
        
        metrics['type_performance'] = type_performance
        
        # Top performing campaigns
        top_campaigns = self.campaigns_df.nlargest(10, 'conversion_rate')
        metrics['top_campaigns'] = top_campaigns
        
        self.analysis_results = metrics
        return metrics
    
    def analyze_campaign_trends(self, date_col='created_at'):
        """
        Analyze campaign performance trends over time
        """
        # Convert date column
        self.campaigns_df[date_col] = pd.to_datetime(self.campaigns_df[date_col])
        
        # Group by month
        monthly_trends = self.campaigns_df.groupby(
            self.campaigns_df[date_col].dt.to_period('M')
        ).agg({
            'num_recipients': 'sum',
            'num_opens': 'sum',
            'num_clicks': 'sum',
            'num_conversions': 'sum'
        }).reset_index()
        
        monthly_trends['open_rate'] = (monthly_trends['num_opens'] / monthly_trends['num_recipients'] * 100).round(2)
        monthly_trends['click_rate'] = (monthly_trends['num_clicks'] / monthly_trends['num_recipients'] * 100).round(2)
        monthly_trends['conversion_rate'] = (monthly_trends['num_conversions'] / monthly_trends['num_recipients'] * 100).round(2)
        
        return monthly_trends

# Example usage
campaign_analyzer = CampaignAnalyzer(campaigns_df, contacts_df)
campaign_metrics = campaign_analyzer.calculate_campaign_metrics()
monthly_trends = campaign_analyzer.analyze_campaign_trends()
```

**ROI Analysis and Optimization**
```python
class ROIAnalyzer:
    def __init__(self, campaigns_df, deals_df):
        self.campaigns_df = campaigns_df
        self.deals_df = deals_df
        self.roi_analysis = {}
    
    def calculate_campaign_roi(self, cost_column='spend', revenue_column='amount'):
        """
        Calculate ROI for each campaign
        """
        # Merge campaign and deal data
        merged_df = self.campaigns_df.merge(
            self.deals_df, 
            left_on='id', 
            right_on='campaign_id', 
            how='left'
        )
        
        # Calculate ROI metrics
        merged_df['roi'] = ((merged_df[revenue_column] - merged_df[cost_column]) / merged_df[cost_column] * 100).round(2)
        merged_df['roas'] = (merged_df[revenue_column] / merged_df[cost_column]).round(2)
        merged_df['profit_margin'] = ((merged_df[revenue_column] - merged_df[cost_column]) / merged_df[revenue_column] * 100).round(2)
        
        # Group by campaign
        campaign_roi = merged_df.groupby('campaign_name').agg({
            cost_column: 'sum',
            revenue_column: 'sum',
            'roi': 'mean',
            'roas': 'mean',
            'profit_margin': 'mean'
        }).reset_index()
        
        # Sort by ROI
        campaign_roi = campaign_roi.sort_values('roi', ascending=False)
        
        self.roi_analysis = campaign_roi
        return campaign_roi
    
    def identify_optimization_opportunities(self):
        """
        Identify campaigns with optimization potential
        """
        opportunities = []
        
        # Low ROI campaigns
        low_roi = self.roi_analysis[self.roi_analysis['roi'] < 0]
        if len(low_roi) > 0:
            opportunities.append({
                'type': 'Low ROI',
                'count': len(low_roi),
                'campaigns': low_roi['campaign_name'].tolist(),
                'recommendation': 'Consider pausing or optimizing these campaigns'
            })
        
        # High potential campaigns
        high_potential = self.roi_analysis[
            (self.roi_analysis['roi'] > 0) & 
            (self.roi_analysis['roi'] < 100)
        ]
        if len(high_potential) > 0:
            opportunities.append({
                'type': 'High Potential',
                'count': len(high_potential),
                'campaigns': high_potential['campaign_name'].tolist(),
                'recommendation': 'Scale up these campaigns for better returns'
            })
        
        return opportunities

# Example usage
roi_analyzer = ROIAnalyzer(campaigns_df, deals_df)
roi_analysis = roi_analyzer.calculate_campaign_roi()
opportunities = roi_analyzer.identify_optimization_opportunities()
```

### 2.3 Hands-on Exercise (2 hours)

#### 2.3.1 Exercise 1: Data Integration and Cleaning

**Step 1: Multi-Source Data Integration**
```python
# Create comprehensive data integration script
def integrate_all_data_sources():
    """
    Integrate data from multiple sources
    """
    # Initialize extractors
    crm_extractor = CRMDataExtractor('your_api_key', 'https://api.hubspot.com')
    ga_extractor = GoogleAnalyticsExtractor('your_property_id')
    social_extractor = SocialMediaExtractor(twitter_creds, facebook_creds)
    
    # Extract data
    contacts_df = crm_extractor.extract_contacts()
    campaigns_df = crm_extractor.extract_campaign_data('2024-01-01', '2024-12-31')
    deals_df = crm_extractor.extract_deals_data()
    website_df = ga_extractor.extract_website_data('2024-01-01', '2024-12-31')
    social_df = social_extractor.extract_twitter_data(['marketing', 'ai', 'crm'])
    
    # Clean data
    contacts_clean = clean_contact_data(contacts_df)
    campaigns_clean = clean_campaign_data(campaigns_df)
    
    # Validate data
    contact_validation = validate_data(contacts_clean, contact_validation_rules)
    campaign_validation = validate_data(campaigns_clean, campaign_validation_rules)
    
    return {
        'contacts': contacts_clean,
        'campaigns': campaigns_clean,
        'deals': deals_df,
        'website': website_df,
        'social': social_df,
        'validation': {
            'contacts': contact_validation,
            'campaigns': campaign_validation
        }
    }

# Execute integration
integrated_data = integrate_all_data_sources()
```

**Step 2: Customer Segmentation Analysis**
```python
# Perform comprehensive customer segmentation
def perform_customer_segmentation(contacts_df):
    """
    Perform multiple customer segmentation analyses
    """
    # RFM Analysis
    rfm_analyzer = RFMAnalyzer(contacts_df)
    rfm_df = rfm_analyzer.calculate_rfm('id', 'created_at', 'hs_lead_score')
    rfm_df = rfm_analyzer.calculate_rfm_scores()
    rfm_df = rfm_analyzer.segment_customers()
    
    # Clustering Analysis
    clustering = CustomerClustering(contacts_df)
    feature_columns = ['hs_lead_score', 'num_conversion_events', 'days_since_last_activity']
    clustered_df, cluster_summary = clustering.cluster_customers(feature_columns)
    
    # Predictive Scoring
    scoring = CustomerScoring(contacts_df)
    model, importance = scoring.train_model('converted', feature_columns)
    
    return {
        'rfm_analysis': rfm_df,
        'clustering': clustered_df,
        'cluster_summary': cluster_summary,
        'scoring_model': model,
        'feature_importance': importance
    }

# Execute segmentation
segmentation_results = perform_customer_segmentation(integrated_data['contacts'])
```

**Step 3: Performance Analysis**
```python
# Perform comprehensive performance analysis
def perform_performance_analysis(campaigns_df, deals_df):
    """
    Perform comprehensive performance analysis
    """
    # Campaign Analysis
    campaign_analyzer = CampaignAnalyzer(campaigns_df, integrated_data['contacts'])
    campaign_metrics = campaign_analyzer.calculate_campaign_metrics()
    monthly_trends = campaign_analyzer.analyze_campaign_trends()
    
    # ROI Analysis
    roi_analyzer = ROIAnalyzer(campaigns_df, deals_df)
    roi_analysis = roi_analyzer.calculate_campaign_roi()
    opportunities = roi_analyzer.identify_optimization_opportunities()
    
    return {
        'campaign_metrics': campaign_metrics,
        'monthly_trends': monthly_trends,
        'roi_analysis': roi_analysis,
        'optimization_opportunities': opportunities
    }

# Execute performance analysis
performance_results = perform_performance_analysis(
    integrated_data['campaigns'], 
    integrated_data['deals']
)
```

---

## 📋 Module 2 Assessment

### **Assignment 1: Data Integration Project (40%)**
**Due:** End of Week 3

**Task:** Integrate data from multiple sources and create comprehensive dataset
**Deliverables:**
- Working data integration scripts
- Cleaned and validated datasets
- Data quality assessment report
- Integration documentation

**Evaluation Criteria:**
- Data integration completeness
- Data quality and validation
- Code quality and documentation
- Error handling and robustness

### **Assignment 2: Customer Segmentation Analysis (30%)**
**Due:** End of Week 4

**Task:** Perform comprehensive customer segmentation using multiple methods
**Deliverables:**
- RFM analysis results
- Customer clustering implementation
- Predictive scoring model
- Segmentation insights and recommendations

**Evaluation Criteria:**
- Analysis methodology and accuracy
- Model performance and validation
- Insight quality and business relevance
- Technical implementation quality

### **Assignment 3: Performance Analysis Report (30%)**
**Due:** End of Week 4

**Task:** Create comprehensive performance analysis with actionable insights
**Deliverables:**
- Campaign performance metrics
- ROI analysis and optimization recommendations
- Trend analysis and forecasting
- Executive summary with key findings

**Evaluation Criteria:**
- Analysis depth and accuracy
- Insight quality and actionability
- Report clarity and presentation
- Business impact and recommendations

---

## 🛠️ Tools and Resources

### **Required Libraries**
```python
# Data processing
import pandas as pd
import numpy as np

# Machine learning
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, silhouette_score

# API integration
import requests
from google.analytics.data_v1beta import BetaAnalyticsDataClient
import tweepy
from facebook_business import FacebookAdsApi

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
```

### **Data Sources**
- CRM system (Salesforce, HubSpot, Pipedrive)
- Google Analytics
- Social media platforms (Twitter, Facebook, LinkedIn)
- Email marketing platforms
- Website analytics tools

### **Additional Tools**
- Jupyter Notebook for data analysis
- Postman for API testing
- Tableau/Power BI for visualization
- Git for version control

---

## 🎯 Next Steps

After completing Module 2, participants will:
- Have mastered data integration from multiple sources
- Understand customer segmentation and analysis techniques
- Be able to perform comprehensive performance analysis
- Have built automated data processing pipelines
- Be ready to move on to Module 3: Custom Report Generation with AI

**Preparation for Module 3:**
- Review AI content generation techniques
- Practice with different AI platforms
- Explore report design and formatting
- Familiarize with automation tools

---

*"Transform raw CRM data into actionable insights with AI-powered analysis and segmentation."* 📊🔍✨

