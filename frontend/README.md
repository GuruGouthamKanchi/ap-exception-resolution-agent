This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

## Vercel Deployment Instructions

### 1. Set Environment Variables
After importing your project to Vercel, navigate to **Project Settings** -> **Environment Variables** and add the following variable:

*   **Key**: `NEXT_PUBLIC_API_URL`
*   **Value**: `https://ap-exception-resolution-agent.onrender.com` (Your deployed Render backend URL)

### 2. Deploy via Dashboard (Recommended)
1. Go to [Vercel](https://vercel.com/new).
2. Connect your GitHub account and import your repository: `ap-exception-resolution-agent`.
3. In the setup page, configure:
   * **Root Directory**: `frontend` (crucial since this is a monorepo).
   * **Framework Preset**: `Next.js`.
4. Expand the **Environment Variables** section and paste `NEXT_PUBLIC_API_URL` with your Render backend URL.
5. Click **Deploy**.

### 3. Deploy via Vercel CLI
If you prefer terminal deploys:
```bash
# Install CLI
npm install -g vercel

# From the frontend directory:
vercel
```
Follow the interactive prompts, then configure the environment variable inside Vercel's console and redeploy:
```bash
vercel env add NEXT_PUBLIC_API_URL https://ap-exception-resolution-agent.onrender.com
vercel --prod
```

