# Setup Guide

This repo is a **plug-and-play GitHub profile README generator**. Nothing
here is hand-written — `README.md` and `assets/svg/terminal.svg` are build
artifacts produced by `scripts/generate_terminal.py` from `config.yml` +
`user.yml`. Don't hand-edit `README.md` directly; edit the config and
regenerate, or your changes will be overwritten by the next automated run.

## 1. Use this as your profile repo

GitHub renders a special README on your profile page when you have a repo
named **exactly your username**. If this isn't already that repo:

1. Create a new repo on GitHub named `<your-username>/<your-username>`
   (public).
2. Push this project's contents to it.

## 2. Install locally (optional, for previewing changes)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 3. Personalize

1. Edit `user.yml` — your name, role, skills, focus areas, about copy,
   contact links. This is *all* of your personal content.
2. Edit `config.yml` — colors, typography, ASCII-portrait settings.
3. Drop a photo at `assets/img/profile.jpg` for the ASCII portrait (a
   generic silhouette placeholder is used until you do).
4. Regenerate everything:

   ```bash
   python scripts/generate_all.py
   ```

5. Commit and push. GitHub renders the new `README.md` on your profile.

## 4. Enable the automation

Once pushed to GitHub, `.github/workflows/generate-assets.yml` takes over:
it rebuilds `assets/svg/terminal.svg` + `README.md` on every push to
`config.yml`/`user.yml`/`assets/img/**`/`scripts/**`, daily at 05:00 UTC
(keeps the profile-views counter fresh), and on manual dispatch.

No secrets are required — the profile-views counter is a public,
unauthenticated widget keyed off your username.

Make sure **Settings → Actions → General → Workflow permissions** is set
to "Read and write permissions" so the workflow can push the regenerated
files back to the repo.

## 5. Everyday editing

You basically never touch `scripts/` or `README.md` by hand again:

- Change your tagline / bio / focus table / skills → edit `user.yml` → push.
- Change the color theme → edit `config.yml` → `theme:` → push.
- New photo → replace `assets/img/profile.jpg` → push.

Every push to `main` touching those files triggers `generate-assets.yml`,
which regenerates and commits the new SVG + README automatically.

See [CUSTOMIZATION.md](CUSTOMIZATION.md) for a field-by-field reference.
