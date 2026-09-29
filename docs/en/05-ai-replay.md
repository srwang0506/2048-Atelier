# Desktop AI, Coach and Replay

## Choose the assistance you need

| Feature | Use | Executes a move? |
|---|---|---|
| Hint, H | Recommended direction, merge count and immediate gain | No |
| AI step, Enter | Ask AI for one action | Yes |
| Autoplay, Space | Continuous decisions; press again to pause | Yes |
| Coach, C | Background analysis after roughly 450 ms without manual action | No |
| Settings → 查看 AI 分析 | Compare directions, previews, depth, nodes and time | Preview does not move; analysis counts as assistance |
| Replay, R | Review actions already taken | No; randomness is unchanged |

Manual input takes over from autoplay. Mode changes, undo and pauses invalidate stale AI results. The compiled search core may need a few seconds to prepare at startup; manual play remains available. Expedition pauses after each cleared stage for your ability choice.

## Thinking quality versus playback speed

| Search quality | Per-move budget |
|---|---:|
| 快速 / Fast | About 25 ms |
| 标准 / Standard | About 100 ms |
| 深入 / Deep | About 450 ms |
| 自适应 / Adaptive, default | Based on 120 ms, roughly 90–300 ms depending on empty cells; may stop early when direction stabilizes |

Slow, Normal, Fast and 「冲分」 are separate **playback speeds**. Score-push skips animations; it does not imply deeper search. Load affects actual time, and budgets are not frame-rate promises. Standard/Adaptive at normal speed is convenient for watching. Algorithm comparisons require matched seeds, quality, versions, hardware and enough trials; one high-scoring game is not a win-rate estimate.

## Read direction analysis correctly

Classic/Daily/Sprint previews show the board **after merging but before a random tile spawns**. Empty-space and risk descriptions account for the next random spawn. Terminal risk means immediate loss after that one spawn, not the probability of losing the entire future game. Relative score bars are not win probabilities.

Puzzle/Rescue randomness is fixed, so analysis can include the new tile and verified routes. Classic, Daily and Sprint do not peek at future RNG state. Up to 32 same-board/same-budget analyses can be reused; 「重新分析」 forces a fresh search.

## What the algorithms do

Desktop Classic uses Numba-compiled Expectimax in a separate process: maximize player choices, weight tile spawns by probability and deepen iteratively while retaining fully completed depth results. It uses row tables, state caching, low-probability pruning and heuristics for empty space, ordering and merge potential. Its two-word 80-bit board allocates five bits per cell, retains full search beyond 32768 and encodes tiles through 2³⁰. It is not a trained neural network and does not guarantee a global optimum.

Expedition uses a separate bounded search aware of abilities, energy, Freeze, Swap and altered spawn probabilities, sampling spawn locations on open boards. Puzzle/Rescue use breadth-first search with complete random state and replay verification of shortest solutions. Timeout or no discovered route is not proof of impossibility. Budgets and scores from one algorithm should not be applied to every mode.

## Replay

R opens up to 100 recent actions. Step through, play automatically or seek via the score graph. Viewing does not roll back the current game, modify undo history or alter randomness. Expedition starts a new history after stage rewards, so cross-stage playback is not implied. Rescue's separate route comparison contrasts your/original moves with the verified reference.
