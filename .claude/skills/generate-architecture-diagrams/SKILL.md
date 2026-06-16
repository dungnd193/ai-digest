---
name: generate-architecture-diagrams
description: Generate professional cloud architecture diagrams from documents or descriptions using Python diagrams library. Creates PNG images and editable Draw.io files. Use when the user wants to create architecture diagrams, infrastructure diagrams, data flow diagrams, or visualize cloud architecture for AWS, Azure, GCP, or on-premises systems.
---

# Generate Architecture Diagrams

Create professional, editable architecture diagrams from documents or descriptions using Python diagrams library and graphviz2drawio.

## Quick Start

### 1. Setup Project (using uv)

```bash
cd <project-directory>
uv init 2>/dev/null || true
uv add diagrams drawpyo

# For Draw.io export (requires graphviz)
brew install graphviz  # macOS
CFLAGS="-I$(brew --prefix graphviz)/include" LDFLAGS="-L$(brew --prefix graphviz)/lib" uv add graphviz2drawio
```

### 2. Generate Diagrams

Create a Python file using the template in [scripts/diagram_template.py](scripts/diagram_template.py).

### 3. Run

```bash
uv run python <your-diagram-file>.py
```

## Output Formats

| Format | Extension | Editable | Use Case |
|--------|-----------|----------|----------|
| PNG | `.png` | No | Documentation, presentations |
| DOT | `.dot` | Yes | GraphViz source |
| Draw.io | `.drawio` | Yes | Edit in VS Code, diagrams.net |

## Diagram Types

### Cloud Architecture (AWS/Azure/GCP)

```python
from diagrams import Diagram, Cluster
from diagrams.aws.compute import EC2, Lambda
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB, APIGateway
from diagrams.aws.storage import S3
from diagrams.aws.analytics import Glue, Kinesis, Redshift, EMR
from diagrams.aws.ml import Sagemaker
from diagrams.aws.security import IAM, KMS
```

### Data Platform / Lakehouse

Common pattern for data platforms:

```python
with Diagram("Data Platform", direction="LR"):
    with Cluster("Sources"):
        sources = [RDS("DB1"), RDS("DB2")]
    
    with Cluster("Ingestion"):
        batch = Glue("Batch ETL")
        stream = Kinesis("Streaming")
    
    with Cluster("Storage - Lakehouse"):
        bronze = S3("Bronze")
        silver = S3("Silver")
        gold = S3("Gold")
    
    with Cluster("Analytics"):
        warehouse = Redshift("SQL Warehouse")
        ml = Sagemaker("ML Platform")
    
    sources >> batch >> bronze >> silver >> gold
    gold >> warehouse
    gold >> ml
```

### Multi-Environment Deployment

```python
with Diagram("Multi-Env Deployment", direction="TB"):
    with Cluster("DEV"):
        dev = [EMR("Dev Cluster"), S3("Dev Lake")]
    with Cluster("UAT"):
        uat = [EMR("UAT Cluster"), S3("UAT Lake")]
    with Cluster("PROD"):
        prod = [EMR("Prod Cluster"), S3("Prod Lake")]
```

## Convert to Draw.io

After generating DOT file, convert to Draw.io:

```python
import subprocess

def convert_to_drawio(dot_file: str, drawio_file: str):
    subprocess.run(["graphviz2drawio", dot_file, "-o", drawio_file])

# In your diagram code, use outformat="dot"
with Diagram("My Diagram", outformat="dot", filename="my_diagram"):
    # ... diagram code ...

# Then convert
convert_to_drawio("my_diagram.dot", "my_diagram.drawio")
```

## Best Practices

1. **Use Clusters** to group related components
2. **Direction**: `LR` for data flows, `TB` for hierarchies
3. **Naming**: Use clear, descriptive labels
4. **Colors**: Use `graph_attr={"bgcolor": "#color"}` for visual grouping
5. **Edges**: Use `Edge(label="", color="", style="")` for connections

## Available Icons

### AWS Icons (most common)

```python
# Compute
from diagrams.aws.compute import EC2, Lambda, ECS, EKS

# Database
from diagrams.aws.database import RDS, DMS, Dynamodb

# Storage
from diagrams.aws.storage import S3

# Analytics
from diagrams.aws.analytics import Glue, Kinesis, Redshift, EMR, Athena, LakeFormation

# Network
from diagrams.aws.network import VPC, APIGateway, DirectConnect, TransitGateway

# Security
from diagrams.aws.security import IAM, KMS, SecretsManager

# ML
from diagrams.aws.ml import Sagemaker

# Integration
from diagrams.aws.integration import StepFunctions, SQS, SNS

# DevTools
from diagrams.aws.devtools import Codecommit, Codepipeline, Codebuild

# Management
from diagrams.aws.management import Cloudwatch, Organizations, Cloudtrail

# General
from diagrams.aws.general import User, Client
```

### Other Providers

```python
# Azure
from diagrams.azure.compute import VM
from diagrams.azure.database import SQLDatabases

# GCP
from diagrams.gcp.compute import GCE
from diagrams.gcp.database import BigQuery

# On-Premises
from diagrams.onprem.database import PostgreSQL, MySQL
from diagrams.onprem.compute import Server
```

## Workflow for Documents

When creating diagrams from technical documents:

1. **Extract architecture info**: Read document for components, layers, flows
2. **Identify clusters**: Group by function (Sources, Processing, Storage, etc.)
3. **Map to icons**: Find appropriate AWS/Azure/GCP icons
4. **Define connections**: Show data flow with arrows
5. **Generate**: Create both PNG and Draw.io formats

## Reference

- Video Tutorial: https://www.youtube.com/watch?v=m7EuZ7GhinE
- Diagrams Docs: https://diagrams.mingrammer.com/
- Draw.io: https://app.diagrams.net/