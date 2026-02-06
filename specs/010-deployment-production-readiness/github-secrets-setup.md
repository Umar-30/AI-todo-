# GitHub Actions Secrets Configuration

**Feature**: 010-deployment-production-readiness

## Required Secrets

Navigate to: **GitHub Repo → Settings → Secrets and variables → Actions**

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `KUBE_CONFIG` | Base64-encoded kubeconfig for cloud cluster | `cat ~/.kube/config \| base64` |
| `DATABASE_URL` | Neon PostgreSQL connection string | Neon dashboard → Connection Details |
| `JWT_SECRET` | JWT signing secret (min 32 chars) | Generate: `openssl rand -hex 32` |
| `COHERE_API_KEY` | Cohere API key for Task Agent | Cohere dashboard → API Keys |
| `OPENAI_API_KEY` | OpenAI API key for Voice STT/TTS | OpenAI dashboard → API Keys |
| `SASL_USERNAME` | Redpanda Cloud SASL username | Redpanda Cloud → Security → Users |
| `SASL_PASSWORD` | Redpanda Cloud SASL password | Redpanda Cloud → Security → Users |

## Setup Steps

### 1. Get Kubeconfig (DOKS Example)
```bash
doctl kubernetes cluster kubeconfig show todo-chatbot | base64
```
Copy the output and save as `KUBE_CONFIG` secret.

### 2. Generate JWT Secret
```bash
openssl rand -hex 32
```

### 3. Add Each Secret
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Enter name and value
4. Click "Add secret"

## Verification

After adding all secrets, trigger the pipeline:
```bash
git push origin main
```

Check the Actions tab for successful execution.
