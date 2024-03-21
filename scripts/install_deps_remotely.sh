source ~/startup.sh
WORKPLACE="$HOME/workplace/Media"

WORKSPACE="$WORKPLACE/MediaApi"
(
  cd "$WORKSPACE"
  rsync-project Media
  ssh root@hetzner "source ~/startup.sh && cd ~/workplace/Media/MediaApi && py-install"
)
