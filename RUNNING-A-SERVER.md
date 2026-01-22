# Running a server

You can just install a normal Forge 1.20.1 **latest** version server. Extract the modpack to the directory so it populates:

- config
- configureddefaults
- mods
- .. etc.

## Remove these mods

These mods prevent the server from running or causes issues:

- Continuity
- BetterF3
- Oculus
- FastQuit

## Java setup

I suggest that you use GraalVM JDK 24 Community edition, see [here](https://github.com/RikoDEV/pterodactyl-graalvm) for Pterodactyl and [here](https://github.com/graalvm/graalvm-ce-builds/releases) for normal builds.

Use [Birdflop's flags generator](https://birdflop.com/resources/flags) with `MeowIce's Flags` chosen and tick `MeowIce's Flags (GraalVM)` if using the above.

It is recommended that you allocate at least 6-8 GB or more to the server to prevent massive lag spikes from occuring.
