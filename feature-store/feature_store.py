from datetime import timedelta
import pandas as pd
from feast import Entity, FeatureService, FeatureView, Field, FileSource, PushSource, RequestSource
from feast.infra.offline_stores.contrib.postgres_offline_store.postgres import PostgreSQLOfflineStoreConfig
from feast.infra.online_stores.redis import RedisOnlineStoreConfig
from feast.on_demand_feature_view import on_demand_feature_view
from feast.types import Float32, Int64, String

# Configuration des stores
offline_store = PostgreSQLOfflineStoreConfig(
    host="postgresql.storage.svc.cluster.local",
    port=5432,
    database="scoring_db",
    db_schema="feast",
    user="postgres",
    password="iaxVrMCI8y"
)

online_store = RedisOnlineStoreConfig(
    connection_string="redis-service.default.svc.cluster.local:6379"
)

# Définir les entités
customer = Entity(
    name="customer",
    join_keys=["customer_id"],
    description="Customer entity for credit scoring"
)

# Sources de données
customer_batch_source = FileSource(
    path="s3a://data-lake/scoring/customers/",
    timestamp_field="event_timestamp"
)

transaction_batch_source = FileSource(
    path="s3a://data-lake/scoring/transactions/",
    timestamp_field="event_timestamp"
)

# Feature Views pour les données clients
customer_features = FeatureView(
    name="customer_features",
    entities=[customer],
    ttl=timedelta(days=365),
    schema=[
        Field(name="age", dtype=Int64, description="Customer age"),
        Field(name="income", dtype=Float32, description="Annual income"),
        Field(name="employment_years", dtype=Int64, description="Years of employment"),
        Field(name="credit_history_length", dtype=Int64, description="Length of credit history in months"),
        Field(name="num_credit_lines", dtype=Int64, description="Number of credit lines"),
        Field(name="debt_ratio", dtype=Float32, description="Debt to income ratio"),
        Field(name="revolving_utilization", dtype=Float32, description="Revolving credit utilization"),
        Field(name="late_payment_ratio_6m", dtype=Float32, description="Late payment ratio in last 6 months"),
        Field(name="late_payment_ratio_12m", dtype=Float32, description="Late payment ratio in last 12 months"),
        Field(name="avg_transaction_amount_3m", dtype=Float32, description="Average transaction amount in last 3 months"),
        Field(name="transaction_count_3m", dtype=Int64, description="Number of transactions in last 3 months"),
        Field(name="transaction_count_6m", dtype=Int64, description="Number of transactions in last 6 months"),
        Field(name="high_risk_transaction_ratio", dtype=Float32, description="Ratio of high-risk transactions"),
        Field(name="geographic_risk_score", dtype=Float32, description="Geographic risk score"),
        Field(name="behavioral_score", dtype=Float32, description="Behavioral risk score"),
    ],
    online=True,
    source=customer_batch_source,
)

# Feature Views pour les transactions
transaction_features = FeatureView(
    name="transaction_features",
    entities=[customer],
    ttl=timedelta(days=90),
    schema=[
        Field(name="total_transaction_amount_7d", dtype=Float32, description="Total transaction amount in last 7 days"),
        Field(name="total_transaction_amount_30d", dtype=Float32, description="Total transaction amount in last 30 days"),
        Field(name="avg_daily_transactions_30d", dtype=Float32, description="Average daily transactions in last 30 days"),
        Field(name="max_transaction_amount_30d", dtype=Float32, description="Maximum transaction amount in last 30 days"),
        Field(name="transaction_frequency_score", dtype=Float32, description="Transaction frequency score"),
        Field(name="unusual_transaction_pattern", dtype=Int64, description="Flag for unusual transaction patterns"),
        Field(name="merchant_risk_score", dtype=Float32, description="Average merchant risk score"),
        Field(name="international_transaction_ratio", dtype=Float32, description="Ratio of international transactions"),
        Field(name="cash_withdrawal_ratio", dtype=Float32, description="Ratio of cash withdrawals"),
        Field(name="online_transaction_ratio", dtype=Float32, description="Ratio of online transactions"),
        Field(name="weekend_transaction_ratio", dtype=Float32, description="Ratio of weekend transactions"),
        Field(name="late_night_transaction_ratio", dtype=Float32, description="Ratio of late night transactions"),
    ],
    online=True,
    source=transaction_batch_source,
)

# Feature View pour les données temps réel (push source)
real_time_features = FeatureView(
    name="real_time_features",
    entities=[customer],
    ttl=timedelta(hours=24),
    schema=[
        Field(name="current_balance", dtype=Float32, description="Current account balance"),
        Field(name="last_transaction_amount", dtype=Float32, description="Last transaction amount"),
        Field(name="last_transaction_time", dtype=Int64, description="Last transaction timestamp"),
        Field(name="login_attempts_24h", dtype=Int64, description="Login attempts in last 24 hours"),
        Field(name="device_fingerprint_score", dtype=Float32, description="Device fingerprint risk score"),
        Field(name="ip_risk_score", dtype=Float32, description="IP address risk score"),
        Field(name="session_duration", dtype=Int64, description="Current session duration"),
    ],
    online=True,
    source=PushSource(name="real_time_push_source"),
)

# On-demand feature view pour les features calculées
@on_demand_feature_view(
    sources=[customer_features, transaction_features],
    schema=[
        Field(name="combined_risk_score", dtype=Float32, description="Combined risk score from multiple features"),
        Field(name="creditworthiness_index", dtype=Float32, description="Overall creditworthiness index"),
        Field(name="fraud_probability", dtype=Float32, description="Probability of fraudulent activity"),
    ],
)
def credit_scoring_features(customer_features, transaction_features):
    # Calcul du score de risque combiné
    combined_risk = (
        customer_features["debt_ratio"] * 0.3 +
        customer_features["revolving_utilization"] * 0.25 +
        customer_features["late_payment_ratio_12m"] * 0.25 +
        transaction_features["unusual_transaction_pattern"] * 0.2
    )

    # Indice de solvabilité
    creditworthiness = (
        (1 - customer_features["debt_ratio"]) * 0.4 +
        (customer_features["employment_years"] / 50.0) * 0.3 +
        (customer_features["credit_history_length"] / 120.0) * 0.3
    )

    # Probabilité de fraude
    fraud_probability = (
        transaction_features["unusual_transaction_pattern"] * 0.4 +
        customer_features["high_risk_transaction_ratio"] * 0.3 +
        transaction_features["international_transaction_ratio"] * 0.3
    )

    return pd.DataFrame({
        "combined_risk_score": combined_risk,
        "creditworthiness_index": creditworthiness,
        "fraud_probability": fraud_probability
    })

# Feature Service pour l'API de scoring
credit_scoring_service = FeatureService(
    name="credit_scoring_service",
    features=[
        customer_features[["age", "income", "employment_years", "credit_history_length", "num_credit_lines", "debt_ratio", "revolving_utilization"]],
        transaction_features[["total_transaction_amount_30d", "avg_daily_transactions_30d", "transaction_frequency_score", "unusual_transaction_pattern"]],
        real_time_features[["current_balance", "login_attempts_24h", "device_fingerprint_score"]],
        credit_scoring_features
    ],
    description="Feature service for credit scoring model"
)

# Feature Service pour la détection de fraude
fraud_detection_service = FeatureService(
    name="fraud_detection_service",
    features=[
        transaction_features[["max_transaction_amount_30d", "unusual_transaction_pattern", "merchant_risk_score", "international_transaction_ratio"]],
        real_time_features[["last_transaction_amount", "ip_risk_score", "device_fingerprint_score"]],
        credit_scoring_features[["fraud_probability"]]
    ],
    description="Feature service for fraud detection"
)

# Feature Service pour les dashboards business
business_analytics_service = FeatureService(
    name="business_analytics_service",
    features=[
        customer_features[["age", "income", "geographic_risk_score"]],
        transaction_features[["total_transaction_amount_30d", "transaction_count_6m", "online_transaction_ratio"]],
        credit_scoring_features[["creditworthiness_index"]]
    ],
    description="Feature service for business analytics and reporting"
)