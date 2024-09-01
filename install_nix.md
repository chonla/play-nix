# Install nix

Reference: _https://nix.dev/install-nix.html_

## Linux

```bash
curl -L https://nixos.org/nix/install | sh -s -- --daemon
```

## MacOS

```bash
curl -L https://nixos.org/nix/install | sh
```

## Windows WSL2 (Single user installation)

```bash
curl -L https://nixos.org/nix/install | sh -s -- --no-daemon
```

## Windows WSL2 (Multiple users installation)

```bash
curl -L https://nixos.org/nix/install | sh -s -- --daemon
```

## Verify if installation is success

```bash
$ nix --version
nix (Nix) 2.11.0
```