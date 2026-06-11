🛒 Shopee Product Recommendation System using Aspect-Based Sentiment Analysis (ABSA)
📌 Overview

This project builds an intelligent product recommendation system for Shopee by combining:

Aspect-Based Sentiment Analysis (ABSA)
Product ratings
Sales volume
Price competitiveness
Review confidence

Instead of recommending products based solely on ratings or sales, the system analyzes customer reviews to understand sentiment toward specific product aspects and generates a comprehensive Buy Score.

🎯 Objectives

Traditional e-commerce rankings often rely on:

Average rating
Number of sales
Product popularity

However, these metrics may not reflect actual customer satisfaction.

This project aims to:

Extract aspect-level sentiment from product reviews
Evaluate products more comprehensively
Recommend the most worthwhile products
Provide explainable recommendations
🏗 System Architecture
Customer Reviews
        │
        ▼
Aspect-Based Sentiment Analysis
(PhoBERT Models)
        │
        ▼
Aspect Scores
        │
        ├── Rating Score
        ├── Price Score
        ├── Sales Score
        └── Review Confidence Score
        │
        ▼
Buy Score Engine
        │
        ▼
Product Ranking Dashboard
📊 Dataset
ViSFD Dataset

Vietnamese Smartphone Feedback Dataset

Total samples:

11,122 reviews
Aspects

The system predicts sentiment for 10 aspects:

Aspect	Description
SCREEN	Display quality
CAMERA	Camera performance
FEATURES	Product features
BATTERY	Battery life
PERFORMANCE	Processing performance
STORAGE	Storage capacity
DESIGN	Product design
PRICE	Price value
GENERAL	Overall satisfaction
SER&ACC	Service & Accessories
Sentiment Labels
Label	Meaning
0	Negative
1	Neutral
2	Positive
3	Not Mentioned
🤖 Model Development
1. Traditional Baselines

Models evaluated:

Logistic Regression
Linear SVM (LinearSVC)
TF-IDF Features

Performance measured using:

Accuracy
Macro Precision
Macro Recall
Macro F1-score
2. PhoBERT Single-Task Learning

Model:

vinai/phobert-base

Each aspect is trained independently.

Techniques:

Class weighting
Smart oversampling
Stratified splitting

Benefits:

Better understanding of Vietnamese review context
Significant improvement over traditional ML models
3. Multi-Task Learning (MTL)

A shared PhoBERT encoder is used with multiple classification heads.

Architecture:

PhoBERT Encoder
       │
 ┌─────┼─────┐
 ▼     ▼     ▼
SCREEN CAMERA ...
Heads for all aspects

Advantages:

Shared semantic understanding
Better generalization
Reduced training redundancy

Additional techniques:

Focal Loss
Aspect-specific loss weights
Smart Oversampling
4. Hybrid Fine-Tuning

The best-performing MTL encoder is reused as the foundation for individual aspect models.

Process:

MTL Encoder
      │
      ├── BATTERY Model
      ├── PRICE Model
      ├── DESIGN Model
      └── SER&ACC Model

This approach combines:

Global knowledge from Multi-Task Learning
Aspect specialization through fine-tuning
📈 Model Performance

Best validation Macro F1-scores:

Aspect	Macro F1
BATTERY	0.838
PRICE	0.814
CAMERA	0.810
FEATURES	0.776
PERFORMANCE	0.758
DESIGN	0.757
GENERAL	0.749
SER&ACC	0.647
SCREEN	0.609
STORAGE	0.564
⭐ Buy Score Calculation

Final recommendation score combines multiple factors:

Buy Score =
ABSA Score +
Rating Score +
Price Score +
Sales Score +
Review Confidence Score

Components:

ABSA Score

Measures customer sentiment toward product aspects.

Rating Score

Normalized product rating.

Price Score

Evaluates price competitiveness.

Sales Score

Measures market popularity.

Review Confidence Score

Reflects reliability based on review volume.

📊 Dashboard Features
Product Recommendation
Top recommended products
Buy Score ranking
Product comparison
Product Analytics
Rating analysis
Price distribution
Sales performance
Aspect Analysis
Sentiment breakdown
Aspect contribution analysis
Positive vs negative trends
Shop Comparison

Compare identical products across multiple Shopee stores.

AI Chat Assistant

Interactive product recommendation support.

🛠 Technologies Used
Machine Learning & NLP
PhoBERT
Transformers
PyTorch
Scikit-Learn
Data Processing
Pandas
NumPy
Visualization
Plotly
Streamlit
Development Tools
Git
GitHub
Jupyter Notebook
🚀 Future Improvements
Real-time Shopee review crawling
LLM-powered recommendation explanation
Product similarity search
Personalized recommendation system
Multi-category support beyond smartphones
👨‍💻 Author

[Your Name]

Bachelor of Information Technology

Interests:

Natural Language Processing
Machine Learning
Data Science
Recommendation Systems
