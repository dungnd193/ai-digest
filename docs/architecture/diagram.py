"""Generate the AI Digest architecture diagram (PNG + DOT).

Run:  uv run python docs/architecture/diagram.py
Outputs (in this directory): ai-digest-architecture.png and .dot
"""
from __future__ import annotations

from diagrams import Cluster, Diagram, Edge
from diagrams.generic.storage import Storage
from diagrams.onprem.client import Client, Users
from diagrams.onprem.compute import Server
from diagrams.onprem.vcs import Git, Github
from diagrams.programming.language import Python

GRAPH_ATTR = {"fontsize": "16", "bgcolor": "white", "splines": "spline"}

with Diagram(
    "AI Digest — Architecture",
    filename="docs/architecture/ai-digest-architecture",
    outformat=["png", "dot"],
    show=False,
    direction="LR",
    graph_attr=GRAPH_ATTR,
):
    cron = Users("cron\n(daily)")
    operator = Client("You\n(Telegram)")

    with Cluster("Sources"):
        rss = Server("RSS feeds")
        tavily = Server("Tavily\n(web search)")

    with Cluster("Ingestion"):
        collector = Python("Collector")
        discovery = Python("Discovery")
        ingestor = Python("Ingestor")
        rss >> collector
        tavily >> discovery
        [collector, discovery] >> ingestor

    with Cluster("Model Router"):
        router = Python("Router\n(cheap / smart)")
        gemma = Server("Gemma\n(Ollama, local)")
        claude = Server("Claude\n(claude -p)")
        router >> Edge(label="cheap") >> gemma
        router >> Edge(label="smart") >> claude

    with Cluster("Processing  (cheap → Gemma)"):
        processor = Python("Processor")
        clusterer = Python("Clusterer")

    with Cluster("Analysis & Content  (smart → Claude)"):
        analyst = Python("Lead Analyst")
        writer = Python("Writer (EN)")
        translator = Python("Translator (VI)")
        qgate = Python("Quality Gate")

    with Cluster("State"):
        seen = Storage("seen.json")
        posts = Storage("posts.json")

    with Cluster("Publishing"):
        publisher = Python("Publisher")
        git = Git("git repo\n(mono-repo)")
        gha = Github("GitHub Actions\n→ Pages (Hugo)")
        publisher >> git >> gha

    with Cluster("Notify / Approval"):
        reporter = Python("Reporter")
        approver = Python("Approver\n(long-poll)")

    # main pipeline flow
    cron >> ingestor
    ingestor >> processor >> clusterer >> analyst
    analyst >> writer >> translator >> qgate >> publisher

    # router used by processing + content agents
    [processor, clusterer] >> Edge(style="dotted") >> router
    [analyst, writer, translator, qgate] >> Edge(style="dotted") >> router

    # idempotency + lifecycle state
    ingestor >> Edge(style="dashed", label="filter") >> seen
    publisher >> Edge(style="dashed") >> posts

    # human-in-the-loop approval
    publisher >> Edge(label="drafts") >> reporter >> operator
    operator >> Edge(label="✅/✏️/❌") >> approver
    approver >> Edge(label="publish") >> git
    approver >> posts
