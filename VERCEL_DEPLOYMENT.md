# Vercel Deployment Guide

This guide will help you deploy your Docker-based application to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally with `npm install -g vercel`
3. **Git Repository**: Your code should be in a Git repository

## Quick Deployment

### Option 1: Using the Deployment Scripts

#### Windows
```bash
deploy-vercel.bat
```

#### Linux/macOS
```bash
chmod +x deploy-vercel.sh
./deploy-vercel.sh
```

### Option 2: Manual Deployment

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Build the project**:
   ```bash
   npm run build
   ```

4. **Deploy to Vercel**:
   ```bash
   vercel --prod
   ```

## Environment Variables

You need to set these environment variables in your Vercel dashboard:

### Required Variables
- `VITE_API_URL`: Your backend API URL (e.g., `https://your-backend.vercel.app`)

### Optional Variables
- `VITE_DEV_MODE`: Set to `false` for production
- `VITE_LOG_LEVEL`: Set to `info` or `warn` for production
- `VITE_ENABLE_DEBUG_PANEL`: Set to `false` for production
- `VITE_ENABLE_PERFORMANCE_MONITORING`: Set to `false` for production

## Backend Deployment

Your backend also needs to be deployed. You have several options:

### Option 1: Deploy Backend to Vercel
```bash
cd backend
vercel --prod
```

### Option 2: Deploy Backend to Railway/Heroku
Use the existing deployment scripts in the root directory.

### Option 3: Use Docker on a VPS
Deploy using the Docker configuration.

## Configuration Files

### vercel.json
The `vercel.json` file in the frontend directory configures:
- Build command and output directory
- URL rewrites for SPA routing
- Security headers
- Caching for static assets

### Environment Files
- `.env.local`: Local development (gitignored)
- `.env.example`: Template for environment variables

## Common Issues and Solutions

### 1. Build Failures
- Ensure all dependencies are installed: `npm install`
- Check TypeScript compilation: `npm run build`
- Verify Node.js version compatibility

### 2. API Connection Issues
- Verify `VITE_API_URL` is set correctly in Vercel
- Ensure backend is deployed and accessible
- Check CORS configuration on backend

### 3. Routing Issues
- The `vercel.json` includes SPA routing configuration
- All routes should redirect to `index.html`

### 4. Environment Variables Not Loading
- Variables must be prefixed with `VITE_`
- Set them in Vercel dashboard, not in `.env` files
- Redeploy after changing environment variables

## Testing Your Deployment

1. **Check the build output**:
   ```bash
   npm run build
   ls -la dist/
   ```

2. **Test locally with production build**:
   ```bash
   npm run preview
   ```

3. **Verify environment variables**:
   - Check browser console for any errors
   - Verify API calls are going to the correct URL

## Performance Optimization

The current configuration includes:
- Asset caching with long TTL
- Source maps for debugging
- Optimized build output

## Security

The configuration includes:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Proper CORS handling

## Monitoring and Debugging

- Use Vercel Analytics for performance monitoring
- Check Vercel Function logs for backend issues
- Monitor API response times and errors

## Next Steps

After successful deployment:
1. Test all functionality in production
2. Set up monitoring and alerts
3. Configure custom domain if needed
4. Set up CI/CD pipeline for automatic deployments

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Verify environment variables
3. Test API endpoints independently
4. Check browser console for frontend errors 