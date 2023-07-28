# f-manager `0.1.1`

core repo for factorio mod manager

## Notes

Example of profile file
```
+ base >= 1.1
+ YARM == 0.8.209
- Krastorio2 >= 1.3.15
```
+/- = enabled/disabled

## To-Do

- [ ] Docs for module itself
- [ ] Profiles
    - [ ] enable/disable mod/mods
    - [ ] rename profile
    - [ ] load game with profile
    - [ ] Download/Update/Remove all mods from profile with saving profile configuration
    - [ ] Create on first launch default profile in user data dir (empty or maybe copy of mod-list.json)
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
    - [x] Get token using login/password
    - [x] Downloading mod
    - [x] Get mod info
    - [ ] More exceptions handling different response status codes or API answers
