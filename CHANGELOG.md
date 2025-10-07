# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-07

### Added
- Initial release of custom Nanoleaf integration
- Copied all files from Home Assistant core Nanoleaf integration (version 2024.x)
- Modified to use custom fork of aionanoleaf library from https://github.com/latetedemelon/aionanoleaf
- Added HACS support via hacs.json
- Added comprehensive README with installation instructions
- Added INSTALLATION.md with detailed setup guide

### Changed
- Updated manifest.json to point to custom aionanoleaf fork
- Changed codeowners to @latetedemelon
- Updated documentation URL to point to this repository

### Features
- Full support for Nanoleaf Light Panels
- Support for Nanoleaf Canvas
- Support for Nanoleaf Shapes
- Support for Nanoleaf Elements
- Support for Nanoleaf Lines
- SSDP and Zeroconf discovery
- Touch event support for compatible models
- HomeKit integration support
- Local push updates

## [Unreleased]

### Planned
- Testing of new features from forked aionanoleaf library
- Bug fixes and improvements before upstream PR submission
