# Deploying the DOMI Obstruction MCP Server as a Public Service

This guide explains how to expose the MCP server over the internet so clients (e.g. Cursor, Claude Desktop, or other MCP clients) can connect via a public URL. Use the **streaming HTTP** image (`Dockerfile_HTTP`); the server will listen on a port and clients connect to `/mcp`.

---

## Option 1: AWS App Runner (recommended)

App Runner runs your container, assigns a public URL, and handles scaling and HTTPS. No cluster or load balancer setup.

### Prerequisites

- AWS account and AWS CLI configured (or AWS SSO — see below)
- Docker installed
- Repository in the **server** directory with `Dockerfile_HTTP`, `main.py`, `wprdc.py`, `pyproject.toml`

### Using AWS SSO (recommended)

With SSO, account and region come from your profile; you don’t need to set them manually.

1. **Configure an SSO profile** (one-time):

   ```powershell
   aws configure sso
   ```

   When prompted, set:

   - **SSO session name** (e.g. `my-sso`)
   - **SSO start URL** (e.g. `https://my-org.awsapps.com/start`)
   - **SSO region** (e.g. `us-east-1`)
   - **SSO registration scopes** (default `sso:account:access` is fine)
   - Then choose the **account** and **role** to use, and the **default region** for the profile.

2. **Log in before deploying:**

   ```powershell
   aws sso login --profile YOUR_PROFILE_NAME
   ```

   Use the same profile name you set in step 1 (e.g. the one in `~/.aws/config` under `[profile ...]`).

3. **Use the profile** in all AWS CLI commands below by adding `--profile YOUR_PROFILE_NAME`, or set once:

   ```powershell
   $env:AWS_PROFILE = "YOUR_PROFILE_NAME"
   ```

### Step 1: Build and push the image to Amazon ECR

From the **server** directory:

**With AWS SSO** (account and region from your profile):

```powershell
# Use your SSO profile (or set $env:AWS_PROFILE = "YOUR_PROFILE_NAME")
$AWS_PROFILE = "YOUR_PROFILE_NAME"   # e.g. "my-sso-profile"
$ECR_REPO = "domi-obstruction-mcp"

# Get account ID and region from the profile (no manual values)
$AWS_ACCOUNT_ID = aws sts get-caller-identity --profile $AWS_PROFILE --query Account --output text
$AWS_REGION   = aws configure get region --profile $AWS_PROFILE
if (-not $AWS_REGION) { $AWS_REGION = "us-east-1" }

# Create ECR repository (one-time)
aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION --profile $AWS_PROFILE

# Log in to ECR
aws ecr get-login-password --region $AWS_REGION --profile $AWS_PROFILE | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# Build the streaming HTTP image (PowerShell: use "${ECR_REPO}:latest" so : is not parsed as scope)
docker build -f Dockerfile_HTTP -t "${ECR_REPO}:latest" .

# Tag for ECR
docker tag "${ECR_REPO}:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"

# Push
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"
```

**Without SSO** (manual account and region):

```powershell
$AWS_ACCOUNT_ID = "123456789012"
$AWS_REGION = "us-east-1"
$ECR_REPO = "domi-obstruction-mcp"

aws ecr create-repository --repository-name $ECR_REPO --region $AWS_REGION
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
docker build -f Dockerfile_HTTP -t "${ECR_REPO}:latest" .
docker tag "${ECR_REPO}:latest" "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"
docker push "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/${ECR_REPO}:latest"
```

Replace `123456789012` and `us-east-1` with your account ID and desired region. Use [AWS regions where App Runner is available](https://docs.aws.amazon.com/apprunner/latest/dg/how-app-runner-works.html#availability).

### Step 2: Create an IAM role for App Runner (ECR access)

App Runner needs permission to pull the image from ECR.

**If "App Runner" does not appear** in the trusted-entity list when you choose "AWS service", create the role with a **custom trust policy** instead:

1. In **IAM** → **Roles** → **Create role**.
2. Under **Trusted entity type**, select **Custom trust policy**.
3. In the **Policy editor**, replace the default JSON with:

   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Service": "apprunner.amazonaws.com"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   ```

4. Click **Next**.
5. Attach the managed policy **AmazonEC2ContainerRegistryReadOnly** (or **AWSAppRunnerServicePolicyForECRAccess** if available in your region). Alternatively use a custom policy that allows `ecr:GetDownloadUrlForLayer` and `ecr:BatchGetImage` on your repository.
6. Click **Next**, name the role (e.g. `AppRunnerECRAccessRole`), then **Create role**.
7. Note the role **ARN** (you will select this as the ECR access role in Step 3).

**If App Runner is listed:** use **AWS service** → **App Runner**, then attach the same managed policy, name the role, and note the ARN.

### Step 3: Create the App Runner service

**Console:**

1. Open [App Runner console](https://console.aws.amazon.com/apprunner) and select your region.
2. **Create service**.
3. **Source**: **Container registry** → **Amazon ECR**.
4. **Browse** and select your repository and image tag (e.g. `domi-obstruction-mcp:latest`).
5. **Deployment**: Manual or Automatic (Automatic requires ECR in the same account).
6. **ECR access role**: Select the role created in Step 2 → **Next**.
7. **Configure service**:
   - **Service name**: e.g. `domi-obstruction-mcp`.
   - **Port**: **8000** (the streaming HTTP server listens on 8000).
   - (Optional) **Environment variables**: e.g. `WPRDC_INGEST_MAX_RECORDS` = `5000` for faster startup.
8. **Next** → **Create and deploy**.

**CLI (optional):**

When using AWS SSO, add `--profile YOUR_PROFILE_NAME` to the command and set `ACCOUNT_ID` / `REGION` from your profile (e.g. `aws sts get-caller-identity --profile ...` and `aws configure get region --profile ...`).

```powershell
# Replace placeholders: ACCOUNT_ID, REGION, ECR_REPO, ECR_ACCESS_ROLE_ARN
# With SSO: use --profile YOUR_PROFILE_NAME and derive ACCOUNT_ID/REGION from the profile
aws apprunner create-service `
  --service-name domi-obstruction-mcp `
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/ECR_REPO:latest",
      "ImageRepositoryType": "ECR"
    },
    "AutoDeploymentsEnabled": false
  }' `
  --instance-configuration '{
    "Cpu": "1024",
    "Memory": "2048"
  }' `
  --health-check-configuration '{
    "Protocol": "HTTP",
    "Path": "/",
    "Interval": 10,
    "Timeout": 5,
    "HealthyThreshold": 1,
    "UnhealthyThreshold": 5
  }' `
  --region REGION
```

You must set the image configuration and ECR access role; the exact CLI for that varies (e.g. via `ImageRepository` and an access role ARN). The console is simpler for the first deployment.

### Step 4: Get the public URL

- In the App Runner **Service** dashboard, wait until **Status** is **Running**.
- Copy the **Default domain** (e.g. `xxxxx.us-east-1.awsapprunner.com`).

Your MCP streaming HTTP endpoint is:

- **`https://<default-domain>/mcp`**

Example client config (Cursor `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "domi-obstruction-mcp": {
      "url": "https://xxxxx.us-east-1.awsapprunner.com/mcp"
    }
  }
}
```

### Optional: Custom domain and HTTPS

- App Runner provides HTTPS on the default domain.
- For a custom domain: **Custom domains** in the service → add domain → add the CNAME target to your DNS.

### Optional: Limit startup data (recommended for App Runner)

To speed up cold starts and reduce memory, set in the service **Environment variables**:

- `WPRDC_INGEST_MAX_RECORDS` = `5000` (or another limit you prefer).

---

## Option 2: AWS ECS (Fargate) + Application Load Balancer

Use this if you need more control (VPC, multiple services, or specific networking).

1. **Push image to ECR** (same as App Runner Step 1).
2. **Create ECS cluster** (Fargate, same region).
3. **Task definition**: Fargate, 0.5 vCPU / 1 GB memory (or more if you ingest many records), image = your ECR URI, port **8000**, env `MCP_TRANSPORT=streamable-http`, `MCP_PORT=8000`. Optional: `WPRDC_INGEST_MAX_RECORDS=5000`.
4. **ALB**: Create Application Load Balancer (internet-facing), listener HTTPS (or HTTP for testing) forwarding to a target group (port 8000).
5. **ECS service**: Fargate, task definition above, desired count 1, target group = the ALB target group. Ensure security group allows ALB → container on 8000 and ALB allows 80/443 from internet.
6. **Public URL**: ALB DNS name (or attach a custom domain to the ALB).

MCP client URL: **`https://<alb-dns-or-domain>/mcp`**.

---

## Option 3: Pipedream

**What Pipedream offers:** Pipedream provides a **hosted MCP server** at `https://remote.mcp.pipedream.net` that exposes **Pipedream’s** tools (3,000+ APIs, 10,000+ tools) with OAuth and credential management. It is **not** a generic host for arbitrary MCP servers like this one.

**Your DOMI Obstruction MCP:**

- **Cannot be “deployed to Pipedream”** as a server. Pipedream does not run your custom MCP process.
- **You can:**
  1. **Deploy this MCP elsewhere** (e.g. AWS App Runner or ECS as above) and use the public `/mcp` URL in any MCP client (Cursor, Claude, etc.). No Pipedream account required for that.
  2. **Use Pipedream’s MCP** in addition: point your app at `https://remote.mcp.pipedream.net` for Pipedream tools, and separately point at your DOMI MCP URL for obstruction data.
  3. **Custom tools on Pipedream**: If you want DOMI data to be available *through* Pipedream’s MCP, you would implement a [Pipedream custom tool](https://pipedream.com/connect/components/custom-tools/) that calls the WPRDC API (or your deployed MCP). That runs inside Pipedream’s ecosystem; your standalone DOMI MCP server would still be hosted by you (e.g. on AWS).

**Summary:** To make the DOMI Obstruction MCP publicly available, deploy it on **AWS** (or another cloud). Use **Pipedream** when you want their hosted MCP and OAuth-backed tools alongside your own services.

---

## Quick reference: client URL

| Deployment        | MCP streaming HTTP URL format               |
|-------------------|---------------------------------------------|
| App Runner        | `https://<service-default-domain>/mcp`      |
| ECS + ALB         | `https://<alb-dns-or-domain>/mcp`           |
| Local Docker      | `http://localhost:8000/mcp`                 |

Ensure the server is built with **streaming HTTP** (`Dockerfile_HTTP`) and listens on the port you configure (default **8000**).
