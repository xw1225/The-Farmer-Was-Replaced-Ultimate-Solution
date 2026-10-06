MODE = "auto"
# 模式: auto自动 / balance均衡 / hay干草 / wood木材 / carrot胡萝卜 / pumpkin南瓜
# sunflower能量 / cactus仙人掌 / dinosaur骨头 / weird奇异物质 / gold金币 / bush灌木
# achievements成就 / leaderboard排行榜(含完全复位)
ACHIEVEMENT_TASK = "all"  # all全部任务(最后故意栈溢出) / safe不做栈溢出 / 或以下单项
# 单项: higher_order高阶 / pig小猪 / healer治愈 / fashion时装 / swarm蜂群
# mud泥泞 / wrong_order反序仙人掌 / recycling循环利用 / stack栈溢出
LEADERBOARD_NAME = "cactus"
# 排行榜入口固定为farm_auto；请将游戏代码窗口命名为farm_auto并保存。
# 常规: hay干草 / wood木材 / carrot胡萝卜 / pumpkin南瓜 / sunflower能量
# cactus仙人掌 / dinosaur骨头 / gold金币
# 单机: hay_single / wood_single / carrot_single / pumpkin_single
# sunflower_single / cactus_single / gold_single (固定8×8、1架)
# 完全复位: reset (从零发展到解锁排行榜)
LEADERBOARD_SPEEDUP = 1000000  # 请求高倍率；游戏按电脑能力降速，成绩仍按游戏计时
GOLD_SIZE = "mixed"
AUTO_BUY = True
ALLOW_EXPAND = True
MAX_DRONES = 0
COMPANIONS = True
FAST = True
FERTILIZE = True
ACH_INCLUDE_OPTIONAL = True  # 成就流程包含可选任务
_ENTRY_TIME = get_time()  # 内部启动判定，须在下方字典之前
TARGETS = {Items.Hay:100000, Items.Wood:100000, Items.Carrot:50000,
           Items.Pumpkin:20000, Items.Power:5000, Items.Cactus:10000,
           Items.Bone:50000, Items.Weird_Substance:2000, Items.Gold:10000}
pr_MODE = 'auto'
pr_MULTI_ENABLED = True
pr_MAX_DRONES = 0
pr_POLYCULTURE_ENABLED = 'auto'
pr_WATER_ENABLED = True
pr_WATER_TARGET = 0.75
pr_TREE_COMPANION_SCOPE = 'trees'
pr_POLY_SPEND_FRACTION = 0.1
pr_WEIRD_BATCH_PLANTS = 16
pr_SUNFLOWER_KEEP = 10
pr_MAZE_USE_MEASURE = True
pr_PASSIVE_WAIT_SECONDS = 120
pr_WAIT_LOG_SECONDS = 10
pr_GROW_WAIT_SECONDS = 600
pr_MULTI_VERBOSE = False
pr_PERF_VERBOSE = False
pr_POLY_LAST_METHOD = {}
pr_POLY_CONTEXT = {'reserves': {}, 'last_batch': None}

def pr_go_to(tx, ty):
    n = get_world_size()
    dx = (tx - get_pos_x()) % n
    if dx <= n // 2:
        for step in range(dx):
            move(East)
    else:
        for step in range(n - dx):
            move(West)
    dy = (ty - get_pos_y()) % n
    if dy <= n // 2:
        for step in range(dy):
            move(North)
    else:
        for step in range(n - dy):
            move(South)

def pr_report_supply_wait(item, required, elapsed):
    quick_print(
        '仍在等待自动补给：',
        item,
        '现有',
        num_items(item),
        '需要',
        required,
        '已等待游戏秒',
        elapsed
    )
    if item == Items.Water:
        quick_print(
            '当前格',
            get_pos_x(),
            get_pos_y(),
            '水位',
            get_water(),
            '要求至少',
            pr_WATER_TARGET,
            '；严格水位模式，不能缺水强行继续。'
        )

def pr_wait_for_item(item, required):
    if num_items(item) >= required:
        return True
    started = get_time()
    last_report = started
    pr_report_supply_wait(item, required, 0)
    while num_items(item) < required:
        now = get_time()
        if pr_PASSIVE_WAIT_SECONDS > 0:
            if now - started >= pr_PASSIVE_WAIT_SECONDS:
                quick_print(
                    '自动补给等待超时：',
                    item,
                    '现有',
                    num_items(item),
                    '需要',
                    required,
                    '；保留现场并停止。请检查水/肥料补给升级。'
                )
                return False
        if pr_WAIT_LOG_SECONDS > 0:
            if now - last_report >= pr_WAIT_LOG_SECONDS:
                pr_report_supply_wait(item, required, now - started)
                last_report = now
        do_a_flip()
    return True

def pr_water_here():
    if not pr_WATER_ENABLED:
        return True
    if num_unlocked(Unlocks.Watering) == 0:
        quick_print('浇水未解锁，无法满足0.75水位要求。')
        return False
    if pr_WATER_TARGET < 0 or pr_WATER_TARGET > 1:
        quick_print('WATER_TARGET必须在0到1之间。')
        return False
    started = get_time()
    while get_water() < pr_WATER_TARGET:
        if (
            pr_PASSIVE_WAIT_SECONDS > 0
            and get_time() - started >= pr_PASSIVE_WAIT_SECONDS
        ):
            quick_print('当前格补水超时：', get_pos_x(), get_pos_y(), '水位', get_water())
            return False
        if not pr_wait_for_item(Items.Water, 1):
            return False
        if not use_item(Items.Water):
            if pr_MULTI_ENABLED and num_items(Items.Water) < 1:
                continue
            quick_print('浇水失败，脚本停止，不把缺水当作达标。')
            return False
    return True

def pr_wait_until_ready():
    started = get_time()
    while not can_harvest():
        if not pr_water_here():
            return False
        if pr_GROW_WAIT_SECONDS > 0:
            if get_time() - started >= pr_GROW_WAIT_SECONDS:
                quick_print('作物成熟等待超时：', get_pos_x(), get_pos_y())
                return False
        pass
    return pr_water_here()

def pr_ensure_crop(entity, ground):
    current = get_entity_type()
    if current != entity:
        if current != None:
            harvest()
    if get_ground_type() != ground:
        till()
    if entity == Entities.Grass and ground == Grounds.Grassland:
        return pr_water_here()
    if get_entity_type() != entity:
        if not plant(entity):
            return False
    return pr_water_here()

def pr_tree_site(x, y, n):
    if n % 2 == 1:
        if x == n - 1 or y == n - 1:
            return False
    return (x + y) % 2 == 0

def pr_tree_slot_count(n):
    side = n - n % 2
    return side * side // 2

def pr_basic_target(mode, x, y, n):
    if mode == 'hay':
        return (Entities.Grass, Grounds.Grassland)
    if mode == 'bush':
        return (Entities.Bush, Grounds.Grassland)
    if mode == 'carrot':
        return (Entities.Carrot, Grounds.Soil)
    if mode == 'wood':
        if num_unlocked(Entities.Tree) > 0 and pr_tree_site(x, y, n):
            return (Entities.Tree, Grounds.Grassland)
        return (Entities.Bush, Grounds.Grassland)
    return (None, None)

def pr_serial_sunflower_cycle():
    n = get_world_size()
    buckets = []
    for i in range(9):
        buckets.append([])
    pr_go_to(0, 0)
    for x in range(n):
        for y in range(n):
            if not pr_ensure_crop(Entities.Sunflower, Grounds.Soil):
                return False
            petals = measure()
            if petals == None:
                quick_print('向日葵测量失败，请检查解锁和游戏版本。')
                return False
            if petals < 7 or petals > 15:
                quick_print('花瓣范围与本脚本不符：', petals)
                return False
            buckets[15 - petals].append((x, y))
            move(North)
        move(East)
    keep = pr_SUNFLOWER_KEEP
    if keep < 0:
        keep = 0
    if keep >= n * n:
        keep = 0
    remaining_to_harvest = n * n - keep
    for bucket in buckets:
        for pos in bucket:
            if remaining_to_harvest == 0:
                return True
            pr_go_to(pos[0], pos[1])
            if not pr_wait_until_ready():
                return False
            harvest()
            remaining_to_harvest -= 1
    return True

def pr_ensure_pumpkin():
    if get_entity_type() == Entities.Dead_Pumpkin:
        if get_ground_type() != Grounds.Soil:
            till()
        if not plant(Entities.Pumpkin):
            return False
        return pr_water_here()
    return pr_ensure_crop(Entities.Pumpkin, Grounds.Soil)

def pr_serial_pumpkin_cycle():
    n = get_world_size()
    pending = []
    pr_go_to(0, 0)
    for x in range(n):
        for y in range(n):
            if not pr_ensure_pumpkin():
                return False
            if not can_harvest():
                pending.append((x, y))
            move(North)
        move(East)
    while len(pending) > 0:
        next_pending = []
        for pos in pending:
            pr_go_to(pos[0], pos[1])
            if not pr_ensure_pumpkin():
                return False
            if not can_harvest():
                next_pending.append(pos)
        pending = next_pending
    pr_go_to(0, 0)
    harvest()
    return True

def pr_sort_cactus(n):
    for y in range(n):
        if not pr_cactus_sort_line(y, False, False):
            return False
    for x in range(n):
        if not pr_cactus_sort_line(x, True, False):
            return False
    return True

def pr_serial_cactus_cycle():
    n = get_world_size()
    pr_go_to(0, 0)
    for x in range(n):
        for y in range(n):
            if not pr_ensure_crop(Entities.Cactus, Grounds.Soil):
                return False
            move(North)
        move(East)
    if not pr_sort_cactus(n):
        return False
    pending = []
    pr_go_to(0, 0)
    for x in range(n):
        for y in range(n):
            if not can_harvest():
                pending.append((x, y))
            move(North)
        move(East)
    while len(pending) > 0:
        next_pending = []
        for pos in pending:
            pr_go_to(pos[0], pos[1])
            if not can_harvest():
                if not pr_water_here():
                    return False
                next_pending.append(pos)
        pending = next_pending
    pr_go_to(0, 0)
    harvest()
    return True

def pr_serial_basic_batch(mode):
    n = get_world_size()
    pr_go_to(0, 0)
    for x in range(n):
        for y in range(n):
            entity, ground = pr_basic_target(mode, x, y, n)
            if not pr_ensure_crop(entity, ground):
                return False
            move(North)
        move(East)
    pr_go_to(0, 0)
    for x in range(n):
        for y in range(n):
            if not pr_wait_until_ready():
                return False
            harvest()
            move(North)
        move(East)
    return True

def pr_serial_prepare_empty_field():
    n = get_world_size()
    pr_go_to(0, 0)
    for x in range(n):
        for y in range(n):
            if get_entity_type() != None:
                harvest()
            if get_ground_type() != Grounds.Soil:
                till()
            move(North)
        move(East)
    return True

def pr_weird_sites():
    sites = []
    n = get_world_size()
    for x in range(n):
        for y in range(n):
            if pr_tree_site(x, y, n):
                sites.append((x, y))
                if len(sites) >= pr_WEIRD_BATCH_PLANTS:
                    return sites
    if len(sites) == 0:
        sites.append((0, 0))
    return sites

def pr_weird_cleanup_jobs(sites):
    n = get_world_size()
    primary = {}
    cleanup = {}
    for position in sites:
        primary[position] = True
        cleanup[position] = True
    for position in sites:
        x, y = position
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            neighbor = ((x + dx) % n, (y + dy) % n)
            if neighbor not in cleanup:
                cleanup[neighbor] = False
    jobs = []
    for position in cleanup:
        jobs.append((position, cleanup[position]))
    return (jobs, primary)

def pr_weird_worker(phase, lo, hi, data):
    if phase == 'weird_clear':
        for i in range(lo, hi):
            position, primary = data[i]
            pr_go_to(position[0], position[1])
            if primary:
                if get_ground_type() != Grounds.Soil:
                    till()
                if get_entity_type() != None:
                    harvest()
            elif get_entity_type() == Entities.Tree:
                if not harvest():
                    return (False, [])
        return (True, [])
    sites, primary, with_companions = data
    records = []
    for i in range(lo, hi):
        position = sites[i]
        pr_go_to(position[0], position[1])
        if phase == 'weird_prepare':
            if not pr_ensure_crop(Entities.Tree, Grounds.Soil):
                return (False, [])
            if not use_item(Items.Fertilizer):
                quick_print('感染树施肥失败：', position)
                return (False, [])
            if with_companions:
                request = get_companion()
                if request != None and request[1] in primary:
                    request = None
                records.append((position, Entities.Tree, request))
        elif phase == 'weird_harvest':
            if get_entity_type() != Entities.Tree or not pr_wait_until_ready():
                return (False, [])
            if not harvest():
                return (False, [])
        else:
            return (False, [])
    return (True, records)

def pr_weird_cycle():
    if (
        num_unlocked(Unlocks.Fertilizer) == 0
        or num_unlocked(Entities.Tree) == 0
    ):
        print('奇异物质需要先解锁肥料和树。')
        return False
    sites = pr_weird_sites()
    if not pr_wait_for_item(Items.Fertilizer, len(sites)):
        return False
    cleanup, primary = pr_weird_cleanup_jobs(sites)
    with_companions = pr_poly_enabled('weird')
    payload = (sites, primary, with_companions)
    good, results = pr_mp_dispatch(
        'weird_clear',
        len(cleanup),
        'weird',
        cleanup
    )
    if not good:
        return False
    good, results = pr_mp_dispatch(
        'weird_prepare',
        len(sites),
        'weird',
        payload
    )
    if not good:
        return False
    support_jobs = []
    if with_companions:
        records = []
        for result in results:
            for record in result[1]:
                records.append(record)
        supports, protected, spent = pr_poly_plan(
            records,
            pr_POLY_CONTEXT['reserves'],
            'weird'
        )
        for position in supports:
            support_jobs.append((position, supports[position]))
        quick_print('感染树并行伴生：主树', len(sites), '匹配', len(protected), '种子', spent)
        good, results = pr_mp_dispatch(
            'poly_support',
            len(support_jobs),
            'weird',
            support_jobs
        )
        if not good:
            return False
    good, results = pr_mp_dispatch(
        'weird_harvest',
        len(sites),
        'weird',
        payload
    )
    if not good:
        return False
    if len(support_jobs) > 0:
        good, results = pr_mp_dispatch(
            'poly_finish',
            len(support_jobs),
            'weird',
            support_jobs
        )
        if not good:
            return False
    pr_POLY_LAST_METHOD['weird'] = pr_poly_choose('weird')
    return True

def pr_opposite(direction):
    if direction == North:
        return South
    if direction == East:
        return West
    if direction == South:
        return North
    return East

def pr_solve_maze(collect=True):
    target = None
    if pr_MAZE_USE_MEASURE and get_entity_type() == Entities.Hedge:
        target = measure()
    visited = {(get_pos_x(), get_pos_y()): True}
    backtrack = []
    while True:
        if get_entity_type() == Entities.Treasure:
            if collect:
                harvest()
            return True
        advanced = False
        for direction in pr_maze_direction_order(target):
            x = get_pos_x()
            y = get_pos_y()
            if direction == North:
                y += 1
            elif direction == East:
                x += 1
            elif direction == South:
                y -= 1
            else:
                x -= 1
            n = get_world_size()
            if x < 0 or x >= n or y < 0 or (y >= n):
                continue
            if (x, y) in visited:
                continue
            if move(direction):
                visited[get_pos_x(), get_pos_y()] = True
                backtrack.append(pr_opposite(direction))
                advanced = True
                break
        if not advanced:
            if len(backtrack) == 0:
                quick_print('迷宫可达区域已探索完但未找到宝箱；保留现场并停止。')
                return False
            if not move(backtrack.pop()):
                quick_print('迷宫回溯受阻；保留现场并停止。')
                return False

def pr_resume_existing_maze():
    current = get_entity_type()
    if current != Entities.Hedge and current != Entities.Treasure:
        return True
    print('发现未完成迷宫：从当前位置继续寻找宝箱')
    if not pr_solve_maze():
        print('迷宫续跑失败，已保留现场；请查看输出中的具体原因。')
        return False
    current = get_entity_type()
    if current == Entities.Hedge or current == Entities.Treasure:
        print('未确认宝箱已收割、迷宫已结束；保留现场并停止。')
        return False
    quick_print('遗留迷宫已完成，恢复当前模式：', pr_MODE)
    return True

def pr_resource_available(item):
    if item == Items.Hay:
        return True
    if item == Items.Wood:
        return num_unlocked(Entities.Bush) > 0
    if item == Items.Carrot:
        return num_unlocked(Entities.Carrot) > 0
    if item == Items.Pumpkin:
        return num_unlocked(Entities.Pumpkin) > 0
    if item == Items.Power:
        return num_unlocked(Entities.Sunflower) > 0
    if item == Items.Cactus:
        return num_unlocked(Entities.Cactus) > 0
    if item == Items.Bone:
        n = get_world_size()
        return num_unlocked(Hats.Dinosaur_Hat) > 0 and n >= 2 and (n % 2 == 0)
    if item == Items.Weird_Substance:
        return (
            num_unlocked(Unlocks.Fertilizer) > 0
            and num_unlocked(Entities.Tree) > 0
        )
    if item == Items.Gold:
        return num_unlocked(Unlocks.Mazes) > 0
    if item == Items.Water:
        return num_unlocked(Unlocks.Watering) > 0
    if item == Items.Fertilizer:
        return num_unlocked(Unlocks.Fertilizer) > 0
    return False

def pr_add_cost(budget, entity, count):
    cost = get_cost(entity)
    if cost == None:
        quick_print('无法取得成本：', entity)
        return False
    for ingredient in cost:
        if ingredient not in budget:
            budget[ingredient] = 0
        budget[ingredient] += cost[ingredient] * count
    return True

def pr_unlock_amount(table, item):
    if item in table:
        return table[item]
    return 0

def pr_mp_capacity(units):
    if units <= 0:
        return 0
    if not pr_MULTI_ENABLED or num_unlocked(Unlocks.Megafarm) == 0:
        return 1
    available = max_drones() - num_drones() + 1
    if pr_MAX_DRONES > 0 and available > pr_MAX_DRONES:
        available = pr_MAX_DRONES
    if available > units:
        available = units
    if available < 1:
        available = 1
    return available

def pr_mp_ranges(total, workers):
    result = []
    if total <= 0:
        return result
    if workers < 1:
        workers = 1
    if workers > total:
        workers = total
    for i in range(workers):
        result.append((i * total // workers, (i + 1) * total // workers))
    return result

def pr_mp_job(phase, lo, hi, mode, data):

    def task():
        return pr_mp_worker(phase, lo, hi, mode, data)
    return task

def pr_mp_dispatch(phase, total, mode='', data=None):
    ranges = pr_mp_ranges(total, pr_mp_capacity(total))
    if len(ranges) == 0:
        return (True, [])
    results = []
    handles = []
    local_jobs = [0]
    for part in ranges:
        results.append(None)
    if pr_MULTI_VERBOSE:
        quick_print('并行阶段', phase, '计划机数（含主机）', len(ranges))
    for i in range(1, len(ranges)):
        lo, hi = ranges[i]
        handle = spawn_drone(pr_mp_job(phase, lo, hi, mode, data))
        if handle == None:
            local_jobs.append(i)
        else:
            handles.append((i, handle))
    for i in local_jobs:
        lo, hi = ranges[i]
        results[i] = pr_mp_worker(phase, lo, hi, mode, data)
        if results[i] == None or results[i][0] != True:
            break
    for entry in handles:
        results[entry[0]] = wait_for(entry[1])
    good = True
    for result in results:
        if result == None or result[0] != True:
            good = False
    if not good:
        quick_print('并行阶段失败，已等待本阶段分机结束：', phase)
    return (good, results)

def pr_mp_worker(phase, lo, hi, mode, data):
    if phase == 'wood_continuous':
        return (pr_wood_continuous(lo, hi), [])
    if phase in ['weird_clear', 'weird_prepare', 'weird_harvest']:
        return pr_weird_worker(phase, lo, hi, data)
    if phase in ['poly_prepare', 'poly_support', 'poly_primary', 'poly_finish']:
        return pr_poly_worker(phase, lo, hi, mode, data)
    n = get_world_size()
    buckets = []
    if phase == 'sunflower_prepare':
        for i in range(9):
            buckets.append([])
    if phase == 'sunflower_harvest':
        for i in range(lo, hi):
            x, y = data[i]
            pr_go_to(x, y)
            if get_entity_type() != Entities.Sunflower:
                quick_print('向日葵位置被外部改动：', x, y)
                return (False, [])
            if not pr_wait_until_ready():
                return (False, [])
            if not harvest():
                return (False, [])
        return (True, [])
    if phase == 'cactus_rows' or phase == 'cactus_columns':
        vertical = phase == 'cactus_columns'
        for index in range(lo, hi):
            if not pr_cactus_sort_line(index, vertical, False):
                return (False, [])
        return (True, [])
    pending = []
    for x in range(lo, hi):
        pr_go_to(x, 0)
        for y in range(n):
            if phase == 'mud_water':
                if not pr_water_here():
                    return (False, [])
            elif phase == 'mud_check':
                if get_water() <= 0.5:
                    return (False, [])
            elif phase == 'basic_pass' or phase == 'basic_batch':
                entity, ground = pr_basic_target(mode, x, y, n)
                if entity == Entities.Tree or entity == Entities.Bush:
                    ground = Grounds.Soil
                    if get_ground_type() != ground:
                        till()
                if (
                    phase == 'basic_pass'
                    and get_entity_type() == entity
                    and can_harvest()
                ):
                    harvest()
                if not pr_ensure_crop(entity, ground):
                    return (False, [])
            elif phase == 'sunflower_prepare':
                if not pr_ensure_crop(Entities.Sunflower, Grounds.Soil):
                    return (False, [])
                petals = measure()
                if petals == None or petals < 7 or petals > 15:
                    quick_print('向日葵测量异常：', x, y, petals)
                    return (False, [])
                buckets[15 - petals].append((x, y))
            elif phase == 'pumpkin_prepare':
                if not pr_ensure_pumpkin():
                    return (False, [])
                if not can_harvest():
                    pending.append((x, y))
            elif phase == 'cactus_prepare':
                if not pr_ensure_crop(Entities.Cactus, Grounds.Soil):
                    return (False, [])
            elif phase == 'cactus_ready':
                if (
                    get_entity_type() != Entities.Cactus
                    or not pr_wait_until_ready()
                ):
                    return (False, [])
            elif phase == 'empty':
                if get_entity_type() != None:
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
            else:
                quick_print('未知并行工作阶段：', phase)
                return (False, [])
            if y < n - 1:
                move(North)
    if phase == 'basic_batch':
        for x in range(lo, hi):
            pr_go_to(x, 0)
            for y in range(n):
                if not pr_wait_until_ready():
                    return (False, [])
                if not harvest():
                    return (False, [])
                if y < n - 1:
                    move(North)
    elif phase == 'pumpkin_prepare':
        started = get_time()
        while len(pending) > 0:
            if (
                pr_GROW_WAIT_SECONDS > 0
                and get_time() - started >= pr_GROW_WAIT_SECONDS
            ):
                quick_print('南瓜分区补苗等待超时：', lo, hi)
                return (False, [])
            next_pending = []
            for pos in pending:
                pr_go_to(pos[0], pos[1])
                if not pr_ensure_pumpkin():
                    return (False, [])
                if not can_harvest():
                    next_pending.append(pos)
            pending = next_pending
    return (True, buckets)

def pr_wood_continuous(lo, hi):
    n = get_world_size()
    for x in range(lo, hi):
        pr_go_to(x, 0)
        for y in range(n):
            entity, ground = pr_basic_target('wood', x, y, n)
            if not pr_ensure_crop(entity, Grounds.Soil):
                return False
            while get_water() < 0.99:
                if not use_item(Items.Water):
                    return False
            move(North)
    for count in range(64):
        for x in range(lo, hi):
            pr_go_to(x, 0)
            for y in range(n):
                if can_harvest():
                    while get_water() < 0.99:
                        if not use_item(Items.Water):
                            return False
                    if not harvest():
                        return False
                    entity, ground = pr_basic_target('wood', x, y, n)
                    if not plant(entity):
                        return False
                move(North)
    return True

def pr_plain_basic_batch(mode):
    if pr_mp_capacity(get_world_size()) <= 1:
        return pr_serial_basic_batch(mode)
    good, results = pr_mp_dispatch('basic_batch', get_world_size(), mode)
    return good

def pr_pumpkin_cycle():
    if pr_mp_capacity(get_world_size()) <= 1:
        return pr_serial_pumpkin_cycle()
    good, results = pr_mp_dispatch('pumpkin_prepare', get_world_size())
    if not good:
        return False
    pr_go_to(0, 0)
    return harvest()

def pr_cactus_cycle_current():
    if pr_mp_capacity(get_world_size()) <= 1:
        return pr_serial_cactus_cycle()
    for phase in [
        'cactus_prepare',
        'cactus_rows',
        'cactus_columns',
        'cactus_ready'
    ]:
        good, results = pr_mp_dispatch(phase, get_world_size())
        if not good:
            return False
    pr_go_to(0, 0)
    return harvest()

def pr_sunflower_cycle():
    if pr_mp_capacity(get_world_size()) <= 1:
        return pr_serial_sunflower_cycle()
    n = get_world_size()
    good, results = pr_mp_dispatch('sunflower_prepare', n)
    if not good:
        return False
    buckets = []
    for i in range(9):
        buckets.append([])
    for result in results:
        for i in range(9):
            for pos in result[1][i]:
                buckets[i].append(pos)
    keep = pr_SUNFLOWER_KEEP
    if keep < 0 or keep >= n * n:
        keep = 0
    remaining = n * n - keep
    for bucket in buckets:
        if remaining == 0:
            break
        chosen = []
        for pos in bucket:
            if len(chosen) >= remaining:
                break
            chosen.append(pos)
        if len(chosen) == 0:
            continue
        good, ignored = pr_mp_dispatch(
            'sunflower_harvest',
            len(chosen),
            '',
            chosen
        )
        if not good:
            return False
        remaining -= len(chosen)
    return True

def pr_poly_item(mode):
    if mode == 'hay':
        return Items.Hay
    if mode == 'wood' or mode == 'bush':
        return Items.Wood
    if mode == 'carrot':
        return Items.Carrot
    if mode == 'weird':
        return Items.Weird_Substance
    return None

def pr_poly_enabled(mode):
    if pr_POLYCULTURE_ENABLED == False or pr_poly_item(mode) == None:
        return False
    return num_unlocked(Unlocks.Polyculture) > 0

def pr_poly_choose(mode):
    if pr_poly_enabled(mode):
        return 'companion'
    return 'plain'

def pr_poly_plan(records, reserves, mode=''):
    n = get_world_size()
    existing = {}
    compact = []
    for record in records:
        x, y = record[0]
        cell = x * n + y
        existing[cell] = record[1]
        compact.append((cell, record[1], record[2]))
    support_cells, source_cells, spent = pr_poly_plan_compact(
        compact,
        reserves,
        mode,
        existing
    )
    supports = {}
    protected = {}
    for cell in support_cells:
        supports[cell // n, cell % n] = support_cells[cell]
    for cell in source_cells:
        target = source_cells[cell]
        protected[cell // n, cell % n] = (target // n, target % n)
    return (supports, protected, spent)

def pr_poly_plan_compact(records, reserves, mode, existing=None):
    n = get_world_size()
    primary = Entities.Grass
    trees_available = False
    if mode == 'carrot':
        primary = Entities.Carrot
    elif mode == 'bush' or mode == 'wood':
        primary = Entities.Bush
    if mode == 'wood':
        trees_available = num_unlocked(Entities.Tree) > 0
    costs = {}
    for entity in [
        Entities.Grass,
        Entities.Bush,
        Entities.Tree,
        Entities.Carrot
    ]:
        if num_unlocked(entity) > 0:
            cost = get_cost(entity)
            if cost != None:
                costs[entity] = cost
    available = {}
    for entity in costs:
        for item in costs[entity]:
            if item not in available:
                free = num_items(item) - pr_unlock_amount(reserves, item)
                if free < 0:
                    free = 0
                available[item] = free * pr_POLY_SPEND_FRACTION
    supports = {}
    protected = {}
    spent = {}
    for record in records:
        source = record[0]
        request = record[2]
        if request == None or source in supports:
            continue
        wanted, target = request
        x, y = target
        if x < 0 or y < 0 or x >= n or (y >= n):
            continue
        target = x * n + y
        if target == source:
            continue
        if wanted not in costs or target in protected:
            continue
        current = primary
        if existing != None:
            current = None
            if target in existing:
                current = existing[target]
            elif mode == 'wood' and pr_TREE_COMPANION_SCOPE == 'trees':
                current = Entities.Bush
        elif mode == 'wood' and trees_available and pr_tree_site(x, y, n):
            current = Entities.Tree
        if mode == 'wood' or mode == 'weird':
            if current == Entities.Tree:
                continue
            if wanted == Entities.Tree and (not pr_tree_site(x, y, n)):
                continue
        if target in supports:
            if supports[target] == wanted:
                protected[source] = target
            continue
        expense = {}
        if current != wanted:
            expense = costs[wanted]
        affordable = True
        for item in expense:
            if pr_unlock_amount(available, item) < expense[item]:
                affordable = False
                break
        if not affordable:
            continue
        for item in expense:
            available[item] -= expense[item]
            spent[item] = pr_unlock_amount(spent, item) + expense[item]
        supports[target] = wanted
        protected[source] = target
    return (supports, protected, spent)

def pr_poly_plan_fast(records, reserves, mode):
    n = get_world_size()
    wood = mode == 'wood'
    if mode != 'carrot' and (not wood):
        return pr_poly_plan_compact(records, reserves, mode)
    if (
        wood
        and ((
            n
            % 2 == 1
            or pr_TREE_COMPANION_SCOPE != 'trees'
            or num_unlocked(Entities.Tree) == 0
        ))
    ):
        return pr_poly_plan_compact(records, reserves, mode)
    allowed = {}
    for entity in [Entities.Grass, Entities.Bush, Entities.Tree]:
        if num_unlocked(entity) > 0:
            cost = get_cost(entity)
            if cost == None or len(cost) > 0:
                return pr_poly_plan_compact(records, reserves, mode)
            allowed[entity] = True
    carrot_cost = {}
    available = {}
    if wood and num_unlocked(Entities.Carrot) > 0:
        cost = get_cost(Entities.Carrot)
        if cost != None:
            allowed[Entities.Carrot] = True
            carrot_cost = cost
            for item in cost:
                available[item] = (
                    max(0, num_items(item) - pr_unlock_amount(reserves, item))
                    * pr_POLY_SPEND_FRACTION
                )
    supports = {}
    protected = {}
    spent = {}
    for record in records:
        source = record[0]
        request = record[2]
        if request == None or source in supports:
            continue
        if (
            wood
            and ((
                record[1] != Entities.Tree
                or (source // n + source % n)
                % 2 == 1
            ))
        ):
            return pr_poly_plan_compact(records, reserves, mode)
        wanted, position = request
        if not wood and wanted == Entities.Carrot:
            return pr_poly_plan_compact(records, reserves, mode)
        if wanted not in allowed:
            continue
        x, y = position
        if x < 0 or y < 0 or x >= n or (y >= n):
            continue
        if wood and ((x + y) % 2 == 0 or wanted == Entities.Tree):
            continue
        target = x * n + y
        if target == source or target in protected:
            continue
        if target in supports:
            if supports[target] == wanted:
                protected[source] = target
            continue
        if wood and wanted == Entities.Carrot:
            affordable = True
            for item in carrot_cost:
                if available[item] < carrot_cost[item]:
                    affordable = False
                    break
            if not affordable:
                continue
            for item in carrot_cost:
                available[item] -= carrot_cost[item]
                spent[item] = pr_unlock_amount(spent, item) + carrot_cost[item]
        supports[target] = wanted
        protected[source] = target
    return (supports, protected, spent)

def pr_poly_support_jobs(supports, n):
    jobs = []
    for x in range(n):
        ys = range(n)
        if x % 2 == 1:
            ys = range(n - 1, -1, -1)
        base = x * n
        for y in ys:
            cell = base + y
            if cell in supports:
                jobs.append(((x, y), supports[cell]))
    return jobs

def pr_poly_stage_record(phase, started, tick_started, good):
    row = {
        'phase': phase,
        'seconds': get_time() - started,
        'ticks': get_tick_count() - tick_started,
        'good': good
    }
    pr_POLY_CONTEXT['last_batch']['stages'].append(row)
    if pr_PERF_VERBOSE:
        quick_print(
            '伴生阶段',
            phase,
            '游戏秒',
            row['seconds'],
            '主机ticks',
            row['ticks'],
            '成功',
            good
        )

def pr_poly_worker(phase, lo, hi, mode, data):
    n = get_world_size()
    trees_available = False
    if mode == 'wood':
        trees_available = num_unlocked(Entities.Tree) > 0
    if phase == 'poly_prepare':
        records = []
        for x in range(lo, hi):
            pr_go_to(x, 0)
            for y in range(n):
                if mode == 'wood':
                    entity = Entities.Bush
                    if trees_available and pr_tree_site(x, y, n):
                        entity = Entities.Tree
                else:
                    entity, ground = pr_basic_target(mode, x, y, n)
                if get_ground_type() != Grounds.Soil:
                    till()
                if not pr_ensure_crop(entity, Grounds.Soil):
                    return (False, [])
                if (
                    mode != 'wood'
                    or pr_TREE_COMPANION_SCOPE == 'all'
                    or (not trees_available)
                    or (entity == Entities.Tree)
                ):
                    position = (x, y)
                    if data == True:
                        position = x * n + y
                    records.append((position, entity, get_companion()))
                if y < n - 1:
                    move(North)
        return (True, records)
    if phase == 'poly_support':
        for i in range(lo, hi):
            position, entity = data[i]
            pr_go_to(position[0], position[1])
            if get_entity_type() != entity:
                if get_ground_type() != Grounds.Soil:
                    till()
                if not pr_ensure_crop(entity, Grounds.Soil):
                    return (False, [])
            elif not pr_water_here():
                return (False, [])
        return (True, [])
    if phase == 'poly_primary':
        for x in range(lo, hi):
            pr_go_to(x, 0)
            base = x * n
            for y in range(n):
                if base + y not in data:
                    if mode == 'wood':
                        entity = Entities.Bush
                        if trees_available and pr_tree_site(x, y, n):
                            entity = Entities.Tree
                    else:
                        entity, ground = pr_basic_target(mode, x, y, n)
                    if get_entity_type() != entity or not pr_wait_until_ready():
                        return (False, [])
                    if not harvest():
                        return (False, [])
                if y < n - 1:
                    move(North)
        return (True, [])
    if phase == 'poly_finish':
        for i in range(lo, hi):
            position, entity = data[i]
            pr_go_to(position[0], position[1])
            if get_entity_type() != entity or not pr_wait_until_ready():
                return (False, [])
            if not harvest():
                return (False, [])
        return (True, [])
    return (False, [])

def pr_polyculture_batch(mode):
    if not pr_poly_enabled(mode):
        return pr_plain_basic_batch(mode)
    n = get_world_size()
    pr_POLY_CONTEXT['last_batch'] = {'mode': mode, 'good': False, 'stages': []}
    started = get_time()
    tick_started = get_tick_count()
    good, results = pr_mp_dispatch('poly_prepare', n, mode, True)
    pr_poly_stage_record('prepare', started, tick_started, good)
    if not good:
        return False
    started = get_time()
    tick_started = get_tick_count()
    records = []
    for result in results:
        for record in result[1]:
            records.append(record)
    supports, protected, spent = pr_poly_plan_fast(
        records,
        pr_POLY_CONTEXT['reserves'],
        mode
    )
    support_jobs = pr_poly_support_jobs(supports, n)
    pr_poly_stage_record('plan', started, tick_started, True)
    pr_POLY_CONTEXT['last_batch']['matched'] = len(protected)
    pr_POLY_CONTEXT['last_batch']['support_count'] = len(supports)
    pr_POLY_CONTEXT['last_batch']['spent'] = spent
    quick_print(
        '伴生计划：主作物',
        mode,
        '匹配',
        len(protected),
        '伴生位置',
        len(supports),
        '额外种子预算',
        spent
    )
    started = get_time()
    tick_started = get_tick_count()
    good, results = pr_mp_dispatch(
        'poly_support',
        len(support_jobs),
        mode,
        support_jobs
    )
    pr_poly_stage_record('support', started, tick_started, good)
    if not good:
        return False
    started = get_time()
    tick_started = get_tick_count()
    good, results = pr_mp_dispatch('poly_primary', n, mode, supports)
    pr_poly_stage_record('primary', started, tick_started, good)
    if not good:
        return False
    started = get_time()
    tick_started = get_tick_count()
    good, results = pr_mp_dispatch(
        'poly_finish',
        len(support_jobs),
        mode,
        support_jobs
    )
    pr_poly_stage_record('finish', started, tick_started, good)
    pr_POLY_CONTEXT['last_batch']['good'] = good
    return good

def pr_dino_index(n, x, y):
    if y == 0:
        if x == 0:
            return 0
        return n * n - x
    if x % 2 == 0:
        return x * (n - 1) + y
    return (x + 1) * (n - 1) + 1 - y
pr_DINO_PLAN = {'key': None, 'data': None}

def pr_dino_plan(n, shortcuts):
    key = (n, shortcuts)
    if pr_DINO_PLAN['key'] == key:
        return pr_DINO_PLAN['data']
    route = []
    for x in range(n):
        if x % 2 == 0:
            count = n - 2
            if x == 0:
                count = n - 1
            for i in range(count):
                route.append(North)
            route.append(East)
        else:
            for i in range(n - 2):
                route.append(South)
            if x == n - 1:
                route.append(South)
                for i in range(n - 1):
                    route.append(West)
            else:
                route.append(East)
    total = n * n
    options = []
    if shortcuts:
        for i in range(total):
            options.append(None)
    pr_DINO_PLAN['key'] = key
    pr_DINO_PLAN['data'] = (route, options)
    return pr_DINO_PLAN['data']

def pr_dino_options(n, x, y, here):
    total = n * n
    result = []
    for d, dx, dy in [
        (North, 0, 1),
        (East, 1, 0),
        (South, 0, -1),
        (West, -1, 0)
    ]:
        nx = x + dx
        ny = y + dy
        if 0 <= nx < n and 0 <= ny < n:
            destination = pr_dino_index(n, nx, ny)
            distance = (destination - here) % total
            if 1 < distance < total - 1:
                result.append((distance, d, destination))
    return result

def pr_dino_cycle_fast(n, apple_limit, shortcut_fill=0.27):
    shortcuts = n >= 8 and shortcut_fill > 0
    route, options = pr_dino_plan(n, shortcuts)
    total = n * n
    at = pr_dino_index(n, get_pos_x(), get_pos_y())
    eaten = 0
    moves = 0
    history = []
    cutoff = 0
    if shortcuts:
        cutoff = min(apple_limit, n * n * shortcut_fill)
        for i in range(total):
            history.append(at)
    while eaten < apple_limit:
        if get_entity_type() != Entities.Apple:
            return (False, eaten, moves)
        following = measure()
        last = following == None or eaten + 1 >= apple_limit
        steps = 1
        if not last:
            nx, ny = following
            if nx < 0 or nx >= n or ny < 0 or (ny >= n):
                return (False, eaten, moves)
            steps = (pr_dino_index(n, nx, ny) - at) % total
            if steps == 0:
                return (False, eaten, moves)
        stop = at + steps
        if eaten < cutoff and (not last):
            target = stop % total
            growing = True
            while at != target:
                free = total
                if eaten > 0:
                    free = (history[(moves - eaten) % total] - at) % total
                reach = min((target - at) % total, free - 9)
                direction = route[at]
                next_at = (at + 1) % total
                best = 1
                if options[at] == None:
                    options[at] = pr_dino_options(
                        n,
                        get_pos_x(),
                        get_pos_y(),
                        at
                    )
                for distance, candidate, destination in options[at]:
                    if best < distance <= reach:
                        best = distance
                        direction = candidate
                        next_at = destination
                if not move(direction):
                    return (False, eaten, moves)
                history[moves % total] = at
                moves += 1
                at = next_at
                if growing:
                    eaten += 1
                    growing = False
            continue
        end = min(stop, total)
        for i in range(at, end):
            if not move(route[i]):
                return (False, eaten, moves + i - at)
        if stop > total:
            for i in range(stop - total):
                if not move(route[i]):
                    return (False, eaten, moves + total - at + i)
        at = stop % total
        moves += steps
        eaten += 1
        if last:
            break
    return (True, eaten, moves)

def pr_maze_direction_order(target):
    if target == None:
        return [North, East, South, West]
    dx = target[0] - get_pos_x()
    dy = target[1] - get_pos_y()
    horizontal = East
    vertical = North
    if dx < 0:
        horizontal = West
    if dy < 0:
        vertical = South
    if abs(dx) > abs(dy):
        return [
            horizontal,
            vertical,
            pr_opposite(vertical),
            pr_opposite(horizontal)
        ]
    return [
        vertical,
        horizontal,
        pr_opposite(horizontal),
        pr_opposite(vertical)
    ]

def pr_cactus_sort_line(index, vertical, descending=False):
    n = get_world_size()
    if vertical:
        pr_go_to(index, 0)
        backward = South
    else:
        pr_go_to(0, index)
        backward = West
    first = measure()
    if first == None:
        return False
    values = [first]
    for i in range(1, n):
        if vertical:
            pr_go_to(index, i)
        else:
            pr_go_to(i, index)
        value = measure()
        if value == None:
            return False
        values.append(value)
        k = i
        while k > 0:
            previous = values[k - 1]
            if descending:
                if previous >= value:
                    break
            elif previous <= value:
                break
            if not swap(backward) or not move(backward):
                return False
            values[k] = previous
            k -= 1
        values[k] = value
    return True
ach_ACH_SMALL_FIELDS = True
ach_HELPERS = {'need': None, 'budget': None}

def ach_ensure_resource(item, amount, trail):
    if item in [Items.Water, Items.Fertilizer]:
        return pr_wait_for_item(item, amount)
    return ach_HELPERS['need'](item, amount, {}, trail)

def ach_batch_budget(item, missing):
    return ach_HELPERS['budget'](item)

def ach_achievement_apply(fn):
    return fn()

def ach_achievement_callback():
    return True

def ach_achievement_higher_order():
    return ach_achievement_apply(ach_achievement_callback)

def ach_achievement_pig():
    pet_the_piggy()
    return True

def ach_achievement_healer():
    if num_unlocked(Unlocks.Fertilizer) == 0:
        quick_print('跳过妙手回春：尚未解锁肥料。')
        return False
    if not ach_ensure_resource(Items.Fertilizer, 1, []):
        return False
    if not ach_ensure_resource(Items.Weird_Substance, 1, []):
        return False
    if get_ground_type() != Grounds.Soil:
        till()
    if get_entity_type() != None:
        harvest()
    if not plant(Entities.Grass):
        return False
    if not use_item(Items.Fertilizer):
        return False
    if not use_item(Items.Weird_Substance):
        return False
    return True

def ach_achievement_hat_job(hat, deadline):

    def worker():
        change_hat(hat)
        while get_time() < deadline:
            do_a_flip()
        change_hat(Hats.Straw_Hat)
        return True
    return worker

def ach_achievement_fashion():
    if num_unlocked(Unlocks.Megafarm) == 0 or max_drones() < 5:
        quick_print('跳过时装秀：需至少5个无人机名额。')
        return False
    hats = []
    for hat in Hats:
        if hat != Hats.Dinosaur_Hat and num_unlocked(hat) > 0:
            hats.append(hat)
        if len(hats) == 5:
            break
    if len(hats) < 5:
        quick_print('跳过时装秀：不足5顶已解锁的不同帽子。')
        return False
    deadline = get_time() + 30
    handles = []
    change_hat(hats[0])
    good = True
    for i in range(1, 5):
        h = spawn_drone(ach_achievement_hat_job(hats[i], deadline))
        if h == None:
            good = False
            break
        handles.append(h)
    if num_drones() < 5 or get_time() >= deadline - 2:
        good = False
    while get_time() < deadline:
        do_a_flip()
    for handle in handles:
        wait_for(handle)
    change_hat(Hats.Straw_Hat)
    return good

def ach_achievement_swarm():
    if num_unlocked(Unlocks.Megafarm) == 0 or max_drones() < 32:
        quick_print('跳过蜂群：还没有32个无人机名额。')
        return False
    deadline = get_time() + 40
    handles = []
    good = True
    for i in range(31):
        handle = spawn_drone(ach_achievement_hat_job(Hats.Straw_Hat, deadline))
        if handle == None:
            good = False
            break
        handles.append(handle)
    if num_drones() != 32:
        good = False
    while get_time() < deadline:
        do_a_flip()
    for handle in handles:
        wait_for(handle)
    return good

def ach_achievement_mud():
    global pr_MAX_DRONES
    global pr_WATER_TARGET
    if num_unlocked(Unlocks.Watering) == 0:
        return False
    n = get_world_size()
    limit = pr_MAX_DRONES
    target = pr_WATER_TARGET
    pr_MAX_DRONES = 0
    pr_WATER_TARGET = 0.95
    good = False
    for attempt in range(3):
        good, ignored = pr_mp_dispatch('mud_water', n)
        if not good:
            break
        good, ignored = pr_mp_dispatch('mud_check', n)
        if good:
            break
    pr_MAX_DRONES = limit
    pr_WATER_TARGET = target
    if not good:
        quick_print('泥泞农场未确认：补水/蒸发速度不足，停止重复消耗。')
    return good

def ach_achievement_wrong_order_current():
    if num_unlocked(Entities.Cactus) == 0:
        return False
    n = get_world_size()
    budget = ach_batch_budget(Items.Cactus, 0)
    if budget == None:
        return False
    for item in budget:
        if not ach_ensure_resource(item, budget[item], []):
            return False
    good, results = pr_mp_dispatch('cactus_prepare', n)
    if not good:
        return False
    for y in range(n):
        for x in range(1, n):
            pr_go_to(x, y)
            k = x
            while k > 0:
                if measure(West) >= measure():
                    break
                if not swap(West) or not move(West):
                    return False
                k -= 1
    for x in range(n):
        for y in range(1, n):
            pr_go_to(x, y)
            k = y
            while k > 0:
                if measure(South) >= measure():
                    break
                if not swap(South) or not move(South):
                    return False
                k -= 1
    good, results = pr_mp_dispatch('cactus_ready', n)
    if not good:
        return False
    for x in range(n):
        for y in range(n):
            pr_go_to(x, y)
            value = measure()
            if x < n - 1 and value < measure(East):
                return False
            if y < n - 1 and value < measure(North):
                return False
    do_a_flip()
    return True

def ach_achievement_stack_overflow():
    return ach_achievement_stack_overflow()

def ach_achievement_wrong_order_action():
    if not ach_ACH_SMALL_FIELDS:
        return ach_achievement_wrong_order_current()
    if num_unlocked(Entities.Cactus) == 0:
        return False
    original = get_world_size()
    if original > 3 and num_unlocked(Unlocks.Debug_2) == 0:
        print('跳过你搞错了：请先解锁缩田能力，不在大田里慢慢排成就。')
        return False
    cost = get_cost(Entities.Cactus)
    if cost == None:
        return False
    target = min(3, original)
    for item in cost:
        if num_items(item) < cost[item] * target * target:
            print('成就缺少9株以内的仙人掌种子原料：', item)
            return False
    if target != original:
        set_world_size(target)
        if get_world_size() != target:
            set_world_size(original)
            return False
    good = ach_achievement_wrong_order_current()
    if good:
        pr_go_to(0, target - 1)
        good = harvest()
    if target != original:
        set_world_size(original)
    return good

def ach_achievement_recycling_action():
    if num_unlocked(Unlocks.Mazes) == 0:
        print('循环利用需要先解锁迷宫。')
        return False
    original = get_world_size()
    size = min(3, original)
    if size < 3 or (size != original and num_unlocked(Unlocks.Debug_2) == 0):
        print('循环利用需要至少3格边长和缩田能力。')
        return False
    unit = size * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    if num_items(Items.Weird_Substance) < unit * 301:
        print('循环利用缺奇异物质：需要', unit * 301, '。先备齐再运行。')
        return False
    if size != original:
        set_world_size(size)
        if get_world_size() != size:
            set_world_size(original)
            return False
    pr_go_to(0, 0)
    good = (
        ach_maze_clear_here()
        and plant(Entities.Bush)
        and use_item(Items.Weird_Substance, unit)
    )
    completed = 0
    if good:
        for i in range(300):
            if (
                not pr_solve_maze(False)
                or not use_item(Items.Weird_Substance, unit)
            ):
                good = False
                break
            completed += 1
    entity = get_entity_type()
    if entity == Entities.Hedge or entity == Entities.Treasure:
        if not pr_solve_maze():
            return False
    if size != original:
        set_world_size(original)
    quick_print('循环利用：同一座3x3迷宫的成功复用调用', completed, '；以Steam实际成就记录为准。')
    return good and completed == 300

def ach_maze_clear_here():
    entity = get_entity_type()
    if entity == Entities.Hedge or entity == Entities.Treasure:
        return False
    if get_ground_type() != Grounds.Soil:
        till()
    if get_entity_type() != None:
        harvest()
    return pr_water_here()

def ach_achievement_wrong_order():
    if (
        num_unlocked(Entities.Cactus) == 0
        or (get_world_size() > 3 and num_unlocked(Unlocks.Debug_2) == 0)
    ):
        return ach_achievement_wrong_order_action()
    cost = get_cost(Entities.Cactus)
    if cost == None:
        return False
    count = min(3, get_world_size()) ** 2
    for item in cost:
        if not ach_ensure_resource(item, cost[item] * count, []):
            return False
    return ach_achievement_wrong_order_action()

def ach_achievement_recycling():
    if num_unlocked(Unlocks.Mazes) == 0:
        return ach_achievement_recycling_action()
    amount = (
        min(3, get_world_size())
        * 301
        * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    )
    if not ach_ensure_resource(Items.Weird_Substance, amount, []):
        return False
    return ach_achievement_recycling_action()

def ach_run(task, include_optional, material_need, budget_fn):
    ach_HELPERS['need'] = material_need
    ach_HELPERS['budget'] = budget_fn
    jobs = {
        'higher_order': ach_achievement_higher_order,
        'pig': ach_achievement_pig,
        'healer': ach_achievement_healer,
        'fashion': ach_achievement_fashion,
        'swarm': ach_achievement_swarm,
        'mud': ach_achievement_mud,
        'wrong_order': ach_achievement_wrong_order,
        'recycling': ach_achievement_recycling
    }
    if task in jobs:
        result = jobs[task]()
        quick_print('成就动作：', task, '完成/条件不足：', result, '；以游戏成就记录为准。')
        return result
    if task not in ['safe', 'all', 'stack']:
        return False
    good = True
    if task != 'stack':
        for name in jobs:
            if not include_optional and name in ['swarm', 'mud']:
                continue
            result = jobs[name]()
            quick_print('成就动作：', name, '完成/条件不足：', result, '；以游戏成就记录为准。')
            if not result:
                good = False
        if task == 'safe':
            return good
    print('接下来故意触发栈溢出；递归红字是所选成就动作。')
    return ach_achievement_stack_overflow()
STATE = {
    'deferred': None,
    'required': 0,
    'target': None,
    'blocked': [],
    'rounds': 0,
    'reserve': {},
    'burst': (None, 0, 0),
    'layout': None,
    'reset': False
}
CROPS = {
    Items.Hay: Entities.Grass,
    Items.Wood: Entities.Bush,
    Items.Carrot: Entities.Carrot,
    Items.Pumpkin: Entities.Pumpkin,
    Items.Power: Entities.Sunflower,
    Items.Cactus: Entities.Cactus,
    Items.Bone: Entities.Apple,
    Items.Weird_Substance: Entities.Tree,
    Items.Gold: Entities.Bush
}

def budget(item):
    n = get_world_size()
    mode = ''
    if item == Items.Hay:
        mode = 'hay'
    if item == Items.Wood:
        mode = 'wood'
        if MODE == 'bush':
            mode = 'bush'
    if item == Items.Carrot:
        mode = 'carrot'
    if item == Items.Weird_Substance:
        mode = 'weird'
    if peak_enabled(mode):
        return peak_budget(mode)
    if focus_enabled(mode) and mode != 'wood':
        return focus_budget(mode)
    if item == Items.Bone:
        n -= n % 2
    count = n * n
    result = {}
    if item not in CROPS:
        return None
    if item == Items.Wood:
        trees = 0
        if MODE != 'bush' and num_unlocked(Entities.Tree) > 0:
            trees = pr_tree_slot_count(n)
        if trees > 0 and (not pr_add_cost(result, Entities.Tree, trees)):
            return None
        count -= trees
    if item == Items.Pumpkin:
        count *= 3
        if FAST and n >= 28 and (pr_mp_capacity(n) >= 32):
            count = 16 * 36 * 128
    if item == Items.Power and FAST and (n >= 16):
        count *= 65
    if item == Items.Bone:
        count -= 1
    if item == Items.Weird_Substance:
        count = len(pr_weird_sites())
        result[Items.Fertilizer] = count
    if item == Items.Gold:
        count = 1
        result[Items.Weird_Substance] = (
            n
            * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
        )
        if FAST and n >= 10:
            workers, unit, rounds = gold_settings()
            count = workers
            result[Items.Weird_Substance] = (
                workers
                * unit
                * (rounds + (rounds + 299) // 300)
            )
    if not pr_add_cost(result, CROPS[item], count):
        return None
    return result

def usable(item, path):
    if item in path or not available(item):
        return False
    if item in [Items.Water, Items.Fertilizer, Items.Hay, Items.Wood]:
        return True
    costs = budget(item)
    if costs == None:
        return False
    for ingredient in costs:
        if (
            costs[ingredient] > num_items(ingredient)
            and (not usable(ingredient, path + [item]))
        ):
            return False
    return True

def available(item):
    if item == Items.Bone:
        n = get_world_size()
        return (
            num_unlocked(Hats.Dinosaur_Hat) > 0
            and n >= 4
            and (n % 2 == 0 or num_unlocked(Unlocks.Debug_2) > 0)
        )
    return pr_resource_available(item)

def need(item, amount, reserves, path, progress=None):
    stagnant = 0
    if progress != None:
        stagnant = progress['stagnant']
    while num_items(item) < amount:
        if item in [Items.Water, Items.Fertilizer]:
            STATE['deferred'] = item
            STATE['required'] = amount
            return False
        before = num_items(item)
        if not make(item, reserves, path):
            return False
        if num_items(item) <= before:
            stagnant += 1
            if stagnant >= 3:
                quick_print('备料连续三批无净增，停止：', item)
                return False
        else:
            stagnant = 0
        if progress != None:
            progress['stagnant'] = stagnant
    return True

def make(item, reserves, path):
    if item in path or not available(item):
        quick_print('资源依赖循环或生产能力不可用：', item)
        return False
    costs = budget(item)
    if costs == None:
        return False
    held = {}
    for ingredient in reserves:
        held[ingredient] = reserves[ingredient]
    for ingredient in costs:
        held[ingredient] = (
            pr_unlock_amount(held, ingredient)
            + costs[ingredient]
            * 1.25
        )
    for ingredient in [Items.Water, Items.Fertilizer]:
        required = pr_unlock_amount(held, ingredient)
        if ingredient == Items.Water and pr_WATER_ENABLED and (required < 1):
            required = 1
        if num_items(ingredient) < required:
            STATE['deferred'] = ingredient
            STATE['required'] = required
            return False
    for attempt in range(30):
        ready = True
        if (
            item in [Items.Hay, Items.Wood]
            and item in costs
            and (num_items(item) < held[item])
        ):
            STATE['layout'] = None
            mode = 'hay'
            if item == Items.Wood:
                mode = 'wood'
                if MODE == 'bush':
                    mode = 'bush'
            return pr_plain_basic_batch(mode)
        for ingredient in costs:
            amount = held[ingredient]
            if num_items(ingredient) < amount:
                ready = False
                if not need(ingredient, amount, held, path + [item]):
                    return False
        if ready:
            pr_POLY_CONTEXT['reserves'] = held
            STATE['reserve'] = reserves
            return produce(item)
    quick_print('备料反复消耗，停止：', item)
    return False

def produce(item):
    mode = {
        Items.Hay: 'hay',
        Items.Wood: 'wood',
        Items.Carrot: 'carrot',
        Items.Weird_Substance: 'weird'
    }
    if item in mode and MODE != 'bush' and peak_enabled(mode[item]):
        return peak_batch(mode[item], STATE['reserve'])
    previous_layout = STATE['layout']
    STATE['layout'] = None
    if item == Items.Hay:
        if focus_enabled('hay'):
            return focus_batch('hay', STATE['reserve'])
        return pr_polyculture_batch('hay')
    if item == Items.Wood:
        if MODE == 'bush':
            if focus_enabled('bush'):
                return focus_batch('bush', STATE['reserve'])
            return pr_polyculture_batch('bush')
        if focus_enabled('wood'):
            good, ignored = pr_mp_dispatch('wood_continuous', get_world_size())
            return good
        return pr_polyculture_batch('wood')
    if item == Items.Carrot:
        if focus_enabled('carrot'):
            return focus_batch('carrot', STATE['reserve'])
        return pr_polyculture_batch('carrot')
    if item == Items.Power:
        if FAST and get_world_size() >= 16:
            return power_batch()
        return pr_sunflower_cycle()
    if item == Items.Pumpkin:
        if (
            FAST
            and get_world_size() >= 28
            and (pr_mp_capacity(get_world_size()) >= 32)
        ):
            return pumpkin_patch_batch(64)
        return pr_pumpkin_cycle()
    if item == Items.Cactus:
        return pr_cactus_cycle_current()
    if item == Items.Weird_Substance:
        return pr_weird_cycle()
    if item == Items.Bone:
        original = get_world_size()
        n = original - original % 2
        change_hat(Hats.Straw_Hat)
        if n != original:
            set_world_size(n)
            if get_world_size() != n:
                set_world_size(original)
                return False
        if previous_layout != ('dinosaur', n) or n != original:
            good, ignored = pr_mp_dispatch('empty', n)
            if not good:
                if n != original:
                    set_world_size(original)
                return False
        pr_go_to(0, 0)
        pr_dino_plan(n, n >= 8)
        change_hat(Hats.Dinosaur_Hat)
        quick_print('恐龙：开始收集苹果。')
        good, eaten, moves = pr_dino_cycle_fast(n, n * n - 1)
        before = num_items(Items.Bone)
        tick = get_time()
        change_hat(Hats.Straw_Hat)
        STATE['burst'] = (
            Items.Bone,
            num_items(Items.Bone) - before,
            get_time() - tick
        )
        if n != original:
            set_world_size(original)
        elif good and eaten > 0:
            STATE['layout'] = ('dinosaur', n)
        return good and eaten > 0
    if item == Items.Gold:
        if FAST and get_world_size() >= 10:
            return gold_batch()
        pr_go_to(0, 0)
        if not pr_ensure_crop(Entities.Bush, Grounds.Soil):
            return False
        amount = get_world_size() * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
        if not use_item(Items.Weird_Substance, amount):
            return False
        if get_entity_type() not in [Entities.Hedge, Entities.Treasure]:
            return False
        return pr_solve_maze()
    return False

def focus_enabled(mode):
    if not FAST or not COMPANIONS or mode not in [
        'hay',
        'wood',
        'bush',
        'carrot'
    ]:
        return False
    if get_world_size() < 16 or num_unlocked(Unlocks.Polyculture) == 0:
        return False
    if mode == 'carrot':
        fuel = get_world_size() // 4 * (get_world_size() // 8) * 128
        if (
            not FERTILIZE
            or min(
                num_items(Items.Fertilizer),
                num_items(Items.Weird_Substance)
            ) < fuel
        ):
            return False
    for entity in [Entities.Bush, Entities.Tree, Entities.Carrot]:
        if num_unlocked(entity) == 0:
            return False
    return True

def peak_enabled(mode):
    check = mode
    if mode == 'weird':
        check = 'wood'
    if not focus_enabled(check) or mode == 'bush':
        return False
    if mode == 'hay':
        return True
    if mode == 'weird':
        return (
            FERTILIZE
            and num_items(Items.Fertilizer) >= get_world_size()
            // 4
            * (get_world_size() // 8)
            * 128
        )
    return (
        FERTILIZE
        and boost_quota(
            {},
            get_world_size() // 4 * (get_world_size() // 8)
        ) >= 128
    )

def peak_kind(mode, x, y):
    if x % 4 == 1 and y % 8 == 3:
        return None
    kinds = [Entities.Grass, Entities.Bush, Entities.Carrot]
    if mode == 'carrot':
        kinds = [Entities.Grass, Entities.Bush, Entities.Tree]
    return kinds[(x + 2 * y) % 3]

def peak_budget(mode):
    n = get_world_size()
    count = n // 4 * (n // 8) * 64
    costs = {}
    if mode == 'hay':
        for entity in [
            Entities.Grass,
            Entities.Bush,
            Entities.Tree,
            Entities.Carrot
        ]:
            if not pr_add_cost(costs, entity, count):
                return None
        return costs
    if STATE['layout'] != (mode, n):
        for entity in [
            Entities.Grass,
            Entities.Bush,
            Entities.Tree,
            Entities.Carrot
        ]:
            if not pr_add_cost(costs, entity, n * n):
                return None
    entity = Entities.Tree
    if mode == 'carrot':
        entity = Entities.Carrot
    if not pr_add_cost(costs, entity, count * 64):
        return None
    if mode == 'weird':
        costs[Items.Fertilizer] = count * 2
    return costs

def peak_worker(lo, hi, mode, phase, reserves, fuel):
    n = get_world_size()
    if phase == 'prepare':
        for x in range(lo, hi):
            pr_go_to(x, 0)
            for y in range(n):
                kind = peak_kind(mode, x, y)
                if kind != None:
                    if get_entity_type() != None:
                        harvest()
                    if get_ground_type() != Grounds.Soil:
                        till()
                    if not plant(kind):
                        return False
                move(North)
        return True
    entity = Entities.Tree
    if mode == 'hay':
        entity = Entities.Grass
    if mode == 'carrot':
        entity = Entities.Carrot
    for zone in range(lo, hi):
        x = zone // (n // 8) * 4 + 1
        y = zone % (n // 8) * 8 + 3
        pr_go_to(x, y)
        for count in range(64):
            for attempt in range(64):
                if get_entity_type() != None:
                    while get_water() < 0.99:
                        if not use_item(Items.Water):
                            return False
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                if not plant(entity):
                    return False
                want = get_companion()
                if want == None:
                    return False
                kind, (cx, cy) = want
                if mode == 'hay':
                    if cx % 4 != 1 or cy % 8 != 3:
                        break
                elif peak_kind(mode, cx, cy) == kind:
                    break
            while get_water() < 0.99:
                if not use_item(Items.Water):
                    return False
            if mode == 'hay' and (cx % 4 != 1 or cy % 8 != 3):
                pr_go_to(cx, cy)
                if get_entity_type() != kind:
                    if get_entity_type() != None:
                        harvest()
                    if get_ground_type() != Grounds.Soil:
                        till()
                    plant(kind)
                pr_go_to(x, y)
            started = get_time()
            if mode == 'weird':
                if (
                    fuel <= 0
                    or num_items(Items.Fertilizer) <= pr_unlock_amount(
                        reserves,
                        Items.Fertilizer
                    )
                    or (not use_item(Items.Fertilizer))
                ):
                    return False
                fuel -= 1
            while not can_harvest():
                if get_time() - started >= 600:
                    return False
                if (
                    FERTILIZE
                    and fuel > 0
                    and (num_items(Items.Fertilizer) > pr_unlock_amount(
                        reserves,
                        Items.Fertilizer
                    ))
                    and ((
                        mode == 'weird'
                        or num_items(Items.Weird_Substance) > pr_unlock_amount(
                            reserves,
                            Items.Weird_Substance
                        )
                    ))
                ):
                    if use_item(Items.Fertilizer):
                        if (
                            mode != 'weird'
                            and (not use_item(Items.Weird_Substance))
                        ):
                            return False
                        fuel -= 1
            if not harvest():
                return False
    return True

def peak_job(lo, hi, mode, phase, reserves, fuel):

    def work():
        return peak_worker(lo, hi, mode, phase, reserves, fuel)
    return work

def peak_dispatch(mode, phase, reserves):
    n = get_world_size()
    total = n // 4 * (n // 8)
    if phase == 'prepare':
        total = n
    ranges = pr_mp_ranges(total, pr_mp_capacity(total))
    fuel = boost_quota(reserves, len(ranges))
    if mode == 'weird':
        fuel = max(
            0,
            (
                (num_items(Items.Fertilizer) - pr_unlock_amount(
                    reserves,
                    Items.Fertilizer
                ))
                // len(ranges)
            )
        )
    handles = []
    local = [ranges[0]]
    for lo, hi in ranges[1:]:
        handle = spawn_drone(peak_job(lo, hi, mode, phase, reserves, fuel))
        if handle == None:
            local.append((lo, hi))
        else:
            handles.append(handle)
    good = True
    for lo, hi in local:
        if not peak_worker(lo, hi, mode, phase, reserves, fuel):
            good = False
            break
    for handle in handles:
        if wait_for(handle) != True:
            good = False
    return good

def peak_batch(mode, reserves):
    key = (mode, get_world_size())
    if mode != 'hay' and STATE['layout'] != key:
        STATE['layout'] = None
        if not peak_dispatch(mode, 'prepare', reserves):
            return False
    STATE['layout'] = key
    good = peak_dispatch(mode, 'harvest', reserves)
    if not good:
        STATE['layout'] = None
    return good

def pumpkin_patch_rows(lo, hi, by, deadline):
    pending = []
    for x in range(lo, hi):
        pr_go_to(x, by)
        for y in range(by, by + 6):
            kind = get_entity_type()
            if kind != Entities.Pumpkin:
                if kind != None and kind != Entities.Dead_Pumpkin:
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                if not plant(Entities.Pumpkin):
                    return False
                while get_water() < 0.99:
                    if not use_item(Items.Water):
                        return False
            if not can_harvest():
                pending.append((x, y))
            if y + 1 < by + 6:
                move(North)
    while len(pending) > 0:
        if get_time() > deadline + 600:
            return False
        remain = []
        for x, y in pending:
            pr_go_to(x, y)
            if get_entity_type() == Entities.Dead_Pumpkin:
                if not plant(Entities.Pumpkin):
                    return False
            if not can_harvest():
                remain.append((x, y))
        pending = remain
    return True

def pumpkin_patch_rows_job(lo, hi, by, deadline):

    def work():
        return pumpkin_patch_rows(lo, hi, by, deadline)
    return work

def pumpkin_patch_leader(index, deadline):
    bx = index // 4 * 7
    by = index % 4 * 7
    while True:
        handle = spawn_drone(pumpkin_patch_rows_job(
            bx + 3,
            bx + 6,
            by,
            deadline
        ))
        good = pumpkin_patch_rows(bx, bx + 3, by, deadline)
        if handle == None:
            if not pumpkin_patch_rows(bx + 3, bx + 6, by, deadline):
                good = False
        elif wait_for(handle) != True:
            good = False
        if not good:
            return False
        pr_go_to(bx, by)
        if not harvest():
            return False
        if get_time() >= deadline:
            return True

def pumpkin_patch_job(index, deadline):

    def work():
        return pumpkin_patch_leader(index, deadline)
    return work

def pumpkin_patch_batch(seconds):
    deadline = get_time() + seconds
    handles = []
    local = [0]
    for index in range(1, 16):
        handle = spawn_drone(pumpkin_patch_job(index, deadline))
        if handle == None:
            local.append(index)
        else:
            handles.append(handle)
    good = True
    for index in local:
        if not pumpkin_patch_leader(index, deadline):
            good = False
    for handle in handles:
        if wait_for(handle) != True:
            good = False
    return good

def power_worker(lo, hi):
    n = get_world_size()
    for x in range(lo, hi):
        pr_go_to(x, 0)
        for y in range(n):
            if get_entity_type() != Entities.Sunflower:
                if get_entity_type() != None:
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                if not plant(Entities.Sunflower):
                    return False
            while get_water() < 0.99:
                if not use_item(Items.Water):
                    return False
            move(North)
    for count in range(64):
        for x in range(lo, hi):
            pr_go_to(x, 0)
            for y in range(n):
                if can_harvest():
                    if not harvest() or not plant(Entities.Sunflower):
                        return False
                    while get_water() < 0.99:
                        if not use_item(Items.Water):
                            return False
                move(North)
    return True

def power_job(lo, hi):

    def work():
        return power_worker(lo, hi)
    return work

def power_batch():
    n = get_world_size()
    ranges = pr_mp_ranges(n, pr_mp_capacity(n))
    handles = []
    local = [ranges[0]]
    for lo, hi in ranges[1:]:
        h = spawn_drone(power_job(lo, hi))
        if h == None:
            local.append((lo, hi))
        else:
            handles.append(h)
    good = True
    for lo, hi in local:
        if not power_worker(lo, hi):
            good = False
            break
    for h in handles:
        if wait_for(h) != True:
            good = False
    return good

def focus_budget(mode):
    n = get_world_size()
    count = n // 4 * (n // 8) * 64
    costs = {}
    for entity in [
        Entities.Grass,
        Entities.Bush,
        Entities.Tree,
        Entities.Carrot
    ]:
        if not pr_add_cost(costs, entity, count):
            return None
    return costs

def boost_ready(reserves, fuel=None):
    started = get_time()
    while not can_harvest():
        if get_time() - started >= 600 or not pr_water_here():
            return False
        if (
            FERTILIZE
            and (fuel == None or fuel[0] > 0)
            and (num_items(Items.Fertilizer) > pr_unlock_amount(
                reserves,
                Items.Fertilizer
            ))
            and (num_items(Items.Weird_Substance) > pr_unlock_amount(
                reserves,
                Items.Weird_Substance
            ))
        ):
            if use_item(Items.Fertilizer):
                if not use_item(Items.Weird_Substance):
                    return False
                if fuel != None:
                    fuel[0] -= 1
    return pr_water_here()

def focus_worker(lo, hi, mode, reserves, fuel=None):
    n = get_world_size()
    entity = Entities.Carrot
    if mode == 'hay':
        entity = Entities.Grass
    if mode == 'wood':
        entity = Entities.Tree
    if mode == 'bush':
        entity = Entities.Bush
        fuel = [0]
    for index in range(lo, hi):
        bx = index // (n // 8) * 4
        by = index % (n // 8) * 8
        x = bx + 1
        y = by + 3
        pr_go_to(x, y)
        for attempt in range(64):
            if get_entity_type() != None:
                harvest()
            if get_ground_type() != Grounds.Soil:
                till()
            if not plant(entity) or not pr_water_here():
                return False
            want = get_companion()
            if want == None:
                return False
            kind, (cx, cy) = want
            if cx < bx or cx >= bx + 4 or cy < by or (cy >= by + 8):
                continue
            pr_go_to(cx, cy)
            if get_entity_type() != kind:
                if get_entity_type() != None:
                    harvest()
                if get_ground_type() != Grounds.Soil:
                    till()
                if not plant(kind):
                    return False
            pr_go_to(x, y)
            if not boost_ready(reserves, fuel) or not harvest():
                return False
    return True

def focus_job(lo, hi, mode, reserves, fuel):

    def work():
        return focus_worker(lo, hi, mode, reserves, [fuel])
    return work

def focus_batch(mode, reserves):
    n = get_world_size()
    total = pr_mp_capacity(n // 4 * (n // 8))
    ranges = pr_mp_ranges(total, total)
    fuel = boost_quota(reserves, len(ranges))
    handles = []
    local = [ranges[0]]
    for i in range(1, len(ranges)):
        lo, hi = ranges[i]
        handle = spawn_drone(focus_job(lo, hi, mode, reserves, fuel))
        if handle == None:
            local.append((lo, hi))
        else:
            handles.append(handle)
    good = True
    for part in local:
        if not focus_worker(part[0], part[1], mode, reserves, [fuel]):
            good = False
            break
    for handle in handles:
        if wait_for(handle) != True:
            good = False
    return good

def boost_quota(reserves, workers):
    free = min(
        num_items(Items.Fertilizer) - pr_unlock_amount(
            reserves,
            Items.Fertilizer
        ),
        num_items(Items.Weird_Substance) - pr_unlock_amount(
            reserves,
            Items.Weird_Substance
        )
    )
    return max(0, free // workers)
GOLD_DIRS = [North, East, South, West]
GOLD_DX = [0, 1, 0, -1]
GOLD_DY = [1, 0, -1, 0]

def gold_edges(pos):
    edges = []
    for d in range(4):
        if can_move(GOLD_DIRS[d]):
            edges.append((
                (pos[0] + GOLD_DX[d], pos[1] + GOLD_DY[d]),
                GOLD_DIRS[d]
            ))
    return edges

def gold_map():
    graph = {}
    back = []
    while True:
        pos = (get_pos_x(), get_pos_y())
        edges = gold_edges(pos)
        graph[pos] = edges
        advanced = False
        for dest, direction in edges:
            if dest not in graph:
                move(direction)
                back.append(pr_opposite(direction))
                advanced = True
                break
        if not advanced:
            if len(back) == 0:
                return graph
            move(back.pop())

def gold_walk(graph, target):
    pos = (get_pos_x(), get_pos_y())
    if pos == target:
        return True
    queue = [pos]
    parent = {pos: None}
    at = 0
    while at < len(queue) and target not in parent:
        current = queue[at]
        at += 1
        for dest, direction in graph[current]:
            if dest not in parent:
                parent[dest] = (current, direction)
                queue.append(dest)
    if target not in parent:
        return False
    route = []
    node = target
    while node != pos:
        node, direction = parent[node]
        route.append(direction)
    for i in range(len(route) - 1, -1, -1):
        pos = (get_pos_x(), get_pos_y())
        graph[pos] = gold_edges(pos)
        if not move(route[i]):
            return False
    return True

def gold_settings():
    size = gold_placement(0)[0]
    capacity = (get_world_size() // max(5, size)) ** 2
    if GOLD_SIZE == 'mixed' and get_world_size() >= 32:
        capacity = 32
    workers = pr_mp_capacity(capacity)
    rounds = 1200
    if MODE in ['auto', 'balance']:
        rounds = 30
    return (workers, size * 2 ** (num_unlocked(Unlocks.Mazes) - 1), rounds)

def gold_placement(index):
    n = get_world_size()
    size = GOLD_SIZE
    if size == 'mixed':
        if n >= 32:
            sites = [
                (6, 0, 0),
                (6, 0, 26),
                (6, 6, 0),
                (6, 6, 26),
                (6, 12, 26),
                (6, 13, 0),
                (6, 19, 0),
                (6, 19, 26),
                (6, 20, 7),
                (6, 20, 14),
                (6, 20, 20),
                (6, 26, 0),
                (6, 26, 7),
                (6, 26, 14),
                (6, 26, 20),
                (6, 26, 26)
            ]
            if index < 16:
                side, x, y = sites[index]
                return (side, x + 3, y + 3)
            index -= 16
            return (5, index // 4 * 5 + 2, 6 + index % 4 * 5 + 2)
        size = 5
    step = max(5, size)
    side = n // step
    return (
        size,
        index // side * step + size // 2,
        index % side * step + size // 2
    )

def gold_find(graph, target):
    if target == None:
        return False
    while (get_pos_x(), get_pos_y()) != target:
        x = get_pos_x()
        y = get_pos_y()
        d = North
        if x < target[0]:
            d = East
        elif x > target[0]:
            d = West
        elif y > target[1]:
            d = South
        if not can_move(d):
            if len(graph) > 0:
                return gold_walk(graph, target)
            return pr_solve_maze(False)
        move(d)
    return True

def gold_cycle(index, unit, rounds, deadline=None):
    size, ax, ay = gold_placement(index)
    unit = size * 2 ** (num_unlocked(Unlocks.Mazes) - 1)
    pr_go_to(ax, ay)
    if get_entity_type() != None:
        harvest()
    if get_ground_type() != Grounds.Soil:
        till()
    if not plant(Entities.Bush) or not use_item(Items.Weird_Substance, unit):
        return False
    graph = {}
    if size >= 4:
        graph = gold_map()
        if len(graph) != size * size:
            return False
    good = True
    for i in range(rounds):
        if deadline != None and get_time() >= deadline:
            break
        target = measure()
        if not gold_find(graph, target):
            good = False
            break
        if (
            get_entity_type() != Entities.Treasure
            or not use_item(Items.Weird_Substance, unit)
        ):
            good = False
            break
    if get_entity_type() in [Entities.Hedge, Entities.Treasure]:
        target = measure()
        if not gold_find(graph, target) or not harvest():
            return False
    return good

def gold_worker(index, unit, rounds, deadline=None):
    for i in range((rounds + 299) // 300):
        if deadline != None and get_time() >= deadline:
            break
        if not gold_cycle(index, unit, min(300, rounds - i * 300), deadline):
            return False
    return True

def gold_job(index, unit, rounds, start, deadline):

    def work():
        while num_items(Items.Weird_Substance) >= start:
            if get_time() >= deadline:
                return False
        until = None
        if MODE == 'gold':
            until = deadline
        return gold_worker(index, unit, rounds, until)
    return work

def gold_batch():
    n = get_world_size()
    good, ignored = pr_mp_dispatch('empty', n)
    if not good:
        return False
    workers, unit, rounds = gold_settings()
    start = num_items(Items.Weird_Substance)
    deadline = get_time() + 600
    until = None
    if MODE == 'gold':
        deadline = get_time() + 240
        until = deadline
    handles = []
    local = []
    for i in range(1, workers):
        size, ax, ay = gold_placement(i)
        pr_go_to(ax, ay)
        h = spawn_drone(gold_job(i, unit, rounds, start, deadline))
        if h == None:
            local.append(i)
        else:
            handles.append(h)
    good = gold_worker(0, unit, rounds, until)
    for index in local:
        if not gold_worker(index, unit, rounds, until):
            good = False
            break
    for h in handles:
        if wait_for(h) != True:
            good = False
    return good

def upgrade_target(skipped):
    best = None
    score = None
    skills = Unlocks
    if STATE['reset']:
        skills = [
            Unlocks.Plant,
            Unlocks.Speed,
            Unlocks.Expand,
            Unlocks.Grass,
            Unlocks.Carrots,
            Unlocks.Trees,
            Unlocks.Pumpkins,
            Unlocks.Sunflowers,
            Unlocks.Polyculture,
            Unlocks.Watering,
            Unlocks.Fertilizer,
            Unlocks.Cactus,
            Unlocks.Dinosaurs,
            Unlocks.Mazes,
            Unlocks.Megafarm,
            Unlocks.Leaderboard
        ]
    for skill in skills:
        if (
            skill in STATE['blocked']
            or (skill == Unlocks.Expand and (not ALLOW_EXPAND))
        ):
            continue
        cost = get_cost(skill)
        if cost == None or (len(cost) == 0 and num_unlocked(skill) > 0):
            continue
        value = 0
        possible = True
        for item in cost:
            missing = cost[item] - num_items(item)
            if missing > 0:
                if item in skipped or not usable(item, []):
                    possible = False
                    break
                value += missing / max(1, num_items(item))
        if possible and (score == None or value < score):
            score = value
            best = (skill, cost)
    return best

def step(skipped):
    STATE['deferred'] = None
    STATE['target'] = None
    chosen = None
    if (
        MODE == 'auto'
        and AUTO_BUY
        and (num_unlocked(Unlocks.Auto_Unlock) > 0)
        and (STATE['rounds'] % 5 != 4)
    ):
        chosen = upgrade_target(skipped)
    if chosen != None:
        skill, cost = chosen
        ready = True
        for item in cost:
            if num_items(item) < cost[item]:
                ready = False
                if item in skipped:
                    break
                held = {}
                for other in cost:
                    if other != item:
                        held[other] = cost[other]
                STATE['target'] = item
                STATE['rounds'] += 1
                if item in [Items.Water, Items.Fertilizer]:
                    return need(item, cost[item], held, [])
                return make(item, held, [])
        if ready:
            level = num_unlocked(skill)
            if unlock(skill) and num_unlocked(skill) > level:
                STATE['blocked'] = []
                if STATE['reset']:
                    quick_print(
                        'RESET_UPGRADE',
                        skill,
                        num_unlocked(skill),
                        get_world_size()
                    )
            else:
                current = get_cost(skill)
                short = False
                if current != None:
                    for item in current:
                        if num_items(item) < current[item]:
                            short = True
                if not short:
                    STATE['blocked'].append(skill)
            STATE['rounds'] += 1
            return True
    item = None
    score = None
    for candidate in TARGETS:
        if (
            candidate in skipped
            or TARGETS[candidate] <= 0
            or (not usable(candidate, []))
        ):
            continue
        value = num_items(candidate) / TARGETS[candidate]
        if score == None or value < score:
            item = candidate
            score = value
    if item == None:
        return False
    STATE['rounds'] += 1
    STATE['target'] = item
    return make(item, {}, [])

def prepare(watering=True):
    global pr_MAX_DRONES
    global pr_POLYCULTURE_ENABLED
    global pr_WATER_ENABLED
    pr_MAX_DRONES = MAX_DRONES
    pr_POLYCULTURE_ENABLED = COMPANIONS
    pr_WATER_ENABLED = num_unlocked(Unlocks.Watering) > 0
    if num_unlocked(Unlocks.Megafarm) > 0 and num_drones() != 1:
        quick_print('请结束其他无人机程序，再运行 farm_auto。')
        return False
    if num_unlocked(Unlocks.Timing) == 0:
        return False
    change_hat(Hats.Straw_Hat)
    if not pr_resume_existing_maze():
        return False
    clear()
    STATE['layout'] = None
    if watering and num_unlocked(Unlocks.Watering) == 0:
        if MODE != 'auto':
            return True
        cost = get_cost(Unlocks.Watering)
        if not AUTO_BUY or cost == None:
            return False
        pr_WATER_ENABLED = False
        for item in cost:
            if not need(item, cost[item], {}, []):
                pr_WATER_ENABLED = True
                return False
        pr_WATER_ENABLED = True
        if not unlock(Unlocks.Watering) or num_unlocked(Unlocks.Watering) == 0:
            return False
    return True

def run_one():
    if MODE in ['auto', 'balance']:
        return step([])
    items = {
        'hay': Items.Hay,
        'wood': Items.Wood,
        'bush': Items.Wood,
        'carrot': Items.Carrot,
        'pumpkin': Items.Pumpkin,
        'sunflower': Items.Power,
        'cactus': Items.Cactus,
        'dinosaur': Items.Bone,
        'weird': Items.Weird_Substance,
        'gold': Items.Gold
    }
    STATE['deferred'] = None
    if MODE not in items:
        return False
    STATE['target'] = items[MODE]
    return make(items[MODE], {}, [])

def achievement_need(item, amount, reserves, path):
    progress = {'stagnant': 0}
    while True:
        STATE['deferred'] = None
        if need(item, amount, reserves, path, progress):
            return True
        if STATE['deferred'] == None:
            return False
        if not pr_wait_for_item(STATE['deferred'], STATE['required']):
            return False

def leaderboard_spec(name):
    specs = {
        'hay': (Items.Hay, 2000000000),
        'wood': (Items.Wood, 10000000000),
        'carrot': (Items.Carrot, 2000000000),
        'pumpkin': (Items.Pumpkin, 200000000),
        'sunflower': (Items.Power, 100000),
        'cactus': (Items.Cactus, 33554432),
        'dinosaur': (Items.Bone, 33488928),
        'gold': (Items.Gold, 9863168),
        'hay_single': (Items.Hay, 100000000),
        'wood_single': (Items.Wood, 500000000),
        'carrot_single': (Items.Carrot, 100000000),
        'pumpkin_single': (Items.Pumpkin, 10000000),
        'sunflower_single': (Items.Power, 10000),
        'cactus_single': (Items.Cactus, 131072),
        'gold_single': (Items.Gold, 616448)
    }
    if name in specs:
        return specs[name]
    return None

def leaderboard_object(name):
    if name == 'reset':
        return Leaderboards.Fastest_Reset
    if name == 'hay':
        return Leaderboards.Hay
    if name == 'wood':
        return Leaderboards.Wood
    if name == 'carrot':
        return Leaderboards.Carrots
    if name == 'pumpkin':
        return Leaderboards.Pumpkins
    if name == 'sunflower':
        return Leaderboards.Sunflowers
    if name == 'cactus':
        return Leaderboards.Cactus
    if name == 'dinosaur':
        return Leaderboards.Dinosaur
    if name == 'gold':
        return Leaderboards.Maze
    if name == 'hay_single':
        return Leaderboards.Hay_Single
    if name == 'wood_single':
        return Leaderboards.Wood_Single
    if name == 'carrot_single':
        return Leaderboards.Carrots_Single
    if name == 'pumpkin_single':
        return Leaderboards.Pumpkins_Single
    if name == 'sunflower_single':
        return Leaderboards.Sunflowers_Single
    if name == 'cactus_single':
        return Leaderboards.Cactus_Single
    if name == 'gold_single':
        return Leaderboards.Maze_Single
    return None

def leaderboard_farm():
    global pr_WATER_ENABLED
    global MODE
    global AUTO_BUY
    global FERTILIZE
    global FAST
    global MAX_DRONES
    spec = leaderboard_spec(LEADERBOARD_NAME)
    if spec == None:
        return False
    item, goal = spec
    if num_items(item) >= goal:
        return True
    MODE = LEADERBOARD_NAME
    if LEADERBOARD_NAME[-7:] == '_single':
        MODE = LEADERBOARD_NAME[:-7]
        MAX_DRONES = 1
    AUTO_BUY = False
    FERTILIZE = num_items(Items.Fertilizer) > 0
    water = num_items(Items.Water) >= 4 * get_world_size() ** 2
    FAST = FAST and (water or MODE in ['gold', 'cactus', 'dinosaur'])
    if not prepare(False):
        return False
    pr_WATER_ENABLED = water
    while num_items(item) < goal:
        if not run_one():
            return False
    return True

def reset_farm():
    if num_unlocked(Unlocks.Leaderboard) > 0:
        return True
    return reset_develop()

def reset_develop():
    global pr_MAX_DRONES
    global pr_PASSIVE_WAIT_SECONDS
    global pr_POLYCULTURE_ENABLED
    global pr_WATER_ENABLED
    global MODE
    global AUTO_BUY
    global ALLOW_EXPAND
    global FERTILIZE
    global FAST
    MODE = 'auto'
    AUTO_BUY = True
    ALLOW_EXPAND = True
    FERTILIZE = False
    FAST = False
    STATE['reset'] = True
    pr_PASSIVE_WAIT_SECONDS = 600
    pr_WATER_ENABLED = False
    pr_MAX_DRONES = 0
    pr_POLYCULTURE_ENABLED = COMPANIONS
    for count in range(100000):
        if num_unlocked(Unlocks.Leaderboard) > 0:
            return True
        if not step([]):
            if (
                STATE['deferred'] == None
                or not pr_wait_for_item(STATE['deferred'], STATE['required'])
            ):
                quick_print('完全复位停止：', STATE['target'], STATE['deferred'])
                return False
    quick_print('完全复位超过轮次限制。')
    return False

def launch_challenge():
    if LEADERBOARD_SPEEDUP < 1:
        quick_print('LEADERBOARD_SPEEDUP必须至少为1。')
        return False
    if MODE == 'reset':
        board = Leaderboards.Fastest_Reset
    else:
        board = leaderboard_object(LEADERBOARD_NAME)
    if board == None:
        quick_print('LEADERBOARD_NAME无效，请选择设置旁注释中的榜名。')
        return False
    if num_unlocked(Unlocks.Leaderboard) == 0 or num_drones() != 1:
        quick_print('请先解锁排行榜并停止其他无人机程序。')
        return False
    quick_print('排行榜入口：farm_auto；游戏代码窗口必须同名并保存。')
    leaderboard_run(board, 'farm_auto', LEADERBOARD_SPEEDUP)
    quick_print('排行榜调用已返回；成绩请查看游戏提示。')
    return True

def run():
    if GOLD_SIZE not in [3, 4, 5, 6, 'mixed']:
        quick_print('GOLD_SIZE请选择3、4、5、6或mixed。')
        return False
    if MODE in ['leaderboard', 'reset']:
        if _ENTRY_TIME == 0:
            if MODE == 'reset' or LEADERBOARD_NAME == 'reset':
                return reset_farm()
            return leaderboard_farm()
        return launch_challenge()
    modes = [
        'auto',
        'balance',
        'hay',
        'wood',
        'bush',
        'carrot',
        'pumpkin',
        'sunflower',
        'cactus',
        'dinosaur',
        'weird',
        'gold',
        'achievements'
    ]
    tasks = [
        'safe',
        'all',
        'higher_order',
        'pig',
        'healer',
        'fashion',
        'swarm',
        'mud',
        'wrong_order',
        'recycling',
        'stack'
    ]
    if (
        MODE not in modes
        or (MODE == 'achievements' and ACHIEVEMENT_TASK not in tasks)
    ):
        quick_print('MODE或ACHIEVEMENT_TASK无效，请查看使用说明。')
        return False
    if not prepare(MODE != 'achievements'):
        return False
    if MODE == 'achievements':
        return ach_run(
            ACHIEVEMENT_TASK,
            ACH_INCLUDE_OPTIONAL,
            achievement_need,
            budget
        )
    skipped = []
    waiting = None
    while True:
        good = False
        if MODE in ['auto', 'balance']:
            good = step(skipped)
        else:
            good = run_one()
        if good:
            skipped = []
            continue
        if STATE['deferred'] == None:
            if STATE['target'] == None and waiting != None:
                if not pr_wait_for_item(waiting[0], waiting[1]):
                    return False
                skipped = []
                waiting = None
                continue
            quick_print('生产停止，请查看上方原因。')
            return False
        waiting = (STATE['deferred'], STATE['required'])
        if MODE not in ['auto', 'balance']:
            if not pr_wait_for_item(waiting[0], waiting[1]):
                return False
            continue
        target = STATE['target']
        if target != None and target not in skipped:
            skipped.append(target)
        if len(skipped) >= len(TARGETS):
            supply = STATE['deferred']
            if not pr_wait_for_item(supply, STATE['required']):
                return False
            skipped = []
if __name__ == '__main__':
    run()
