WORKPLACE="$HOME/workplace/Media"
WORKSPACE="$WORKPLACE/MediaApi"

(
  cd "$WORKSPACE/api"
  flask spec --output openapi.yaml > /dev/null
)
