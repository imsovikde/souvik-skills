# Local Commit Setup (Verified Commits For Souvik Dey)

This is the one-time setup for `imsovikde/souvik-skills` so that commits made **from your own local
machine** (not Claude Code on the web) sign directly and show GitHub's green **Verified** badge
immediately, with no merge-through-UI step required. For the cloud-session flow, see the
"Verified Commits" section in `CLAUDE.md`.

## 1. Set your identity once, locally

```bash
git config --global user.name "Souvik Dey"
git config --global user.email "imsovikde@gmail.com"
```

Use the exact email that is verified on your GitHub account (`imsovikde`), since GitHub links
commits to your contribution graph by matching this address.

## 2. Generate a signing key

Pick one. SSH signing is simpler and is what GitHub now recommends by default.

### Option A — SSH signing (recommended)

```bash
ssh-keygen -t ed25519 -C "imsovikde@gmail.com" -f ~/.ssh/id_ed25519_signing
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519_signing.pub
git config --global commit.gpgsign true
```

Add the public key on GitHub:

1. Copy it: `cat ~/.ssh/id_ed25519_signing.pub`
2. GitHub → Settings → SSH and GPG keys → **New SSH key**
3. Key type: **Signing Key** (not Authentication Key)
4. Paste and save.

### Option B — GPG signing

```bash
gpg --full-generate-key
gpg --list-secret-keys --keyid-format=long
gpg --armor --export <KEY_ID>
git config --global user.signingkey <KEY_ID>
git config --global commit.gpgsign true
```

Add the exported public key block on GitHub under Settings → SSH and GPG keys → **New GPG key**.

## 3. Verify it works

```bash
cd souvik-skills
git commit --allow-empty -m "test: verify local commit signing"
git log -1 --show-signature
git push origin <your-branch>
```

Open the commit on GitHub and confirm it shows the green **Verified** badge. Delete the test commit
or branch once confirmed.

## 4. Recommended: Vigilant mode

Enable GitHub → Settings → SSH and GPG keys → **Vigilant mode**. This marks any commit on your
account that is *not* signed as "Unverified" so an unsigned commit (for example, one merged from a
Claude Code cloud session before its GitHub-UI merge step) never quietly passes as yours.

## Cloud sessions are different

A cloud container (Claude Code on the web) does not hold your private signing key and never will —
copying a signing key into a shared or ephemeral cloud environment would defeat the purpose of the
key. Cloud work therefore always follows the path in `CLAUDE.md`: commit to a branch with your
identity and a clean message (no AI co-author trailer), push, then merge through the GitHub web UI
or API so GitHub signs the resulting commit with its own key. Both paths land a commit that is
Verified and attributed only to `imsovikde`.
