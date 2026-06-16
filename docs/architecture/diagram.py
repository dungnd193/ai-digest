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
    trigger = Users("daily.sh\n(you, each morning)")
    operator = Client("You\n(Telegram)")

    with Cluster("Sources"):
        rss = Server("RSS feeds")
        tavily = Server("Tavily\n(web search)")

    with Cluster("Ingestion"):
        collector = Python("Collector")
        discovery = Python("Discovery")
        ingestor = Python("Ingestor\n(dedupe vs seen)")
        rss >> collector
        tavily >> discovery
        [collector, discovery] >> ingestor

    with Cluster("Model Router  (model_mode: both | claude_only | ollama_only)"):
        router = Python("Router\n(cheap / smart)")
        gemma = Server("Gemma\n(Ollama, local)")
        claude = Server("Claude\n(claude -p)")
        router >> Edge(label="cheap") >> gemma
        router >> Edge(label="smart") >> claude

    with Cluster("Per-story pipeline  (timed per step)"):
        processor = Python("Processor")
        clusterer = Python("Clusterer")
        analyst = Python("Lead Analyst")
        writer = Python("Writer (EN)")
        translator = Python("Translator (VI)")
        qgate = Python("Quality Gate")

    with Cluster("State"):
        seen = Storage("seen.json")
        posts = Storage("posts.json")
        runlog = Storage("runs/*.log\n(timings)")

    with Cluster("Publishing"):
        publisher = Python("Publisher")
        git = Git("git repo\n(mono-repo)")
        gha = Github("GitHub Actions\n→ Pages (Hugo)")
        publisher >> git >> gha

    reporter = Python("Reporter\n(daily report:\nper-post timings)")

    # main flow
    trigger >> ingestor
    ingestor >> processor >> clusterer >> analyst
    analyst >> writer >> translator >> qgate

    # router used by processing + content agents
    [processor, clusterer] >> Edge(style="dotted") >> router
    [analyst, writer, translator, qgate] >> Edge(style="dotted") >> router

    # state
    ingestor >> Edge(style="dashed", label="filter") >> seen
    qgate >> Edge(style="dashed") >> runlog

    # publish: auto-publish (default) OR optional Telegram approval
    qgate >> Edge(label="auto-publish\n(default)") >> publisher
    qgate >> Edge(style="dashed", label="if approval_required") >> reporter
    reporter >> operator
    operator >> Edge(label="✅/✏️/❌") >> publisher
    publisher >> posts
    reporter >> Edge(style="dotted", label="summary") >> operator
