# Changelog

All notable changes to this project will be documented in this file.

## [2.0.2] - 2024-06-01

### Added

- Reimplemented animated waiting screen for opponent in the new frontend. (previously available in terminal version).
- Reimplemented resign functionality in the new frontend (previously available in terminal version).
- Reimplemented draw offer functionality in the new frontend (previously available in terminal version).
- Added frontend pop-up notifications for invalid moves, improving interaction (adapted for new frontend, previously in terminal).
- Added highlights to selected chessboard square on click for better visibility.

### Fixed

- Adjusted chess tests to align with changes in game functionality.
- Corrected a game logic error related to the EmptySquare implementation.
- Fixed detection of the en passant rule in the game logic.
- Implemented switching turns logic on the game server to manage player turns correctly.
- Moved location of the flake8 configuration file for better code style enforcement.

## [2.0.1] - 2024-04-14

### Changed

- Updated tests to align with version 2.0.0 changes.
- Cleaned up the codebase and improved documentation and in-line comments

## [2.0.0] - 2024-04-14

### Added

- Frontend layer to handle user interactions through a web interface.

### Removed

- Terminal-based client.py, transitioning all user interactions to the new frontend.

### Changed

- Server refactored to support new web-based client interactions.

## [1.0.0] - 2024-03-06

### Added

- Initial release of the chess game application with terminal-based user interface and backend functionalities.
