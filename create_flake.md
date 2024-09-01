## Start using nix with Flakes

1. Create a new `flake.nix`, using command `nix flake init`. A new `flake.nix` will be created with the following content.

    ```nix
    {
        description = "A very basic flake";

        inputs = {
            nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
        };

        outputs = { self, nixpkgs }: {

            packages.x86_64-linux.hello = nixpkgs.legacyPackages.x86_64-linux.hello;

            packages.x86_64-linux.default = self.packages.x86_64-linux.hello;

        };
    }
    ```

    - `description` is description shown by `nix flake metadata`.
    - `inputs` defines other flakes that this flake depends on. The dependencies will be passed to `outputs`.
    - `outputs` produces attribute set.

2. Replace the `flake.nix` with the below content.
   
    ```nix
    {
        description = "A very basic flake";

        inputs.nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";

        outputs = { self, nixpkgs }: 
        let 
            supportedSystems = [ "aarch64-darwin" ]; 
        in 
        {
            devShells = builtins.foldl' (prev: system: prev // {
                ${system}.default = nixpkgs.legacyPackages.${system}.mkShell {
                    buildInputs = with nixpkgs.legacyPackages.${system}; [

                    ];

                    shellHook = ''

                    '';
                };
            }) {} supportedSystems;

            packages = builtins.foldl' (prev: system: prev // {
                ${system}.default = nixpkgs.legacyPackages."${system}".hello; 
            }) {} supportedSystems;
        };
    }
    ```

    - `inputs.nixpkgs.url` refers to nix packages channel. See https://search.nixos.org/packages for latest channel version. You can replace `unstable` with the version in the link.
    - `supportedSystem` is a list of platform supported for this nix. See all platforms supported by nix [here](https://nix.dev/manual/nix/2.18/installation/supported-platforms#supported-platforms).
    - `buildInputs` is a list of packages that will be available when built. See all package names and versions on corresponding channel [here](https://search.nixos.org/packages).
    - `shellHook` is a sequence of commands that will be executed every time when start `nix shell` or `nix develop`.
  
    **Example**

    The `flake.nix` below creates nix for MacOS and Linux 64 bits platform. Ruby 3.3, bundler, and playwright will be available after shell is initiated.

    ```nix
    {
        description = "A very basic flake";

        inputs.nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";

        outputs = { self, nixpkgs }: 
        let 
            supportedSystems = [ "aarch64-darwin" "x86_64-linux" ]; 
        in 
        {
            devShells = builtins.foldl' (prev: system: prev // {
                ${system}.default = nixpkgs.legacyPackages.${system}.mkShell {
                    buildInputs = with nixpkgs.legacyPackages.${system}; [
                        ruby_3_3
                        bundler
                        playwright
                    ];

                    shellHook = ''
                        export PLAYWRIGHT_BROWSERS_PATH=${nixpkgs.legacyPackages.${system}.playwright-driver.browsers}
                        export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
                    '';
                };
            }) {} supportedSystems;

            packages = builtins.foldl' (prev: system: prev // {
                ${system}.default = nixpkgs.legacyPackages."${system}".hello; 
            }) {} supportedSystems;
        };
    }
    ```