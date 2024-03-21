source ~/startup.sh
WORKPLACE="$HOME/workplace/Media"

WORKSPACE="$WORKPLACE/MediaApi"
(
  cd "$WORKSPACE"
  rsync-project Media
  ssh root@hetzner "pm2 restart api-media"
)
