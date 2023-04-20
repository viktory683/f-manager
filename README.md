# f-manager

core repo for factorio mod manager

## To-Do

- [ ] Docs for module itself
- [ ] Profiles
  - [ ] enable/disable mod/mods
  - [ ] rename profile
  - [ ] load game with profile
  - [ ] Download/Update/Remove all mods from profile with saving profile configuration
- [ ] Saves
  - [ ] Sync profile with save
  - [ ] Sync save with profile
  - [ ] Start game using save
  - [ ] Remove/backup
- [ ] Game start
  - [ ] Test if it works
  - [ ] Test if it works properly when game need to restart
- [ ] Mods managing
  - [ ] Downloading
    - [ ] Check if mod already installed
      - [ ] Reinstall only mod without dependencies if no updates available
    - [ ] Download dependencies
  - [ ] Update
  - [ ] Dependencies managing
  - [ ] Fully refactor ``Mod`` and ``ModController`` classes
    - [ ] ...
- [ ] Configuration
  - [ ] Base game directory
  - [ ] User data directory
  - [ ] Authentication options
    - [ ] username/password
    - [ ] username/token
      - [ ] Save token to user data directory
- [ ] API
  - [ ] Get token using login/password
  - [ ] Downloading mod
  - [ ] Get mod info
    - [ ] ...
  - [ ] More exceptions handling different response status codes or API answers
