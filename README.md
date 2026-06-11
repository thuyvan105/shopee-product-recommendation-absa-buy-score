# 🛒 Shopee Product Recommendation System using Aspect-Based Sentiment Analysis (ABSA)

## 📌 Overview

This project builds an intelligent product recommendation system for Shopee by combining:

- Aspect-Based Sentiment Analysis (ABSA)
- Product ratings
- Sales volume
- Price competitiveness
- Review confidence

Instead of recommending products based solely on ratings or sales, the system analyzes customer reviews to understand sentiment toward specific product aspects and generates a comprehensive **Buy Score**.

---

## 🎯 Objectives

Traditional e-commerce rankings often rely on:

- Average rating
- Number of sales
- Product popularity

However, these metrics may not fully reflect actual customer satisfaction.

This project aims to:

- Extract aspect-level sentiment from customer reviews
- Evaluate products more comprehensively
- Recommend the most worthwhile products
- Provide explainable recommendations

---

## 🏗️ System Architecture

```text
Customer Reviews
        │
        ▼
Aspect-Based Sentiment Analysis
       (PhoBERT)
        │
        ▼
Aspect Sentiment Scores
        │
        ├── Rating Score
        ├── Price Score
        ├── Sales Score
        └── Review Confidence Score
        │
        ▼
      Buy Score
        │
        ▼
Product Recommendation Dashboard
```

---

## 📊 Dataset

### ViSFD Dataset

Vietnamese Smartphone Feedback Dataset

- Total reviews: **11,122**
- Language: Vietnamese
- Domain: Smartphone reviews

### Aspects

The system predicts sentiment for 10 aspects:

| Aspect | Description |
|----------|------------|
| SCREEN | Display quality |
| CAMERA | Camera performance |
| FEATURES | Product features |
| BATTERY | Battery life |
| PERFORMANCE | Device performance |
| STORAGE | Storage capacity |
| DESIGN | Product design |
| PRICE | Price value |
| GENERAL | Overall satisfaction |
| SER&ACC | Service & Accessories |

### Sentiment Labels

| Label | Meaning |
|---------|----------|
| 0 | Negative |
| 1 | Neutral |
| 2 | Positive |
| 3 | Not Mentioned |

---

## 🤖 Model Development

### 1. Traditional Machine Learning Baselines

Models evaluated:

- TF-IDF + Logistic Regression
- TF-IDF + Linear SVM

Evaluation metrics:

- Accuracy
- Precision
- Recall
- Macro F1-score

---

### 2. PhoBERT Single-Task Learning

Model:

```text
vinai/phobert-base
```

Each aspect is trained independently.

Techniques applied:

- Class weighting
- Smart oversampling
- Stratified train/validation/test split

Benefits:

- Better understanding of Vietnamese context
- Significant improvement compared to traditional ML models

---

### 3. Multi-Task Learning (MTL)

A shared PhoBERT encoder is used with separate classification heads for all aspects.

Architecture:

```text
                 PhoBERT Encoder
                         │
 ┌────────┬────────┬─────┼─────┬────────┐
 ▼        ▼        ▼           ▼        ▼
SCREEN  CAMERA  BATTERY  ...  PRICE  GENERAL
 Head     Head     Head         Head    Head
```

Additional techniques:

- Focal Loss
- Aspect-specific loss weighting
- Smart Oversampling

Advantages:

- Shared semantic representation
- Improved generalization
- Reduced redundancy across tasks

---

### 4. Hybrid Fine-Tuning

The trained Multi-Task encoder is reused as the foundation for individual aspect models.

Workflow:

```text
Multi-Task Encoder
        │
        ├── BATTERY Fine-Tuning
        ├── PRICE Fine-Tuning
        ├── DESIGN Fine-Tuning
        └── SER&ACC Fine-Tuning
```

This combines:

- General knowledge learned from all aspects
- Specialized optimization for difficult aspects

---

## 📈 Model Performance

Best validation Macro F1-scores:

| Aspect | Macro F1 |
|----------|----------|
| BATTERY | 0.838 |
| PRICE | 0.814 |
| CAMERA | 0.810 |
| FEATURES | 0.776 |
| PERFORMANCE | 0.758 |
| DESIGN | 0.757 |
| GENERAL | 0.749 |
| SER&ACC | 0.647 |
| SCREEN | 0.609 |
| STORAGE | 0.564 |

---

## ⭐ Buy Score Calculation

The final recommendation score combines multiple signals:

```text
Buy Score =
ABSA Score +
Rating Score +
Price Score +
Sales Score +
Review Confidence Score
```

### Components

#### ABSA Score
Measures customer sentiment toward product aspects.

#### Rating Score
Normalized product rating score.

#### Price Score
Evaluates price competitiveness compared to similar products.

#### Sales Score
Measures product popularity based on sales volume.

#### Review Confidence Score
Reflects review reliability based on review quantity and consistency.

---

## 📊 Dashboard Features

### Product Recommendation

- Top recommended products
- Buy Score ranking
- Product comparison

### Product Analytics

- Rating distribution
- Price analysis
- Sales performance

### Aspect Analysis

- Sentiment breakdown by aspect
- Positive vs negative comparison
- Aspect contribution visualization

### Shop Comparison

Compare identical products across different Shopee stores.

### AI Assistant

Interactive recommendation and product analysis support.

---

## 🛠️ Technologies Used

### Machine Learning & NLP

- PhoBERT
- Transformers
- PyTorch
- Scikit-Learn

### Data Processing

- Pandas
- NumPy

### Data Visualization

- Plotly
- Streamlit

### Development Tools

- Git
- GitHub
- Jupyter Notebook

---

## 🚀 Future Improvements

- Real-time Shopee review crawling
- Personalized recommendation engine
- LLM-powered recommendation explanations
- Multi-category product support
- Automated model retraining pipeline

---

## 🎓 Academic Contribution

This project demonstrates practical applications of:

- Aspect-Based Sentiment Analysis (ABSA)
- Vietnamese NLP using PhoBERT
- Multi-Task Learning
- Hybrid Fine-Tuning
- Recommendation Systems
- Explainable AI

---

Interests:

- Natural Language Processing (NLP)
- Machine Learning
- Data Science
- Recommendation Systems
- Big Data Analytics
