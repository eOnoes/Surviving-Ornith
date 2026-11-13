# Surviving Ornith

**Surviving Ornith** is an original, single-player survival vertical slice set on Ornith Island. It is built with the Rust **Unbiased Bob Engine (UBE), nerd 0.1**.

This is an independent game repository. The engine is consumed through its public `engine` API from [eOnoes/UBE](https://github.com/eOnoes/UBE); engine sources are not duplicated here.

## Play

Requires Windows, DirectX 12, and Rust 1.99.1 or newer.

```sh
cargo run --release
```

Launch the executable with this repository as its working directory so it can find `assets/ornith/`. To disable audio:

```sh
cargo run --release -- --no-audio
```

## Controls

| Input | Action |
| --- | --- |
| WASD | Move |
| Space | Jump while standing on the ground |
| Left Ctrl | Toggle crouching / standing |
| Z | Toggle prone / standing |
| Left Shift | Hold with movement to sprint; uses energy |
| Right mouse / mouse | Capture cursor and look |
| Left mouse | Fire, harvest, or place the selected structure |
| 1 / 2 | Rifle / pistol |
| 3 / 4 | Pickaxe / axe |
| R | Reload |
| E | Forage, tame, or breed |
| B | Toggle build mode |
| X or Tab | Cycle wall / foundation |
| F | Eat meat or berries |
| C | Companions follow / stay |
| V | First-person / third-person / top-down |
| Escape | Release cursor and clear held input |

Sprinting drains energy, which recovers when sprinting stops. Crouching and prone movement are slower, and a low ceiling can prevent standing back up. The HUD shows stance, sprint state, and energy.

Start with 4 meat and 4 berries. Wolves and hawks eat meat; cows eat berries. A tamed adult needs a nearby, tamed adult of the opposite sex and 2 additional food to breed. Babies mature after 45 seconds.

The rifle is accurate and long-ranged but holds one round and reloads slowly. The pistol fires faster, holds six rounds, and has more spread with a shorter effective range. Successful shots produce visible recoil; tools swing even on a miss. Wood, stone, animal impacts, swings, gunfire, and reloads have distinct sound feedback.

## Original assets

The 17 GLB models and 15 WAV clips are deterministic procedural originals generated locally by `tools/generate_ornith_assets.py`. No downloaded game assets are used.

```sh
python tools/generate_ornith_assets.py
```

## Verify

```sh
cargo fmt --all --check
cargo check --workspace --all-targets
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
cargo build --release --workspace
```

Native Windows playtests:

```sh
python tools/ornith_smoke.py
python tools/ornith_movement_smoke.py
python tools/ornith_loop_smoke.py
```

See `docs/surviving-ornith.md` for gameplay evidence and limitations.

## Scope

This is a compact, polished test island—not a complete ARK-scale survival game or a multiplayer release. Networking and full gameplay-state save/load remain future work.

## License

MIT. The owner-provided `LICENSE` is preserved. UBE and its third-party dependencies retain their respective licenses and notices; the generated bundle is in `THIRD_PARTY_NOTICES.html`, including the bundled IBM Plex font notice.
