Local Machine

git reset --hard abda8b1

git push origin main --force

Remote Server

git fetch origin

git reset --hard origin/main

Verification

git log -1 --oneline (Both should show: abda8b1 fixed app pw leak)