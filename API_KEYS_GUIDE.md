# 🔑 API Keys Configuration Guide

This guide will help you obtain and configure all necessary API keys for the Jynco Video Foundry platform.

## Required API Keys

The platform requires 5 types of credentials:

1. **AWS Credentials** (S3 Storage) - Required
2. **Runway API Key** (AI Video Generation) - Required for Runway models
3. **Stability AI API Key** (AI Image/Video) - Required for Stability models
4. **Secret Key** (Application Security) - Required
5. **Database Password** (Optional - can use default)

---

## 1. AWS Credentials (S3 Storage)

### What it's for:
- Storing generated video segments
- Storing final composed videos
- User uploaded assets

### How to get it:

#### Option A: Create New IAM User (Recommended)

1. **Go to AWS Console**: https://console.aws.amazon.com/iam/
2. **Create IAM User**:
   - Click "Users" → "Add users"
   - Username: `jynco-video-foundry`
   - Access type: ✅ Programmatic access
   - Click "Next"

3. **Set Permissions**:
   - Attach policies directly
   - Select: `AmazonS3FullAccess` (or create custom policy below)
   - Click "Next" → "Create user"

4. **Save Credentials**:
   - **Access Key ID**: `AKIA...` (save this!)
   - **Secret Access Key**: `...` (save this - shown only once!)

5. **Create S3 Bucket**:
   - Go to: https://s3.console.aws.amazon.com/
   - Click "Create bucket"
   - Bucket name: `jynco-video-foundry-{your-name}` (must be globally unique)
   - Region: `us-east-1` (or your preferred region)
   - **Uncheck** "Block all public access" if you need public video URLs
   - Click "Create bucket"

#### Option B: Use Existing Credentials

If you already have AWS credentials with S3 access, you can use them.

#### Custom IAM Policy (More Secure)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

#### Cost Estimate:
- S3 storage: ~$0.023 per GB/month
- Data transfer: First 100GB free, then ~$0.09/GB
- Example: 100 videos (10GB total) = ~$0.23/month

### What to add to .env:
```env
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
S3_BUCKET=jynco-video-foundry-yourname
```

---

## 2. Runway API Key (AI Video Generation)

### What it's for:
- Generating video segments using Runway Gen-3 Alpha Turbo
- Text-to-video and image-to-video generation

### How to get it:

1. **Sign Up**: https://runwayml.com/
2. **Go to API Settings**:
   - Click profile icon → "Settings"
   - Navigate to "API" tab
   - Or direct link: https://app.runwayml.com/settings/api

3. **Create API Key**:
   - Click "Create API Key"
   - Name it: `Jynco Video Foundry`
   - Copy the key: `rw_...`

4. **Add Credits**:
   - Go to "Billing": https://app.runwayml.com/billing
   - Add payment method and credits
   - Gen-3 Alpha Turbo: ~$0.05 per second of video

#### Pricing:
- Gen-3 Alpha Turbo: $0.05/second (~$3 per minute of generated video)
- Gen-3 Alpha: $0.10/second (~$6 per minute)
- You need to pre-purchase credits

### What to add to .env:
```env
RUNWAY_API_KEY=rw_aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
```

---

## 3. Stability AI API Key

### What it's for:
- Alternative AI video/image generation
- Stable Video Diffusion
- Image generation for video frames

### How to get it:

1. **Sign Up**: https://platform.stability.ai/
2. **Go to Account**:
   - Click "Account" in top right
   - Or: https://platform.stability.ai/account/keys

3. **Create API Key**:
   - Click "Create API Key"
   - Name: `Jynco Video Foundry`
   - Copy key: `sk-...`

4. **Add Credits**:
   - Go to "Billing": https://platform.stability.ai/account/billing
   - Purchase credits (starts at $10)

#### Pricing:
- Image generation: $0.002 - $0.08 per image
- Video: Varies by model
- $10 = ~500-5000 generations depending on model

### What to add to .env:
```env
STABILITY_API_KEY=sk-aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
```

---

## 4. Application Secret Key

### What it's for:
- JWT token signing
- Session encryption
- Password hashing

### How to generate it:

#### Option A: Use Python
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Option B: Use OpenSSL
```bash
openssl rand -base64 32
```

#### Option C: Use the provided script
```bash
./generate_secret.sh
```

This should output something like:
```
YourRandomSecretKey123abc_xyz-789
```

### What to add to .env:
```env
SECRET_KEY=YourGeneratedSecretKeyHere_MakeItLongAndRandom
```

---

## 5. Database Password (Optional)

### What it's for:
- PostgreSQL database authentication
- Default is `password` (fine for development)

### For Production:
Generate a strong password and update both:

```env
# In .env
DATABASE_URL=postgresql://postgres:YOUR_STRONG_PASSWORD@postgres:5432/videofoundry

# In docker-compose.yml (postgres service)
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD
```

---

## Quick Setup Script

We've provided an interactive script to help configure everything:

```bash
./configure_keys.sh
```

This script will:
1. Guide you through each API key
2. Validate the format
3. Update your .env file
4. Test connections (optional)

---

## Testing Your Configuration

After configuring all keys, test them:

```bash
./validate_keys.py
```

This will verify:
- ✅ AWS credentials are valid
- ✅ S3 bucket is accessible
- ✅ Runway API key works
- ✅ Stability AI key works
- ✅ Secret key is strong enough

---

## Cost Summary

### Minimum to Get Started:
- **AWS S3**: ~$0 (free tier: 5GB storage, 20k GET, 2k PUT requests/month)
- **Runway**: $10 minimum (≈200 seconds of video = 3.3 minutes)
- **Stability AI**: $10 minimum (≈500-5000 generations)
- **Total**: ~$20 to start testing

### Monthly Estimate (Light Usage):
- 50 video segments @ 5 sec each = 250 seconds
- Runway cost: 250 × $0.05 = $12.50
- S3 storage (5GB): $0.12
- S3 transfer (10GB): $0.90
- **Total**: ~$13.52/month

### Monthly Estimate (Medium Usage):
- 500 video segments @ 5 sec each = 2500 seconds
- Runway cost: 2500 × $0.05 = $125
- S3 storage (50GB): $1.15
- S3 transfer (100GB): Free (first 100GB)
- **Total**: ~$126/month

---

## Security Best Practices

### DO:
- ✅ Use environment variables (never hardcode keys)
- ✅ Use IAM roles with minimal permissions
- ✅ Rotate keys regularly
- ✅ Use different keys for dev/staging/production
- ✅ Add .env to .gitignore (already done)
- ✅ Use AWS Secrets Manager in production

### DON'T:
- ❌ Commit .env to git
- ❌ Share keys in Slack/email
- ❌ Use root AWS credentials
- ❌ Give S3 full public access
- ❌ Use same keys across environments

---

## Free Tier Alternatives (For Testing)

If you want to test the platform without AI features:

1. **Skip AI Keys**: The platform will work without AI keys
   - You can test the UI, project management, timeline editor
   - Just can't generate actual videos

2. **LocalStack** (AWS S3 Mock):
   ```bash
   # Add to docker-compose.yml
   localstack:
     image: localstack/localstack
     ports:
       - "4566:4566"

   # Update .env
   AWS_ENDPOINT_URL=http://localstack:4566
   S3_BUCKET=test-bucket
   ```

3. **Mock Worker Mode**:
   Set in .env:
   ```env
   MOCK_AI_GENERATION=true
   ```
   This will simulate video generation without calling APIs.

---

## Troubleshooting

### AWS Credentials Invalid
```
Error: The security token included in the request is invalid
```
**Solution**: Check your Access Key ID and Secret Access Key

### S3 Bucket Not Found
```
Error: The specified bucket does not exist
```
**Solution**: Create the bucket or check the bucket name in .env

### Runway API Error
```
Error: Invalid API key
```
**Solution**:
- Verify key starts with `rw_`
- Check you have credits: https://app.runwayml.com/billing

### Stability AI Error
```
Error: Unauthorized
```
**Solution**:
- Verify key starts with `sk-`
- Check you have credits: https://platform.stability.ai/account/billing

---

## Next Steps

1. **Obtain all keys** using the guides above
2. **Run configuration script**: `./configure_keys.sh`
3. **Validate keys**: `./validate_keys.py`
4. **Launch platform**: `./launch.sh`
5. **Test video generation**: Create a project and generate a segment

---

## Need Help?

- **AWS Documentation**: https://docs.aws.amazon.com/s3/
- **Runway API Docs**: https://docs.runwayml.com/
- **Stability AI Docs**: https://platform.stability.ai/docs
- **Jynco Docs**: See README.md and VIDEO_FOUNDRY_README.md

---

**Estimated Time to Configure**: 15-30 minutes (including account creation)

Ready to configure? Run `./configure_keys.sh` to get started! 🚀
