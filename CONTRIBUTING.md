# Contributing Guide

Hi there! Thank you for your interest in contributing to Xenia's Expanded Agriculture.

If you are attempting to report an issue, please do so under the [Issues](https://github.com/Creaous/xenias-expanded-agriculture/issues) tab.

## Rules

1. Please be respectful to other contributors.
2. Attempt to follow [Conventional Commits specification](https://www.conventionalcommits.org/en/v1.0.0).
   - This is not enforced but try to stick with it if you can :)
3. Obviously do not attempt to add malware.

## General Guidelines

- Try to allow the modpack to run at around a minimum of 4 GB of RAM with a recommendation of 8 GB.
  - Aim for playable on singleplayer with 4 GB, otherwise, multiplayer should at least be playable.

## Feature Restrictions

Please refrain from adding mods which:

- Add overpowered items and/or blocks which could be considered cheating, e.g. [Chicken Chest](https://www.curseforge.com/minecraft/mc-mods/chicken-chest).
- Add easy methods to skip early game, whether that be vanilla or other mods, e.g. [When Dungeons Arise](https://www.curseforge.com/minecraft/mc-mods/when-dungeons-arise).
- Use TerraBlender to interface with terrian generation, see [here](https://github.com/Glitchfiend/TerraBlender/issues/159). I am aware of [TerraBlenderFix](https://modrinth.com/mod/terrablenderfix) but it is a hacky way around the issue.
- Majorly overhaul the overworld in some way. Please note that the modpack already has the [Lithosphere](https://modrinth.com/datapack/lithosphere) mod.
- Add a lot of blocks and/or items to the Minecraft registry (unless necessary). This is due to the fact that this could cause major lag.

_No hate to any mods listed here, I just do not believe they fit this modpack or have issues that need to be fixed._

## Feature Encouragements

Please add mods that:

- Backport new vanilla features to the older version we use.
- Optimize the game in any way (e.g. with mods or just vanilla).
- Forks of existing mods that improve the original in a notable way.

## Breaking Changes

Contributors should avoid any changes including removal of mods that are critical to the modpack. For example, removing Mekanism would break a lot of players worlds, so they should avoid this where possible. In some rare cases, mods that cause breaking changes may need to be removed. In this case, they should notify the user in some way to at least let them know that they should backup their world.
