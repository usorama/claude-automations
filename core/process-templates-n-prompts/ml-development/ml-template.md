# ML Development Templates

## 1. Model Card Template

```markdown
# Model Card: [Model Name]

## Model Details
- **Version**: 1.0.0
- **Date**: YYYY-MM-DD
- **Type**: [Classification/Regression/Clustering/etc.]
- **Architecture**: [Algorithm details]
- **Training Framework**: [TensorFlow/PyTorch/Scikit-learn/etc.]
- **License**: [MIT/Apache/Proprietary/etc.]

## Intended Use
- **Primary Use Case**: [Describe primary application]
- **Users**: [Who will use this model]
- **Out of Scope**: [What the model should NOT be used for]

## Training Data
- **Dataset**: [Name and version]
- **Size**: [Number of samples]
- **Date Range**: [If temporal]
- **Features**: [Number and types]
- **Label Distribution**: [Class balance or target distribution]
- **Data Processing**: [Preprocessing steps applied]

## Evaluation Data
- **Test Set Size**: [Number of samples]
- **Evaluation Metrics**: [List metrics used]
- **Performance Results**:
  - Accuracy: X%
  - Precision: X%
  - Recall: X%
  - F1-Score: X
  - [Other metrics]

## Ethical Considerations
- **Potential Biases**: [Known biases in data or model]
- **Fairness Metrics**: [Results of fairness testing]
- **Privacy**: [PII handling, anonymization]
- **Environmental Impact**: [Training compute resources]

## Limitations
- [List known limitations]
- [Edge cases not handled well]
- [Data requirements]
- [Performance constraints]

## References
- [Papers, documentation, links]
```

## 2. Experiment Tracking Template

```yaml
# experiment_config.yaml
experiment:
  name: "baseline_model_v1"
  description: "Initial baseline model for customer churn prediction"
  author: "ML Team"
  date: "2024-01-21"
  tags: ["baseline", "churn", "classification"]

data:
  source: "s3://ml-data/churn/v1.0"
  version: "1.0"
  train_samples: 100000
  validation_samples: 20000
  test_samples: 20000
  features: 50
  preprocessing:
    - missing_value_imputation: "median"
    - scaling: "standard"
    - encoding: "one-hot"

model:
  algorithm: "XGBoost"
  hyperparameters:
    n_estimators: 100
    max_depth: 6
    learning_rate: 0.1
    subsample: 0.8
    colsample_bytree: 0.8
  random_seed: 42

training:
  epochs: 100
  early_stopping: true
  patience: 10
  validation_metric: "auc"
  cross_validation: 5

results:
  validation:
    accuracy: 0.875
    precision: 0.823
    recall: 0.791
    f1_score: 0.807
    auc_roc: 0.913
  test:
    accuracy: 0.869
    precision: 0.818
    recall: 0.785
    f1_score: 0.801
    auc_roc: 0.908

artifacts:
  model_path: "s3://ml-models/churn/xgboost_v1.pkl"
  feature_importance: "s3://ml-models/churn/features_v1.json"
  evaluation_plots: "s3://ml-models/churn/plots/"
```

## 3. Feature Engineering Pipeline Template

```python
# feature_pipeline.py
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer

class FeatureEngineeringPipeline:
    """
    Reusable feature engineering pipeline for ML projects
    """
    
    def __init__(self, numeric_features, categorical_features):
        self.numeric_features = numeric_features
        self.categorical_features = categorical_features
        self.pipeline = None
        
    def create_pipeline(self):
        # Numeric pipeline
        numeric_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        # Categorical pipeline
        categorical_pipeline = Pipeline([
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('encoder', OneHotEncoder(handle_unknown='ignore'))
        ])
        
        # Combine pipelines
        self.pipeline = ColumnTransformer([
            ('numeric', numeric_pipeline, self.numeric_features),
            ('categorical', categorical_pipeline, self.categorical_features)
        ])
        
        return self.pipeline
    
    def fit_transform(self, X, y=None):
        return self.pipeline.fit_transform(X, y)
    
    def transform(self, X):
        return self.pipeline.transform(X)
    
    def save_pipeline(self, filepath):
        import joblib
        joblib.dump(self.pipeline, filepath)
    
    def load_pipeline(self, filepath):
        import joblib
        self.pipeline = joblib.load(filepath)
        return self.pipeline

# Usage example
numeric_features = ['age', 'income', 'credit_score']
categorical_features = ['gender', 'region', 'product_type']

pipeline = FeatureEngineeringPipeline(numeric_features, categorical_features)
preprocessor = pipeline.create_pipeline()
```

## 4. Model Training Script Template

```python
# train_model.py
import mlflow
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import logging

class ModelTrainer:
    """
    Standard model training template with MLflow tracking
    """
    
    def __init__(self, experiment_name):
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def load_data(self, data_path):
        """Load and split data"""
        self.logger.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        X = df.drop('target', axis=1)
        y = df['target']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        return X_train, X_test, y_train, y_test
    
    def train(self, model, X_train, y_train, X_test, y_test):
        """Train model with MLflow tracking"""
        with mlflow.start_run():
            # Log parameters
            mlflow.log_params(model.get_params())
            
            # Train model
            self.logger.info("Training model...")
            model.fit(X_train, y_train)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            mlflow.log_metric("cv_mean", cv_scores.mean())
            mlflow.log_metric("cv_std", cv_scores.std())
            
            # Evaluate on test set
            y_pred = model.predict(X_test)
            
            # Log metrics
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            mlflow.log_metric("accuracy", accuracy_score(y_test, y_pred))
            mlflow.log_metric("precision", precision_score(y_test, y_pred, average='weighted'))
            mlflow.log_metric("recall", recall_score(y_test, y_pred, average='weighted'))
            mlflow.log_metric("f1", f1_score(y_test, y_pred, average='weighted'))
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            # Log artifacts
            self.logger.info("Logging artifacts...")
            report = classification_report(y_test, y_pred)
            with open("classification_report.txt", "w") as f:
                f.write(report)
            mlflow.log_artifact("classification_report.txt")
            
            return model
    
    def register_model(self, run_id, model_name):
        """Register model in MLflow Model Registry"""
        client = mlflow.tracking.MlflowClient()
        model_uri = f"runs:/{run_id}/model"
        model_version = mlflow.register_model(model_uri, model_name)
        
        # Transition to staging
        client.transition_model_version_stage(
            name=model_name,
            version=model_version.version,
            stage="Staging"
        )
        
        return model_version

# Usage
if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    
    trainer = ModelTrainer("customer_churn_experiment")
    X_train, X_test, y_train, y_test = trainer.load_data("data/churn.csv")
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    trained_model = trainer.train(model, X_train, y_train, X_test, y_test)
```

## 5. Model Serving API Template

```python
# model_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import pandas as pd
import joblib
import logging
from typing import List, Dict

app = FastAPI(title="ML Model API", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model at startup
MODEL_PATH = "models/production_model.pkl"
PREPROCESSOR_PATH = "models/preprocessor.pkl"

try:
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    raise

# Request/Response schemas
class PredictionRequest(BaseModel):
    features: Dict[str, float]
    
class PredictionResponse(BaseModel):
    prediction: float
    probability: List[float]
    model_version: str

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    try:
        # Convert to DataFrame
        df = pd.DataFrame([request.features])
        
        # Preprocess
        X = preprocessor.transform(df)
        
        # Predict
        prediction = model.predict(X)[0]
        probability = model.predict_proba(X)[0].tolist()
        
        return PredictionResponse(
            prediction=float(prediction),
            probability=probability,
            model_version="1.0.0"
        )
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch prediction endpoint
@app.post("/predict_batch")
def predict_batch(requests: List[PredictionRequest]):
    try:
        # Convert to DataFrame
        df = pd.DataFrame([r.features for r in requests])
        
        # Preprocess
        X = preprocessor.transform(df)
        
        # Predict
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)
        
        results = []
        for pred, prob in zip(predictions, probabilities):
            results.append({
                "prediction": float(pred),
                "probability": prob.tolist()
            })
        
        return {"predictions": results}
        
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 6. Data Drift Monitoring Template

```python
# drift_monitor.py
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List
import logging

class DriftMonitor:
    """
    Monitor data drift between training and production data
    """
    
    def __init__(self, reference_data: pd.DataFrame):
        self.reference_data = reference_data
        self.numeric_columns = reference_data.select_dtypes(include=[np.number]).columns
        self.categorical_columns = reference_data.select_dtypes(include=['object']).columns
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def calculate_psi(self, expected, actual, bins=10):
        """Calculate Population Stability Index"""
        def psi_bucket(expected, actual):
            expected_prop = expected / expected.sum()
            actual_prop = actual / actual.sum()
            psi = (actual_prop - expected_prop) * np.log(actual_prop / expected_prop)
            return psi.sum()
        
        breakpoints = np.quantile(expected, np.linspace(0, 1, bins))
        expected_bins = pd.cut(expected, bins=breakpoints, include_lowest=True)
        actual_bins = pd.cut(actual, bins=breakpoints, include_lowest=True)
        
        expected_counts = expected_bins.value_counts()
        actual_counts = actual_bins.value_counts()
        
        return psi_bucket(expected_counts, actual_counts)
    
    def detect_drift(self, production_data: pd.DataFrame, threshold: float = 0.1) -> Dict:
        """
        Detect drift in production data
        Returns dict with drift metrics and alerts
        """
        results = {
            'numeric_drift': {},
            'categorical_drift': {},
            'alerts': []
        }
        
        # Check numeric features
        for col in self.numeric_columns:
            if col in production_data.columns:
                # Kolmogorov-Smirnov test
                ks_stat, p_value = stats.ks_2samp(
                    self.reference_data[col].dropna(),
                    production_data[col].dropna()
                )
                
                # PSI
                psi = self.calculate_psi(
                    self.reference_data[col].dropna(),
                    production_data[col].dropna()
                )
                
                results['numeric_drift'][col] = {
                    'ks_statistic': ks_stat,
                    'p_value': p_value,
                    'psi': psi
                }
                
                if psi > threshold:
                    results['alerts'].append(f"High PSI detected for {col}: {psi:.3f}")
        
        # Check categorical features
        for col in self.categorical_columns:
            if col in production_data.columns:
                # Chi-square test
                ref_counts = self.reference_data[col].value_counts()
                prod_counts = production_data[col].value_counts()
                
                # Align categories
                all_categories = set(ref_counts.index) | set(prod_counts.index)
                ref_aligned = pd.Series([ref_counts.get(cat, 0) for cat in all_categories])
                prod_aligned = pd.Series([prod_counts.get(cat, 0) for cat in all_categories])
                
                chi2_stat, p_value = stats.chi2_contingency([ref_aligned, prod_aligned])[:2]
                
                results['categorical_drift'][col] = {
                    'chi2_statistic': chi2_stat,
                    'p_value': p_value
                }
                
                if p_value < 0.05:
                    results['alerts'].append(f"Significant drift detected for {col} (p={p_value:.3f})")
        
        return results
    
    def generate_report(self, drift_results: Dict) -> str:
        """Generate drift monitoring report"""
        report = "=== Data Drift Monitoring Report ===\n\n"
        
        report += "Numeric Features:\n"
        for feature, metrics in drift_results['numeric_drift'].items():
            report += f"  {feature}:\n"
            report += f"    - KS Statistic: {metrics['ks_statistic']:.3f}\n"
            report += f"    - P-Value: {metrics['p_value']:.3f}\n"
            report += f"    - PSI: {metrics['psi']:.3f}\n"
        
        report += "\nCategorical Features:\n"
        for feature, metrics in drift_results['categorical_drift'].items():
            report += f"  {feature}:\n"
            report += f"    - Chi2 Statistic: {metrics['chi2_statistic']:.3f}\n"
            report += f"    - P-Value: {metrics['p_value']:.3f}\n"
        
        if drift_results['alerts']:
            report += "\n⚠️ ALERTS:\n"
            for alert in drift_results['alerts']:
                report += f"  - {alert}\n"
        
        return report

# Usage
if __name__ == "__main__":
    # Load reference data (training data)
    reference_data = pd.read_csv("data/training_data.csv")
    
    # Initialize monitor
    monitor = DriftMonitor(reference_data)
    
    # Load production data
    production_data = pd.read_csv("data/production_data.csv")
    
    # Detect drift
    drift_results = monitor.detect_drift(production_data)
    
    # Generate report
    report = monitor.generate_report(drift_results)
    print(report)
```

## 7. A/B Testing Template

```python
# ab_testing.py
import numpy as np
from scipy import stats
from typing import Tuple, Dict
import pandas as pd

class ABTestAnalyzer:
    """
    Analyze A/B test results for model comparison
    """
    
    def __init__(self, control_name="Control", treatment_name="Treatment"):
        self.control_name = control_name
        self.treatment_name = treatment_name
        
    def calculate_sample_size(self, 
                             baseline_rate: float,
                             minimum_detectable_effect: float,
                             alpha: float = 0.05,
                             power: float = 0.8) -> int:
        """
        Calculate required sample size for A/B test
        """
        from statsmodels.stats.power import NormalIndPower
        
        effect_size = minimum_detectable_effect / baseline_rate
        analysis = NormalIndPower()
        sample_size = analysis.solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            alternative='two-sided'
        )
        
        return int(np.ceil(sample_size))
    
    def analyze_test(self,
                     control_data: pd.Series,
                     treatment_data: pd.Series,
                     metric_type: str = "continuous") -> Dict:
        """
        Analyze A/B test results
        
        Args:
            control_data: Control group results
            treatment_data: Treatment group results
            metric_type: "continuous" or "binary"
        """
        results = {
            'control_mean': control_data.mean(),
            'treatment_mean': treatment_data.mean(),
            'control_std': control_data.std(),
            'treatment_std': treatment_data.std(),
            'control_n': len(control_data),
            'treatment_n': len(treatment_data)
        }
        
        if metric_type == "continuous":
            # T-test for continuous metrics
            t_stat, p_value = stats.ttest_ind(treatment_data, control_data)
            
            # Effect size (Cohen's d)
            pooled_std = np.sqrt(
                ((len(control_data) - 1) * control_data.std() ** 2 +
                 (len(treatment_data) - 1) * treatment_data.std() ** 2) /
                (len(control_data) + len(treatment_data) - 2)
            )
            effect_size = (treatment_data.mean() - control_data.mean()) / pooled_std
            
        elif metric_type == "binary":
            # Chi-square test for binary metrics
            control_success = control_data.sum()
            treatment_success = treatment_data.sum()
            
            contingency_table = np.array([
                [control_success, len(control_data) - control_success],
                [treatment_success, len(treatment_data) - treatment_success]
            ])
            
            chi2_stat, p_value, _, _ = stats.chi2_contingency(contingency_table)
            t_stat = chi2_stat
            
            # Risk ratio
            control_rate = control_success / len(control_data)
            treatment_rate = treatment_success / len(treatment_data)
            effect_size = treatment_rate / control_rate if control_rate > 0 else np.inf
            
        results.update({
            'test_statistic': t_stat,
            'p_value': p_value,
            'effect_size': effect_size,
            'relative_improvement': (results['treatment_mean'] - results['control_mean']) / results['control_mean'] * 100,
            'significant': p_value < 0.05
        })
        
        # Confidence interval
        if metric_type == "continuous":
            ci = stats.t.interval(
                0.95,
                len(treatment_data) + len(control_data) - 2,
                loc=treatment_data.mean() - control_data.mean(),
                scale=pooled_std * np.sqrt(1/len(treatment_data) + 1/len(control_data))
            )
        else:
            # Wilson score interval for proportions
            from statsmodels.stats.proportion import proportion_confint
            ci_control = proportion_confint(control_success, len(control_data))
            ci_treatment = proportion_confint(treatment_success, len(treatment_data))
            ci = (ci_treatment[0] - ci_control[1], ci_treatment[1] - ci_control[0])
        
        results['confidence_interval'] = ci
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Generate A/B test report"""
        report = f"""
=== A/B Test Results Report ===

Groups:
- {self.control_name}: n={results['control_n']}, mean={results['control_mean']:.4f} (std={results['control_std']:.4f})
- {self.treatment_name}: n={results['treatment_n']}, mean={results['treatment_mean']:.4f} (std={results['treatment_std']:.4f})

Statistical Test:
- Test Statistic: {results['test_statistic']:.4f}
- P-Value: {results['p_value']:.4f}
- Effect Size: {results['effect_size']:.4f}
- 95% Confidence Interval: ({results['confidence_interval'][0]:.4f}, {results['confidence_interval'][1]:.4f})

Business Impact:
- Relative Improvement: {results['relative_improvement']:.2f}%
- Statistical Significance: {"✅ Yes" if results['significant'] else "❌ No"}

Recommendation:
{"🎯 Treatment shows significant improvement. Consider rolling out." if results['significant'] and results['relative_improvement'] > 0 else
 "⚠️ No significant improvement detected. Continue monitoring or try different approach."}
        """
        return report

# Usage
if __name__ == "__main__":
    analyzer = ABTestAnalyzer("Model A", "Model B")
    
    # Calculate required sample size
    sample_size = analyzer.calculate_sample_size(
        baseline_rate=0.1,  # 10% conversion rate
        minimum_detectable_effect=0.02,  # 2% absolute improvement
        alpha=0.05,
        power=0.8
    )
    print(f"Required sample size per group: {sample_size}")
    
    # Analyze results
    control_results = pd.Series(np.random.binomial(1, 0.10, 1000))  # 10% conversion
    treatment_results = pd.Series(np.random.binomial(1, 0.12, 1000))  # 12% conversion
    
    results = analyzer.analyze_test(control_results, treatment_results, "binary")
    print(analyzer.generate_report(results))
```

## 8. Model Deployment Dockerfile Template

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY models/ ./models/
COPY config/ ./config/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MODEL_PATH=/app/models/production_model.pkl
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Run application
CMD ["python", "-m", "uvicorn", "src.model_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 9. Model Monitoring Dashboard Config

```yaml
# monitoring_config.yaml
dashboards:
  - name: "ML Model Performance"
    refresh_interval: 60s
    panels:
      - title: "Prediction Volume"
        type: "timeseries"
        metric: "predictions_total"
        aggregation: "rate"
        
      - title: "Prediction Latency"
        type: "histogram"
        metric: "prediction_duration_seconds"
        percentiles: [0.5, 0.95, 0.99]
        
      - title: "Model Accuracy"
        type: "gauge"
        metric: "model_accuracy"
        thresholds:
          - value: 0.95
            color: "green"
          - value: 0.90
            color: "yellow"
          - value: 0
            color: "red"
            
      - title: "Data Drift Score"
        type: "timeseries"
        metric: "data_drift_score"
        alert_threshold: 0.1
        
      - title: "Error Rate"
        type: "timeseries"
        metric: "prediction_errors_total"
        aggregation: "rate"

alerts:
  - name: "High Error Rate"
    condition: "rate(prediction_errors_total[5m]) > 0.01"
    severity: "critical"
    notification_channel: "slack"
    
  - name: "Data Drift Detected"
    condition: "data_drift_score > 0.15"
    severity: "warning"
    notification_channel: "email"
    
  - name: "Model Performance Degradation"
    condition: "model_accuracy < 0.85"
    severity: "critical"
    notification_channel: ["slack", "pagerduty"]
    
  - name: "High Prediction Latency"
    condition: "histogram_quantile(0.95, prediction_duration_seconds) > 1.0"
    severity: "warning"
    notification_channel: "slack"
```

## 10. Retraining Pipeline Configuration

```yaml
# retraining_config.yaml
pipeline:
  name: "model_retraining_pipeline"
  schedule: "0 2 * * *"  # Daily at 2 AM
  
  triggers:
    - type: "performance"
      condition: "accuracy < 0.85"
      
    - type: "drift"
      condition: "psi > 0.2"
      
    - type: "data_volume"
      condition: "new_samples > 10000"
      
    - type: "time"
      condition: "days_since_last_training > 30"

  stages:
    - name: "data_collection"
      tasks:
        - collect_production_data
        - validate_data_quality
        - merge_with_training_data
        
    - name: "data_preparation"
      tasks:
        - feature_engineering
        - data_splitting
        - data_validation
        
    - name: "model_training"
      tasks:
        - hyperparameter_tuning
        - model_training
        - cross_validation
        
    - name: "model_evaluation"
      tasks:
        - performance_evaluation
        - bias_testing
        - business_metrics_validation
        
    - name: "deployment_decision"
      tasks:
        - compare_with_production
        - stakeholder_approval
        - deployment_planning
        
    - name: "deployment"
      tasks:
        - canary_deployment
        - monitoring_setup
        - gradual_rollout

  notifications:
    on_start: ["email"]
    on_success: ["slack"]
    on_failure: ["slack", "pagerduty"]
    
  rollback:
    enabled: true
    condition: "error_rate > 0.05"
    automatic: true
```