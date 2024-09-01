# Enable flake

I use `direnv` to enable flake by creating a file `.envrc` with this content in my project directory.

```envrc
use flake
```

Then I enable it by command `direnv allow`. This will initialize `flake.nix` every time I enter my project directory.