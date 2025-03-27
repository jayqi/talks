# Print this help documentation
help:
    just --list

# Add a submodule and remove the local files
add-submodule repo path:
    # git submodule add {{repo}} {{path}}
    git submodule deinit -f {{path}}
    rm -rf .git/modules/{{path}}

# Render README.md
render-readme:
    uv run _src/main.py
