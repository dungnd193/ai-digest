"""
Architecture Diagram Template
=============================
Template for generating professional architecture diagrams with Draw.io export.

Usage:
    1. Copy this file to your project
    2. Modify the diagram code
    3. Run: uv run python diagram_template.py

Requirements:
    uv add diagrams graphviz2drawio
    brew install graphviz
"""

import subprocess
import os
from pathlib import Path

# AWS Icons - Import what you need
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.analytics import Glue, Kinesis, Redshift, EMR, LakeFormation, Athena
from diagrams.aws.compute import EC2, Lambda, ECS, EKS
from diagrams.aws.database import RDS, DMS, Dynamodb
from diagrams.aws.integration import StepFunctions, SQS, SNS
from diagrams.aws.network import VPC, APIGateway, DirectConnect, TransitGateway, ELB
from diagrams.aws.management import Cloudwatch, Organizations, Cloudtrail
from diagrams.aws.security import IAM, SecretsManager, KMS
from diagrams.aws.storage import S3
from diagrams.aws.devtools import Codecommit, Codepipeline, Codebuild
from diagrams.aws.ml import Sagemaker
from diagrams.aws.general import User, Client

# Output directory
OUTPUT_DIR = Path(__file__).parent


def convert_dot_to_drawio(dot_file: str, drawio_file: str):
    """Convert DOT file to Draw.io format using graphviz2drawio"""
    try:
        result = subprocess.run(
            ["graphviz2drawio", dot_file, "-o", drawio_file],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  ✅ Converted to: {drawio_file}")
            return True
        else:
            print(f"  ❌ Error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("  ⚠️ graphviz2drawio not found. Skipping Draw.io export.")
        print("     Install with: uv add graphviz2drawio")
        return False


def generate_png_diagram():
    """Generate PNG format (static image)"""
    with Diagram(
        "My Architecture",
        show=False,
        direction="LR",  # LR = left-right, TB = top-bottom
        filename=str(OUTPUT_DIR / "architecture"),
        outformat="png",
        graph_attr={"fontsize": "20", "bgcolor": "white", "pad": "0.5"}
    ):
        # ========================================
        # Define your architecture here
        # ========================================
        
        with Cluster("Sources"):
            db1 = RDS("Database 1")
            db2 = RDS("Database 2")
        
        with Cluster("Processing"):
            etl = Glue("ETL Jobs")
            compute = EMR("Spark")
        
        with Cluster("Storage"):
            lake = S3("Data Lake")
        
        with Cluster("Analytics"):
            warehouse = Redshift("Warehouse")
            bi = User("BI Users")
        
        # Define connections
        db1 >> etl >> lake
        db2 >> etl
        lake >> compute >> warehouse >> bi

    print("✅ Generated: architecture.png")


def generate_drawio_diagram():
    """Generate Draw.io format (editable)"""
    dot_file = str(OUTPUT_DIR / "architecture_drawio")
    
    with Diagram(
        "My Architecture",
        show=False,
        direction="LR",
        filename=dot_file,
        outformat="dot",  # DOT format for conversion
        graph_attr={"fontsize": "20", "bgcolor": "white", "pad": "0.5", "splines": "ortho"}
    ):
        # ========================================
        # Same architecture as above
        # ========================================
        
        with Cluster("Sources"):
            db1 = RDS("Database 1")
            db2 = RDS("Database 2")
        
        with Cluster("Processing"):
            etl = Glue("ETL Jobs")
            compute = EMR("Spark")
        
        with Cluster("Storage"):
            lake = S3("Data Lake")
        
        with Cluster("Analytics"):
            warehouse = Redshift("Warehouse")
            bi = User("BI Users")
        
        # Define connections
        db1 >> etl >> lake
        db2 >> etl
        lake >> compute >> warehouse >> bi

    print("✅ Generated: architecture_drawio.dot")
    
    # Convert to Draw.io
    convert_dot_to_drawio(
        f"{dot_file}.dot",
        str(OUTPUT_DIR / "architecture.drawio")
    )


def main():
    """Generate all diagram formats"""
    print("=" * 50)
    print("Generating Architecture Diagrams")
    print("=" * 50)
    print()
    
    os.chdir(OUTPUT_DIR)
    
    print("📊 Generating PNG...")
    generate_png_diagram()
    print()
    
    print("📊 Generating Draw.io...")
    generate_drawio_diagram()
    print()
    
    print("=" * 50)
    print("Done!")
    print("=" * 50)
    print()
    print("Output files:")
    print("  - architecture.png (static image)")
    print("  - architecture.drawio (editable)")
    print()
    print("Open .drawio in:")
    print("  - VS Code with Draw.io extension")
    print("  - https://app.diagrams.net/")


if __name__ == "__main__":
    main()