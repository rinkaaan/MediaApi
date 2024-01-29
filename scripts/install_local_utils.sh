WORKPLACE="$HOME/workplace/Media"

(
  cd "$WORKPLACE/PythonUtils"
  pip install .
  rm -rf build
)
