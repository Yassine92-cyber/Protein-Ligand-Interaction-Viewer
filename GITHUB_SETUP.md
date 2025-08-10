# 🚀 GitHub Setup Guide

This guide will help you set up your Protein-Ligand Interaction Viewer project on GitHub with automated testing, deployment, and project management.

## 📋 Prerequisites

- GitHub account
- Git installed on your local machine
- Project code ready for upload

## 🗂️ Repository Setup

### 1. Create a New Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Fill in the details:
   - **Repository name**: `Protein-Ligand-Interaction-Viewer`
   - **Description**: `A FastAPI-based web service for analyzing protein-ligand interactions using RDKit`
   - **Visibility**: Choose Public or Private
   - **Initialize with**: Check "Add a README file"
   - **Add .gitignore**: Select "Python"
   - **Choose a license**: MIT License (recommended)

### 2. Clone and Setup Local Repository

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Protein-Ligand-Interaction-Viewer.git
cd Protein-Ligand-Interaction-Viewer

# Copy your project files to this directory
# (excluding the .git folder that was created)

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Protein-Ligand Interaction Viewer"

# Push to GitHub
git push origin main
```

## 🔧 GitHub Features Setup

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click "Settings" tab
3. Scroll down to "Pages" section
4. Under "Source", select "GitHub Actions"
5. This will use the workflow we created in `.github/workflows/deploy.yml`

### 2. Enable GitHub Actions

1. Go to "Actions" tab in your repository
2. Click "Enable Actions" if prompted
3. The workflows will automatically run on push/PR

### 3. Set Up Branch Protection (Optional but Recommended)

1. Go to "Settings" → "Branches"
2. Click "Add rule" for the `main` branch
3. Enable:
   - ✅ "Require a pull request before merging"
   - ✅ "Require status checks to pass before merging"
   - ✅ "Require branches to be up to date before merging"

## 📊 GitHub Actions Workflows

### CI/CD Pipeline (`.github/workflows/ci.yml`)

This workflow runs on every push and pull request:

- **Backend Testing**: Tests Python code on multiple OS and Python versions
- **Frontend Testing**: Builds and tests the React frontend
- **Docker Testing**: Builds and tests Docker containers
- **Preview Deployment**: Creates preview environments for PRs

### GitHub Pages Deployment (`.github/workflows/deploy.yml`)

This workflow deploys the frontend to GitHub Pages:

- **Automatic**: Runs on every push to `main` branch
- **Manual**: Can be triggered manually from Actions tab
- **Result**: Your app will be available at `https://YOUR_USERNAME.github.io/Protein-Ligand-Interaction-Viewer/`

## 🎯 Project Management

### 1. Issues and Templates

We've created issue templates for:
- **Bug Reports**: Structured bug reporting
- **Feature Requests**: Organized feature suggestions

### 2. Pull Request Template

The PR template ensures:
- Clear descriptions of changes
- Testing information
- Checklist for quality assurance

### 3. Labels and Milestones

Create labels for:
- `bug` - Bug fixes
- `enhancement` - New features
- `documentation` - Documentation updates
- `good first issue` - Beginner-friendly tasks

## 🚀 Deployment Options

### Option 1: GitHub Pages (Frontend Only)

- **Pros**: Free, automatic, integrated with GitHub
- **Cons**: Frontend only, no backend API
- **Use Case**: Demo, documentation, frontend showcase

### Option 2: Full Deployment (Frontend + Backend)

For full deployment, you'll need additional services:

#### Heroku
```bash
# Install Heroku CLI
# Create Procfile in backend/
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Deploy
heroku create your-app-name
git push heroku main
```

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

#### Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

## 🔐 Environment Variables

### For Backend Deployment

Create these environment variables in your deployment platform:

```bash
# Database (if using)
DATABASE_URL=your_database_url

# API Keys (if needed)
API_KEY=your_api_key

# CORS settings
ALLOWED_ORIGINS=https://yourdomain.com,https://yourdomain.github.io
```

### For Frontend

Update the API base URL in your frontend code:

```typescript
// In frontend/src/lib/api.ts
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-backend-url.com' 
  : 'http://localhost:8000';
```

## 📈 Monitoring and Analytics

### 1. GitHub Insights

- **Traffic**: View repository traffic and popular content
- **Contributors**: Track contributions over time
- **Commits**: Analyze commit patterns

### 2. External Services

- **Uptime Monitoring**: [UptimeRobot](https://uptimerobot.com/)
- **Error Tracking**: [Sentry](https://sentry.io/)
- **Performance**: [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)

## 🧪 Testing Strategy

### 1. Automated Testing

- **Backend**: Python tests with pytest
- **Frontend**: React component tests
- **E2E**: Playwright or Cypress for full user journey testing

### 2. Manual Testing

- **Cross-browser**: Test on Chrome, Firefox, Safari, Edge
- **Mobile**: Responsive design testing
- **Accessibility**: Screen reader compatibility

## 📚 Documentation

### 1. README.md

Your main README should include:
- Project description and features
- Installation instructions
- Usage examples
- API documentation
- Contributing guidelines

### 2. Wiki (Optional)

Enable GitHub Wiki for:
- Detailed setup guides
- Troubleshooting
- API reference
- User guides

## 🔄 Continuous Improvement

### 1. Regular Updates

- Keep dependencies updated
- Monitor security advisories
- Review and update documentation

### 2. Community Engagement

- Respond to issues promptly
- Review pull requests thoroughly
- Encourage contributions
- Maintain a welcoming environment

## 🆘 Troubleshooting

### Common Issues

1. **Workflow Failures**
   - Check Actions tab for error details
   - Verify Python/Node.js versions in workflows
   - Test locally before pushing

2. **Deployment Issues**
   - Check GitHub Pages settings
   - Verify build output paths
   - Review deployment logs

3. **Permission Issues**
   - Ensure workflows have correct permissions
   - Check repository settings
   - Verify GitHub Actions are enabled

## 🎉 Next Steps

1. **Push your code** to GitHub
2. **Enable GitHub Pages** in repository settings
3. **Create your first issue** to test the templates
4. **Set up branch protection** for quality control
5. **Monitor Actions** to ensure everything works
6. **Share your repository** with the community!

## 📞 Need Help?

- **GitHub Docs**: [docs.github.com](https://docs.github.com)
- **GitHub Actions**: [github.com/features/actions](https://github.com/features/actions)
- **GitHub Pages**: [pages.github.com](https://pages.github.com)
- **Community**: [github.community](https://github.community)

Happy coding! 🚀✨ 