# The Farmer Was Replaced 自动化代码

适用于右侧代码技能树已点完的玩家。一个无import的farm_auto.py集成生产、成就和全部16种排行榜；每行最多80字符，设置在文件最前。

## 安装与运行

安装任选以下一种方式。

### 方式一：直接复制代码

在游戏中创建代码窗口，或使用现有窗口，把完整代码复制进去。

**务必将游戏代码窗口重命名为farm_auto（不带.py），否则leaderboard模式无法启用。**

### 方式二：通过文件监视器安装

在游戏中创建代码窗口并命名为 **farm_auto**（不带.py），保存后开启文件监视器，再把farm_auto.py放入当前存档的代码目录，替换同名文件。默认代码目录为 `%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced\Saves\Save0`。

### 运行

核对窗口顶部设置，停止其他程序后，只运行farm_auto。修改设置后先保存，再运行。

**排行榜按游戏内窗口名寻找入口。** 把代码复制到仍叫f0的窗口，或只把farm_auto.py放在磁盘上，不能完成安装；未注册成窗口的文件还可能被游戏保存时清掉。启动后应看到挑战计时和采样进度；立即返回且没有计时，请先核对窗口标题。

生产会重新布置农田。排行榜使用游戏的隔离场景，确认结果后恢复真实农场。无需其他模块或辅助窗口。

## 生产与设置

默认MODE=auto。auto自动备料、买升级、按TARGETS比例持续补库存；balance只均衡、不买升级。库存超过所有参考值仍继续生产。固定资源模式缺必要原料时自动补料。

| MODE | 资源 | 数量/实际分钟 | 收集方式 |
|---|---|---:|---|
| hay | 干草 | 491,996,098 | 定点伴生，多机收割 |
| wood | 木材 | 1,926,024,457 | 定点树木伴生，施肥催熟 |
| carrot | 胡萝卜 | 408,764,749 | 定点伴生，施肥催熟 |
| pumpkin | 南瓜 | 20,378,709 | 16块6×6田，双机合种补苗后合并收割 |
| sunflower | 能量 | 22,982 | 整田种植，多机分列巡回收种 |
| cactus | 仙人掌 | 31,263,133 | 整田行列排序，连锁收割 |
| dinosaur | 骨头 | 2,152,347 | 前约27%走安全捷径，之后走哈密顿回路 |
| weird | 奇异物质 | 1,128,078,058 | 感染树伴生，保留感染收割 |
| gold | 金币 | 4,947,639 | 16个6×6＋16个5×5迷宫，缓存寻路迁移宝箱 |

bush为灌木木材备用模式。表中产速的测试条件：32×32、32架无人机，Speed/Megafarm/Polyculture 5级，草/树/胡萝卜/南瓜10级，向日葵1级，仙人掌/恐龙/迷宫6级，原料充足。按净增×60÷实际秒计算，含启动、布置和收割；不能套用为排行榜成绩。

| 设置 | 含义 |
|---|---|
| MODE | auto、balance、上表资源模式、bush、achievements、leaderboard |
| AUTO_BUY / ALLOW_EXPAND | auto允许买升级 / 允许买扩地 |
| MAX_DRONES | 0使用全部名额；正数限制总数，含主机 |
| COMPANIONS | 基础作物伴生开关 |
| FAST / FERTILIZE | 启用快刷方案 / 允许施肥；weird保留感染 |
| GOLD_SIZE | 默认mixed，使用混合迷宫组合 |
| TARGETS | 相对库存比例；0不主动囤积，但仍可生产必要原料 |
| ACHIEVEMENT_TASK | 默认all；safe省略最后栈溢出；或指定单项 |
| ACH_INCLUDE_OPTIONAL | 是否包含蜂群和泥泞 |
| LEADERBOARD_NAME | 下表16个榜名，默认cactus |
| LEADERBOARD_SPEEDUP | 默认1000000请求高倍率，游戏按电脑能力降速 |

日常种植/生长检查的供水要求至少0.75。产速受生产升级、供料和电脑负载影响。

## 成就

设置MODE=achievements。ACHIEVEMENT_TASK=all依次执行higher_order高阶、pig小猪、healer治愈、fashion时装、swarm蜂群、mud泥泞、wrong_order反序仙人掌、recycling循环利用，最后故意触发stack栈溢出。safe只省略最后栈溢出，正常结束；也可填写某个单项名。

蜂群需要32个名额；时装需要对应帽子。all最后出现递归红字是预期动作。效率成就使用相应资源模式。是否解锁以游戏/Steam显示为准。

## 16种排行榜

例如在farm_auto窗口顶部设置：

```python
MODE = "leaderboard"
LEADERBOARD_NAME = "cactus"
LEADERBOARD_SPEEDUP = 1000000
```

完全复位把LEADERBOARD_NAME改为reset。单机榜自动使用8×8、1架无人机。

| 榜名 | 目标 |
|---|---:|
| hay | 干草2,000,000,000 |
| hay_single | 干草100,000,000 |
| wood | 木材10,000,000,000 |
| wood_single | 木材500,000,000 |
| carrot | 胡萝卜2,000,000,000 |
| carrot_single | 胡萝卜100,000,000 |
| pumpkin | 南瓜200,000,000 |
| pumpkin_single | 南瓜10,000,000 |
| sunflower | 能量100,000 |
| sunflower_single | 能量10,000 |
| cactus | 仙人掌33,554,432 |
| cactus_single | 仙人掌131,072 |
| dinosaur | 骨头33,488,928 |
| gold | 金币9,863,168 |
| gold_single | 金币616,448 |
| reset | 从一格地、零进度发展到解锁排行榜 |

表中资源目标对应游戏构建25234622。游戏没有单机恐龙榜和奇异物质榜。达标后代码退出，游戏重复采样至累计至少2小时游戏时间，再显示平均成绩。倍率只缩短现实等待，不改变游戏计时成绩。

---

# The Farmer Was Replaced Automation (English)

For players who have fully unlocked the code skill tree on the right. A single `farm_auto.py` file handles production, achievements, and all 16 leaderboards without imports. Each line is at most 80 characters long, and all user settings are at the top of the file.

## Installation and Running

Choose either installation method below.

### Method 1: Copy and Paste

Create a code window in the game, or use an existing one, and paste the complete script into it.

**You must rename the in-game code window to `farm_auto` (without `.py`), or leaderboard mode will not work.**

### Method 2: Install with the File Watcher

Create a code window in the game and name it **`farm_auto`** (without `.py`). Save it, enable the file watcher, and copy `farm_auto.py` into the code directory of your current save, replacing the file with the same name. The default code directory is `%USERPROFILE%\AppData\LocalLow\TheFarmerWasReplaced\TheFarmerWasReplaced\Saves\Save0`.

### Running

Check the settings at the top of the code window, stop any other running programs, and run only `farm_auto`. After changing settings, save before running.

**Leaderboards locate the entry script by its in-game window name.** Pasting the code into a window still named `f0`, or placing `farm_auto.py` on disk without creating its in-game window, does not complete the installation. Files without a corresponding code window may also be removed when the game saves. After starting a leaderboard run, you should see the challenge timer and sampling progress. If the script returns immediately without a timer, check the window title first.

Production rearranges the farm. Leaderboards run in the game's isolated challenge environment; the real farm is restored after you confirm the results. No other modules or helper windows are required.

## Production and Settings

The default is `MODE = "auto"`. In `auto` mode, the script prepares materials, buys upgrades, and continuously replenishes inventory according to the ratios in `TARGETS`. The `balance` mode balances inventory without buying upgrades. Production continues even when all inventories exceed their reference values. Resource-specific modes automatically produce any required materials that are missing.

| MODE | Resource | Units per real-world minute | Method |
|---|---|---:|---|
| hay | Hay | 491,996,098 | Companion planting at fixed locations, harvested by multiple drones |
| wood | Wood | 1,926,024,457 | Tree companion planting at fixed locations, accelerated with fertilizer |
| carrot | Carrots | 408,764,749 | Companion planting at fixed locations, accelerated with fertilizer |
| pumpkin | Pumpkins | 20,378,709 | Sixteen 6×6 plots; two drones plant and replace dead pumpkins together, then harvest the merged pumpkins |
| sunflower | Power | 22,982 | Full-field planting; multiple drones patrol assigned columns to harvest and replant |
| cactus | Cacti | 31,263,133 | Full-field row and column sorting, followed by chain harvesting |
| dinosaur | Bones | 2,152,347 | Safe shortcuts for approximately the first 27% of the field, then a Hamiltonian cycle |
| weird | Weird Substance | 1,128,078,058 | Infected tree companion planting; infection is preserved until harvest |
| gold | Gold | 4,947,639 | Sixteen 6×6 and sixteen 5×5 mazes; cached pathfinding for relocated treasure |

`bush` is a fallback wood mode using bushes. The production rates above were measured with a 32×32 field and 32 drones; Speed, Megafarm, and Polyculture at level 5; Grass, Trees, Carrots, and Pumpkins at level 10; Sunflowers at level 1; Cactus, Dinosaurs, and Mazes at level 6; and sufficient materials. Rates are calculated as net inventory gain × 60 ÷ elapsed real-world seconds, including startup, field setup, and harvesting. They are not leaderboard scores.

| Setting | Description |
|---|---|
| MODE | `auto`, `balance`, any resource mode above, `bush`, `achievements`, or `leaderboard` |
| AUTO_BUY / ALLOW_EXPAND | Allow `auto` mode to buy upgrades / allow field expansion purchases |
| MAX_DRONES | `0` uses all available drone slots; a positive value caps the total, including the main drone |
| COMPANIONS | Enable companion planting for basic crops |
| FAST / FERTILIZE | Enable fast farming strategies / allow fertilizer; `weird` preserves infection |
| GOLD_SIZE | Defaults to `"mixed"`, using the mixed maze sizes above |
| TARGETS | Relative inventory ratios; `0` disables intentional stockpiling but still allows production of required materials |
| ACHIEVEMENT_TASK | Defaults to `"all"`; `"safe"` skips the final stack overflow; or specify an individual task |
| ACH_INCLUDE_OPTIONAL | Include the swarm and mud tasks |
| LEADERBOARD_NAME | One of the 16 leaderboard names below; defaults to `"cactus"` |
| LEADERBOARD_SPEEDUP | Defaults to `1000000` to request a high speed multiplier; the game reduces it to match your computer's capacity |

Routine planting and growth checks require a water level of at least `0.75`. Production rates vary with upgrades, material supply, and computer load.

## Achievements

Set `MODE = "achievements"`. With `ACHIEVEMENT_TASK = "all"`, the script runs these tasks in order: `higher_order` (higher-order functions), `pig` (pig), `healer` (healing), `fashion` (fashion), `swarm` (swarm), `mud` (mud), `wrong_order` (reverse cactus order), and `recycling` (recycling). Finally, `stack` intentionally triggers a stack overflow. The `"safe"` option skips only the final stack overflow and finishes normally. You can also specify any individual task name.

The swarm task requires 32 drone slots, and the fashion task requires the corresponding hats. The red recursion error at the end of `"all"` is expected. Use the corresponding resource modes for efficiency achievements. Check the game or Steam to confirm whether an achievement has unlocked.

## All 16 Leaderboards

For example, set the following at the top of the `farm_auto` window:

```python
MODE = "leaderboard"
LEADERBOARD_NAME = "cactus"
LEADERBOARD_SPEEDUP = 1000000
```

For the full reset challenge, change `LEADERBOARD_NAME` to `"reset"`. Single-drone leaderboards automatically use an 8×8 field and one drone.

| Leaderboard name | Target |
|---|---:|
| hay | 2,000,000,000 Hay |
| hay_single | 100,000,000 Hay |
| wood | 10,000,000,000 Wood |
| wood_single | 500,000,000 Wood |
| carrot | 2,000,000,000 Carrots |
| carrot_single | 100,000,000 Carrots |
| pumpkin | 200,000,000 Pumpkins |
| pumpkin_single | 10,000,000 Pumpkins |
| sunflower | 100,000 Power |
| sunflower_single | 10,000 Power |
| cactus | 33,554,432 Cacti |
| cactus_single | 131,072 Cacti |
| dinosaur | 33,488,928 Bones |
| gold | 9,863,168 Gold |
| gold_single | 616,448 Gold |
| reset | Start with a single tile and no progress, then unlock leaderboards |

The resource targets above correspond to game build `25234622`. The game has no single-drone dinosaur leaderboard or Weird Substance leaderboard. Once the target is reached, the script exits. The game repeats the run until at least two hours of cumulative game time have been sampled, then displays the average result. The speed multiplier reduces real-world waiting time without changing the score measured in game time.
