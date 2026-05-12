#  Complete Run, Test & Deploy Guide

## Prerequisites
- Azure account (free tier works)
- Azure CLI installed → https://learn.microsoft.com/en-us/cli/azure/install-azure-cli
- Terraform installed → https://developer.hashicorp.com/terraform/install
- Docker Desktop installed → https://www.docker.com/products/docker-desktop
- Git installed

---

## STEP 1 — Run locally (test before deploying)

```bash
# Clone or unzip the project
cd jeddah-library-intelligence

# Install Python dependencies
pip install -r requirements.txt

# Run the ML pipeline (generates model_artifacts.pkl)
python jeddah_library_rentals_SOLUTION.py
# You should see: ✅ Pipeline complete. All outputs in ./outputs/
#Best model: Neural Network (R² = 0.9311 on GPU, 0.9091 on CPU)


# Launch the dashboard locally
streamlit run dashboard.py
# Opens at http://localhost:8501
```

**Test the dashboard:**
- Tab 1: Change branch, hour, temperature → click Predict → check staffing recommendation changes
- Tab 2: Verify all charts load (branch totals, season, hour, day of week)
- Tab 3: Verify model comparison table and feature importance chart load

---

## STEP 2 — Test with Docker locally

```bash
# Build the Docker image
docker build -t jeddah-library-intelligence .

# Run it
docker run -p 8501:8501 jeddah-library-intelligence

# Open http://localhost:8501
# If it works → you're ready to deploy to Azure
```

---

## STEP 3 — Provision Azure infrastructure with Terraform

```bash
# Login to Azure
az login

# Go to terraform folder
cd terraform

# Copy example vars file and edit it
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars — change acr_name and app_name to something unique
# Example: acr_name = "fahadalshehrilib" (no hyphens, max 50 chars)

# Initialize Terraform (downloads Azure provider)
terraform init

# Preview what will be created (safe — no changes yet)
terraform plan

# Create all resources on Azure
terraform apply
# Type "yes" when prompted
# Takes about 2-3 minutes
```

**After terraform apply completes, copy these outputs:**
```
acr_login_server    = "yourname.azurecr.io"
acr_admin_username  = "yourname"
acr_admin_password  = "..."  (run: terraform output -raw acr_admin_password)
app_service_url     = "https://your-app.azurewebsites.net"
app_service_name    = "your-app-name"
```

---

## STEP 4 — Push code to GitHub

```bash
# Go back to project root
cd ..

# Initialize git repo
git init
git add .
git commit -m "Initial commit — Jeddah Library Intelligence Platform"

# Create repo on GitHub: https://github.com/new
# Name it: jeddah-library-intelligence
# Keep it PUBLIC

# Push
git remote add origin https://github.com/FahadAlshehrii/jeddah-library-intelligence.git
git branch -M main
git push -u origin main
```

---

## STEP 5 — Add GitHub Secrets (for CI/CD)

Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these 5 secrets:

| Secret Name | Value (from terraform output) |
|---|---|
| `REGISTRY_LOGIN_SERVER` | value of `acr_login_server` |
| `REGISTRY_USERNAME` | value of `acr_admin_username` |
| `REGISTRY_PASSWORD` | run `terraform output -raw acr_admin_password` |
| `AZURE_APP_NAME` | value of `app_service_name` |
| `AZURE_PUBLISH_PROFILE` | see step below |

**To get AZURE_PUBLISH_PROFILE:**
```bash
az webapp deployment list-publishing-profiles \
  --name YOUR_APP_NAME \
  --resource-group jeddah-library-rg \
  --xml
```
Copy the entire XML output and paste it as the secret value.

---

## STEP 6 — Trigger deployment

```bash
# Make any small change (e.g. update README)
echo "# Jeddah Library Intelligence" >> README.md
git add .
git commit -m "Trigger CI/CD deployment"
git push
```

Go to GitHub → **Actions** tab → watch the pipeline run.

It will:
1. Run the ML pipeline
2. Build the Docker image
3. Push to Azure Container Registry
4. Deploy to Azure App Service

**After it completes (~5 min), open your live URL:**
```
https://your-app-name.azurewebsites.net
```

---

## STEP 7 — Open the Draw.io diagram

1. Go to https://app.diagrams.net
2. Click **Extras** → **Edit Diagram**
3. Delete everything in the box
4. Paste the contents of `architecture.drawio`
5. Click **OK**
6. Export as PNG: **File** → **Export as** → **PNG** → **Export**

This is the architecture diagram to include in your GitHub README and show to Abdulrahman.

---

## Troubleshooting

**App shows "Application Error" on Azure:**
```bash
az webapp log tail --name YOUR_APP_NAME --resource-group jeddah-library-rg
```

**Terraform error "name already taken":**
- Change `acr_name` and `app_name` in `terraform.tfvars` to something more unique
- Run `terraform apply` again

**Docker build fails on Mac M1/M2:**
```bash
docker build --platform linux/amd64 -t jeddah-library-intelligence .
```

**To destroy all Azure resources (avoid charges when done):**
```bash
cd terraform
terraform destroy
```
