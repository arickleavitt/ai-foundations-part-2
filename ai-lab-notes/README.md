# AI Lab Notes

AI Lab Notes is a small beginner-friendly Vite website. It includes a setup
checklist, a Linux and Git command cheat sheet, and a form for saving fictional
lab notes in your browser.

The app does not use external APIs, passwords, tokens, private data, or paid
services.

## What you need

- [Node.js](https://nodejs.org/) version 20.19 or newer
- npm, which is included with Node.js
- Git, if you want to upload the project to GitHub

Check your installed versions:

```bash
node --version
npm --version
git --version
```

## Install

Open a terminal and move into the project folder:

```bash
cd ai-lab-notes
```

Install the project packages:

```bash
npm install
```

## Run the app

Start the Vite development server:

```bash
npm run dev
```

Vite will show a local address, usually `http://localhost:5173`. Open that
address in your browser. Press `Ctrl+C` in the terminal when you want to stop
the server.

## Build the app

Create a production build:

```bash
npm run build
```

The finished files will be placed in the `dist` folder. You can test that build
locally with:

```bash
npm run preview
```

## How saved notes work

The form saves notes with the browser's `localStorage` feature. Notes remain
after refreshing the page, but they are only available in the same browser on
the same device.

Do not enter real private or sensitive information. This project is intended
for fictional practice notes.

## Upload to GitHub

First, create an empty repository on GitHub. Do not add a README or other files
when creating it. Then run these commands from the project folder:

```bash
git init
git add .
git commit -m "Build AI Lab Notes app"
git branch -M main
git remote add origin git@github.com:YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace `YOUR-USERNAME` and `YOUR-REPOSITORY` with your GitHub details.

If this folder is already inside a Git repository, do not run `git init`.
Instead, run the `git add`, `git commit`, and `git push` commands from the main
repository folder.

## Deploy to Vercel

1. Upload the project to GitHub.
2. Sign in at [vercel.com](https://vercel.com/) using your GitHub account.
3. Select **Add New**, then **Project**.
4. Import your GitHub repository.
5. If this app is inside a larger repository, set **Root Directory** to
   `ai-lab-notes`.
6. Vercel should detect Vite automatically. The build command should be
   `npm run build`, and the output directory should be `dist`.
7. Select **Deploy**.

Vercel will provide a public website address after the deployment finishes.
