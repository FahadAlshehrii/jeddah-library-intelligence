"""
Diagram as Code — Jeddah Library Intelligence Platform
Architecture diagram using Python diagrams library (no draw.io needed)
Run: python3 architecture_diagram.py
Output: architecture.png
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.azure.compute import AppServices, ContainerRegistries, VM
from diagrams.azure.devops import Pipelines, Repos, Artifacts
from diagrams.azure.storage import BlobStorage
from diagrams.azure.ml import MachineLearningServiceWorkspaces
from diagrams.onprem.vcs import Github
from diagrams.onprem.container import Docker
from diagrams.programming.language import Python
from diagrams.generic.storage import Storage
from diagrams.generic.device import Tablet

graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
    "fontname": "Helvetica",
    "label": "Jeddah Library Intelligence Platform\nEnd-to-End ML + Cloud Architecture | by Fahad Alshehri",
    "labelloc": "t",
    "fontcolor": "#2c3e50",
}

node_attr = {
    "fontsize": "13",
    "fontname": "Helvetica",
}

with Diagram(
    "",
    filename="architecture",
    outformat="png",
    show=False,
    graph_attr=graph_attr,
    node_attr=node_attr,
    direction="LR",
):

    # ── 1. DATA LAYER ────────────────────────────────────────────
    with Cluster("📄 Data Layer", graph_attr={"bgcolor": "#fef9e7", "style": "rounded"}):
        raw_csv   = Storage("Raw CSV\njeddah_library_rentals.csv\n6,609 rows | 17 cols")

    # ── 2. ML PIPELINE ───────────────────────────────────────────
    with Cluster("🔧 ML Pipeline  (jeddah_library_rentals_SOLUTION.py)",
                 graph_attr={"bgcolor": "#eafaf1", "style": "rounded"}):
        cleaning  = Python("Data Cleaning\nFix dates, nulls\nduplicates, negatives")
        eda       = Python("EDA\n8 visualizations\nPatterns & insights")
        feat_eng  = Python("Feature Engineering\nPeak hours, temp bins\nweekend flags")

        with Cluster("🤖 4 ML Models", graph_attr={"bgcolor": "#d5f5e3"}):
            lr  = MachineLearningServiceWorkspaces("Linear Regression\nR²=0.86")
            dt  = MachineLearningServiceWorkspaces("Decision Tree\nR²=0.86")
            rf  = MachineLearningServiceWorkspaces("Random Forest\nR²=0.92")
            nn  = MachineLearningServiceWorkspaces("Neural Network\nR²=0.93 ⭐")

        artifacts = Storage("model_artifacts.pkl\nBest model + scaler\n+ feature columns")

    # ── 3. DASHBOARD ─────────────────────────────────────────────
    with Cluster("📊 Streamlit Dashboard  (dashboard.py)",
                 graph_attr={"bgcolor": "#eaf2fb", "style": "rounded"}):
        tab1 = Python("Tab 1\nDemand Predictor\n+ Staffing Advisor")
        tab2 = Python("Tab 2\nBranch Analytics\n+ Business Insights")
        tab3 = Python("Tab 3\nModel Comparison\n+ Feature Importance")

    # ── 4. CONTAINERIZATION ──────────────────────────────────────
    with Cluster("🐳 Containerization", graph_attr={"bgcolor": "#f4ecf7", "style": "rounded"}):
        dockerfile = Docker("Dockerfile\nStreamlit app\nPort 8501")

    # ── 5. CI/CD ─────────────────────────────────────────────────
    with Cluster("🐙 GitHub", graph_attr={"bgcolor": "#f5f5f5", "style": "rounded"}):
        github_repo    = Github("GitHub Repo\nAll code + IaC\n+ workflows")
        github_actions = Pipelines("GitHub Actions\nCI/CD on git push\nBuild → Push → Deploy")

    # ── 6. TERRAFORM IaC ─────────────────────────────────────────
    with Cluster("🏗️ Terraform  (IaC)",
                 graph_attr={"bgcolor": "#f0e6ff", "style": "rounded"}):
        tf = Artifacts("main.tf + variables.tf\nProvisions all Azure\nresources automatically")

    # ── 7. AZURE CLOUD ────────────────────────────────────────────
    with Cluster("☁️ Microsoft Azure", graph_attr={"bgcolor": "#dbeafe", "style": "rounded"}):
        acr     = ContainerRegistries("Azure Container\nRegistry (ACR)\nStores Docker images")
        appplan = VM("App Service Plan\nLinux B1\nManaged hosting")
        webapp  = AppServices("Azure App Service\nyour-app.azurewebsites.net\nPort 8501 → Streamlit")

    # ── 8. END USER ───────────────────────────────────────────────
    user = Tablet("Library Manager\nAny browser\nNo setup needed")

    # ═══════════════════════════════════════════════════════
    # CONNECTIONS
    # ═══════════════════════════════════════════════════════

    # Data → Pipeline
    raw_csv >> Edge(label="load") >> cleaning
    cleaning >> eda >> feat_eng

    # Feature eng → models
    feat_eng >> Edge(label="train") >> [lr, dt, rf, nn]

    # Models → artifacts (NN is best)
    nn >> Edge(label="save best\nmodel", color="#27ae60", style="bold") >> artifacts
    [lr, dt, rf] >> Edge(style="dashed", color="#95a5a6") >> artifacts

    # Artifacts → Dashboard
    artifacts >> Edge(label="load") >> tab1
    artifacts >> tab2
    artifacts >> tab3

    # Dashboard → Docker
    [tab1, tab2, tab3] >> Edge(label="package") >> dockerfile

    # Docker → GitHub
    dockerfile >> Edge(label="git push") >> github_repo

    # Terraform provisions Azure
    tf >> Edge(label="provisions", style="dashed", color="#8e44ad") >> acr
    tf >> Edge(style="dashed", color="#8e44ad") >> appplan
    tf >> Edge(style="dashed", color="#8e44ad") >> webapp

    # GitHub Actions pipeline
    github_repo >> Edge(label="trigger") >> github_actions
    github_actions >> Edge(label="docker push") >> acr
    acr >> Edge(label="pull image") >> appplan
    appplan >> webapp

    # User hits live URL
    webapp >> Edge(label="HTTPS\nlive URL", color="#27ae60", style="bold") >> user

print("✅ Architecture diagram generated: architecture.png")
