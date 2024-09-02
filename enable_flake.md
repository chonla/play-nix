# Enable Flakes

Create file `~/.config/nix/nix.conf` with this content.

```
experimental-features = nix-command flakes
```

## Hook Flakes

I use `direnv` to enable flake by creating a file `.envrc` with this content in my project directory.

```envrc
use flake
```

Then I enable it by command `direnv allow`. This will initialize `flake.nix` every time I enter my project directory.