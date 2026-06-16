# Diagram Examples

## Data Platform / Lakehouse

```python
with Diagram("Data Platform", direction="LR", outformat="dot"):
    # Sources
    with Cluster("Data Sources"):
        with Cluster("On-Premises"):
            oracle = RDS("Oracle")
            sqlserver = RDS("SQL Server")
        with Cluster("Cloud"):
            s3_source = S3("External Data")
        with Cluster("Streaming"):
            kafka = Kinesis("Message Queue")
    
    # Ingestion
    with Cluster("Ingestion Layer"):
        batch = Glue("Batch ETL")
        cdc = DMS("CDC")
        stream = Kinesis("Streaming")
    
    # Storage - Medallion Architecture
    with Cluster("Data Lakehouse"):
        bronze = S3("Bronze\\nRaw")
        silver = S3("Silver\\nCleansed")
        gold = S3("Gold\\nBusiness")
    
    # Processing
    with Cluster("Processing"):
        spark = EMR("Databricks/Spark")
    
    # Analytics
    with Cluster("Analytics"):
        warehouse = Redshift("SQL Warehouse")
        ml = Sagemaker("ML Platform")
        bi = User("BI Users")
    
    # Connections
    oracle >> cdc >> bronze
    sqlserver >> batch >> bronze
    s3_source >> batch
    kafka >> stream >> bronze
    
    bronze >> spark >> silver >> spark >> gold
    gold >> warehouse >> bi
    gold >> ml
```

## Multi-Environment AWS

```python
with Diagram("Multi-Environment", direction="TB", outformat="dot"):
    # Management
    with Cluster("AWS Organizations"):
        org = Organizations("AWS Org")
        sso = IAM("IAM Identity Center")
    
    # Shared Services
    with Cluster("Shared Services"):
        with Cluster("CI/CD"):
            git = Codecommit("Git")
            pipeline = Codepipeline("Pipeline")
            build = Codebuild("Build")
        monitoring = Cloudwatch("Central Monitoring")
        tf = S3("Terraform State")
    
    # Environments
    with Cluster("DEV"):
        dev_compute = EMR("Dev Cluster")
        dev_storage = S3("Dev Lake")
    
    with Cluster("UAT"):
        uat_compute = EMR("UAT Cluster")
        uat_storage = S3("UAT Lake")
    
    with Cluster("PROD"):
        prod_compute = EMR("Prod Cluster")
        prod_storage = S3("Prod Lake")
        backup = S3("DR Backup")
    
    # Network
    with Cluster("Network"):
        dx = DirectConnect("Direct Connect")
        tgw = TransitGateway("Transit Gateway")
    
    # Connections
    org >> sso
    git >> pipeline >> build
    
    pipeline >> Edge(label="Deploy") >> dev_compute
    pipeline >> Edge(label="Promote") >> uat_compute
    pipeline >> Edge(label="Release") >> prod_compute
    
    sso >> dev_compute
    sso >> uat_compute
    sso >> prod_compute
    
    dx >> tgw
    tgw >> dev_storage
    tgw >> uat_storage
    tgw >> prod_storage
    
    prod_storage >> backup
```

## Microservices Architecture

```python
with Diagram("Microservices", direction="LR", outformat="dot"):
    # Client
    client = Client("Mobile/Web")
    
    # API Layer
    with Cluster("API Gateway"):
        apigw = APIGateway("API Gateway")
        auth = Lambda("Auth")
    
    # Services
    with Cluster("Services"):
        with Cluster("User Service"):
            user_api = ECS("User API")
            user_db = RDS("User DB")
        
        with Cluster("Order Service"):
            order_api = ECS("Order API")
            order_db = RDS("Order DB")
        
        with Cluster("Payment Service"):
            payment_api = Lambda("Payment")
            payment_q = SQS("Payment Queue")
    
    # Events
    with Cluster("Event Bus"):
        events = SNS("Event Bus")
    
    # Connections
    client >> apigw >> auth
    auth >> user_api >> user_db
    auth >> order_api >> order_db
    order_api >> payment_q >> payment_api
    
    user_api >> events
    order_api >> events
    payment_api >> events
```

## ML/MLOps Platform

```python
with Diagram("MLOps Platform", direction="LR", outformat="dot"):
    # Data
    with Cluster("Data Sources"):
        lake = S3("Data Lake")
        features = S3("Feature Store")
    
    # Development
    with Cluster("Development"):
        notebooks = Sagemaker("Notebooks")
        experiments = Sagemaker("Experiments")
    
    # Training
    with Cluster("Training"):
        training = Sagemaker("Training Jobs")
        gpu = EC2("GPU Instances")
    
    # Registry
    with Cluster("Model Registry"):
        registry = Sagemaker("Model Registry")
        artifacts = S3("Model Artifacts")
    
    # Deployment
    with Cluster("Serving"):
        endpoint = Sagemaker("Endpoints")
        batch = Lambda("Batch Inference")
    
    # Monitoring
    with Cluster("Monitoring"):
        monitor = Cloudwatch("Model Monitor")
        alerts = SNS("Alerts")
    
    # Connections
    lake >> features >> notebooks >> experiments
    experiments >> training >> gpu
    training >> registry >> artifacts
    registry >> endpoint
    registry >> batch
    endpoint >> monitor >> alerts
```

## Serverless Architecture

```python
with Diagram("Serverless", direction="LR", outformat="dot"):
    # Frontend
    with Cluster("Frontend"):
        cdn = S3("CloudFront + S3")
        client = Client("Users")
    
    # API
    with Cluster("API"):
        api = APIGateway("API Gateway")
        auth = Lambda("Authorizer")
    
    # Functions
    with Cluster("Lambda Functions"):
        create = Lambda("Create")
        read = Lambda("Read")
        update = Lambda("Update")
        delete = Lambda("Delete")
    
    # Data
    with Cluster("Data"):
        dynamo = Dynamodb("DynamoDB")
        s3 = S3("S3 Storage")
    
    # Events
    with Cluster("Events"):
        sqs = SQS("Queue")
        sns = SNS("Notifications")
    
    # Connections
    client >> cdn
    client >> api >> auth
    api >> create >> dynamo
    api >> read >> dynamo
    api >> update >> dynamo
    api >> delete >> dynamo
    
    create >> s3
    create >> sqs >> sns
```

## Hybrid Cloud

```python
with Diagram("Hybrid Cloud", direction="TB", outformat="dot"):
    # On-Premises
    with Cluster("On-Premises Data Center"):
        with Cluster("Legacy Systems"):
            mainframe = RDS("Mainframe")
            erp = RDS("ERP")
        with Cluster("Local Infrastructure"):
            servers = EC2("App Servers")
            storage = S3("NAS/SAN")
    
    # Network
    with Cluster("Connectivity"):
        dx = DirectConnect("Direct Connect")
        vpn = VPC("VPN Backup")
    
    # AWS Cloud
    with Cluster("AWS Cloud"):
        with Cluster("Data Platform"):
            lake = S3("Data Lake")
            spark = EMR("Analytics")
        with Cluster("Applications"):
            apps = ECS("Modernized Apps")
            api = APIGateway("APIs")
    
    # Connections
    mainframe >> dx >> lake
    erp >> dx >> lake
    servers >> vpn >> apps
    lake >> spark >> api
    apps >> api
```