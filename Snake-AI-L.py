import pygame, random, sys

G_W, P_W, PLAY_H, HDR, CELL = 600, 300, 600, 40, 20
W_W, W_H = G_W + P_W, PLAY_H + HDR

pygame.init()
screen = pygame.display.set_mode((W_W, W_H))
pygame.display.set_caption("Snake-AI-L")
clock, font, font_l = pygame.time.Clock(), pygame.font.SysFont("Arial", 16, bold=True), pygame.font.SysFont("Arial", 28, bold=True)

ALPHA, GAMMA, epsilon, EPS_DECAY, EPS_MIN = 0.3, 0.95, 1.0, 0.9995, 0.01
q_table, ACTIONS = {}, [0, 1, 2] # Проверить акшионс

def get_state(snake, direction, food):
    head, dirs = snake[0], [[0, -CELL], [CELL, 0], [0, CELL], [-CELL, 0]]
    idx = ["UP", "RIGHT", "DOWN", "LEFT"].index(direction)
    v_f, v_r, v_l = dirs[idx], dirs[(idx + 1) % 4], dirs[(idx - 3) % 4]
    #https://github.com/loanelly
    def look(v):
        cur, dist = [head[0] + v[0], head[1] + v[1]], 1 
        while not (cur[0] < 0 or cur[0] >= G_W or cur[1] < HDR or cur[1] >= W_H or cur in snake[1:]):
            cur[0] += v[0]; cur[1] += v[1]; dist += 1
        return 1 if dist == 1 else 2 if dist <= 3 else 3
#https://github.com/loanelly
    df, dr, dl = look(v_f), look(v_r), look(v_l)
    dx, dy = food[0] - head[0], food[1] - head[1]
    if direction == "UP":    f_f, f_r = (dy < 0), (dx > 0)
    elif direction == "RIGHT": f_f, f_r = (dx > 0), (dy > 0)
    elif direction == "DOWN":  f_f, f_r = (dy > 0), (dx < 0)#https://github.com/loanelly
    else:                      f_f, f_r = (dx < 0), (dy < 0)
    return (df, dr, dl, int(f_f), int(f_r), int(not f_r and (dx != 0 or dy != 0) and not f_f))
#https://github.com/loanelly
def get_space(start, snake_set):
    if start[0] < 0 or start[0] >= G_W or start[1] < HDR or start[1] >= W_H or tuple(start) in snake_set: return 0
    q, visited, count, limit = [start], {tuple(start)}, 0, len(snake_set) + 5
    while q and count < limit:
        curr = q.pop(0); count += 1#https://github.com/loanelly
        for n in [[curr[0]+CELL, curr[1]], [curr[0]-CELL, curr[1]], [curr[0], curr[1]+CELL], [curr[0], curr[1]-CELL]]:
            if 0 <= n[0] < G_W and HDR <= n[1] < W_H and tuple(n) not in snake_set and tuple(n) not in visited:
                visited.add(tuple(n)); q.append(n)
    return count
#https://github.com/loanelly
def a_star(snake, food):
    start, end, snake_set = tuple(snake[0]), tuple(food), {tuple(p) for p in snake[1:]}
    open_set, came_from, g = {start}, {}, {start: 0}#https://github.com/loanelly
    f = {start: abs(start[0]-end[0]) + abs(start[1]-end[1])}
    while open_set:
        curr = min(open_set, key=lambda x: f.get(x, float('inf')))#https://github.com/loanelly
        if curr == end:
            path = []
            while curr in came_from: path.append(curr); curr = came_from[curr]
            return path[::-1]
        open_set.remove(curr)#https://github.com/loanelly
        for n in [(curr[0]+CELL, curr[1]), (curr[0]-CELL, curr[1]), (curr[0], curr[1]+CELL), (curr[0], curr[1]-CELL)]:#https://github.com/loanelly
            if n[0] < 0 or n[0] >= G_W or n[1] < HDR or n[1] >= W_H or n in snake_set: continue
            tg = g[curr] + 1
            if tg < g.get(n, float('inf')):
                came_from[n], g[n] = curr, tg
                f[n] = tg + abs(n[0]-end[0]) + abs(n[1]-end[1]) #https://github.com/loanelly
                open_set.add(n)#https://github.com/loanelly
    return None

def main():
    global epsilon
    mode, episode, recent, avg = 3, 0, [], 0
    while True:
        episode += 1
        snake, direction = [[300, 300], [280, 300], [260, 300]], "RIGHT"#https://github.com/loanelly
        food = [random.randrange(0, G_W // CELL) * CELL, random.randrange(HDR // CELL, W_H // CELL) * CELL]
        score, steps, game_over = 0, 0, False

        while not game_over:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()#https://github.com/loanelly
                if ev.type == pygame.KEYDOWN and ev.key in [pygame.K_1, pygame.K_2, pygame.K_3]: mode = int(ev.unicode)

            state = get_state(snake, direction, food)
            if state not in q_table: q_table[state] = [0.0, 0.0, 0.0]#https://github.com/loanelly
            
            dir_names = ["UP", "RIGHT", "DOWN", "LEFT"]
            d_idx, path, act_choice = dir_names.index(direction), a_star(snake, food), None
            
            if path and random.uniform(0, 1) > epsilon:
                for a in ACTIONS:#https://github.com/loanelly
                    td = dir_names[(d_idx + (1 if a == 1 else -1 if a == 2 else 0)) % 4]
                    v = [[0, -CELL], [CELL, 0], [0, CELL], [-CELL, 0]][dir_names.index(td)]
                    if [snake[0][0] + v[0], snake[0][1] + v[1]] == list(path[0]): act_choice = a; break
            
            if act_choice is None: act_choice = random.choice(ACTIONS) if random.uniform(0, 1) < epsilon else q_table[state].index(max(q_table[state]))
            
            s_set = {tuple(p) for p in snake}
            safe_act = act_choice#https://github.com/loanelly
            for a in [act_choice] + [act for act in ACTIONS if act != act_choice]:
                td = dir_names[(d_idx + (1 if a == 1 else -1 if a == 2 else 0)) % 4]
                v = [[0, -CELL], [CELL, 0], [0, CELL], [-CELL, 0]][dir_names.index(td)]
                if get_space([snake[0][0]+v[0], snake[0][1]+v[1]], s_set) >= len(snake): safe_act = a; break
                
            action, curr_q = safe_act, q_table[state][safe_act]#https://github.com/loanelly
            direction = dir_names[(d_idx + (1 if action == 1 else -1 if action == 2 else 0)) % 4]
            v = [[0, -CELL], [CELL, 0], [0, CELL], [-CELL, 0]][dir_names.index(direction)]
            head = [snake[0][0] + v[0], snake[0][1] + v[1]]
            
            snake.insert(0, head)
            steps, reward = steps + 1, -0.15

            if head[0] < 0 or head[0] >= G_W or head[1] < HDR or head[1] >= W_H or head in snake[1:] or steps > (300 + len(snake) * 3):
                reward, game_over = -200, True; snake.pop()
            elif head == food:#https://github.com/loanelly
                score, reward, steps = score + 10, 150 + len(snake) * 5, 0
                while True:
                    food = [random.randrange(0, G_W // CELL) * CELL, random.randrange(HDR // CELL, W_H // CELL) * CELL]
                    if food not in snake: break
            else:#https://github.com/loanelly
                snake.pop()
                if (abs(head[0] - food[0]) + abs(head[1] - food[1])) < (abs(snake[0][0] - food[0]) + abs(snake[0][1] - food[1])): reward = 2.0

            n_state = get_state(snake, direction, food)
            if n_state not in q_table: q_table[n_state] = [0.0, 0.0, 0.0]
            q_table[state][action] += ALPHA * (reward + GAMMA * max(q_table[n_state]) - curr_q)

            if mode == 3:#https://github.com/loanelly
                if steps % 10000 == 0 or steps == 1:
                    screen.fill((15, 15, 22))
                    screen.blit(font_l.render("ГРАФИКА ОТКЛЮЧЕНА ДЛЯ УСКОРЕНИЯ", True, (231, 76, 60)), (W_W // 2 - 240, W_H // 2 - 40))
                    screen.blit(font.render(f"Игр: {episode} | Модель: {len(q_table)} состояний | Ср. счет: {avg:.1f} | Хаос (Eps): {epsilon:.3f}", True, (255, 255, 255)), (W_W // 2 - 200, W_H // 2 + 10))
                    screen.blit(font.render("Нажмите 1 или 2 для включения видеорежима", True, (120, 120, 140)), (W_W // 2 - 150, W_H // 2 + 40))
                    pygame.display.flip()
            else:#https://github.com/loanelly
                screen.fill((30, 30, 30))
                pygame.draw.rect(screen, (20, 20, 20), (0, 0, G_W, HDR))
                pygame.draw.rect(screen, (231, 76, 60), (food[0], food[1], CELL, CELL))
                for i, p in enumerate(snake): pygame.draw.rect(screen, (241, 196, 15) if i == 0 else (46, 196, 182), (p[0], p[1], CELL, CELL))
                #https://github.com/loanelly
                x = G_W + 20
                pygame.draw.rect(screen, (20, 20, 28), (G_W, 0, P_W, W_H))
                pygame.draw.line(screen, (60, 60, 60), (G_W, 0), (G_W, W_H), 2)
                screen.blit(font.render(f"Счет: {score} | Игр: {episode} | Режим: {mode}", True, (255,255,255)), (15, 10))
                screen.blit(font.render("АНАЛИТИКА ИИ [ПОКАЗАТЕЛИ]", True, (241, 196, 15)), (x, 20))
                screen.blit(font.render(f"Хаос (Eps): {epsilon:.3f} | База знаний: {len(q_table)}", True, (255,255,255)), (x, 45))
                screen.blit(font.render(f"Ср. счет (50 игр): {avg:.1f}", True, (230, 126, 34)), (x, 70))
                #https://github.com/loanelly
                screen.blit(font.render("ЧТО ВИДИТ ЗМЕЙКА:", True, (52, 152, 219)), (x, 120))
                for i, name in enumerate(["Опасность Прямо", "Опасность Справа", "Опасность Слева", "Еда Прямо", "Еда Справа", "Еда Слева"]):
                    y_p = 145 + i * 25
                    active = [state[0] == 1, state[1] == 1, state[2] == 1, state[3], state[4], state[5]][i]
                    pygame.draw.circle(screen, (46, 204, 113) if active else (100, 30, 30), (x + 10, y_p + 10), 6)
                    screen.blit(font.render(name, True, (255,255,255) if active else (120,120,120)), (x + 25, y_p))
                    #https://github.com/loanelly
                screen.blit(font.render("ВЕСА НАПРАВЛЕНИЙ:", True, (155, 89, 182)), (x, 320))
                b_a = q_table[state].index(max(q_table[state]))
                for i, name in enumerate(["ПРЯМО", "ВПРАВО", "ВЛЕВО"]):
                    y_p = 345 + i * 35; val = q_table[state][i]
                    screen.blit(font.render(f"{name}: {val:.1f}", True, (46, 204, 113) if i == b_a else (255,255,255)), (x, y_p))
                    pygame.draw.rect(screen, (155, 89, 182) if i != b_a else (46, 204, 113), (x + 100, y_p + 4, max(0, min(140, int((val + 10) * 4))), 12))
                pygame.display.flip()#https://github.com/loanelly
                clock.tick(15 if mode == 1 else 500)
#https://github.com/loanelly
        if epsilon > EPS_MIN: epsilon *= EPS_DECAY
        recent.append(score)
        if len(recent) > 50: recent.pop(0)#https://github.com/loanelly
        avg = sum(recent) / len(recent)
#https://github.com/loanelly
if __name__ == "__main__":
    main()
    #https://github.com/loanelly
