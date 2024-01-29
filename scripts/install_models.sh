WORKPLACE="$HOME/workplace/Media"

(
  cd "$WORKPLACE/MediaModels"
  pip install .
  rm -rf build
)
