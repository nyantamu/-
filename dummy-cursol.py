import pygame
import random
import sys
import math
import time
import csv

# 初期化
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Dummy Cursor Experiment")

# 色定義
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# カーソル数設定
n = 10  # ダミーの数

#時間制限
limit_time = 30

# パラメータ調整
cursor_speed_multiplier = 1
delay_time = 0.0
delay_frames = 60

total_cursors = n + 1
motion_ids = list(range(1, n+1)) + [n+1]
display_ids = list(range(1, n+2))
random.shuffle(display_ids)

# カーソルデータ作成
""" cursors = []
for i in range(total_cursors):
    cursors.append({
        'motion_id': motion_ids[i],
        'display_id': display_ids[i],
        'pos': [random.randint(200, 600), random.randint(150, 450)],
        'delay_buffer': [0, 0]
    })

virtual_cursor_pos = [400, 300] """
# カーソルと位置を毎試行生成

# メインループ用変数
running = True
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 72)
small_font = pygame.font.SysFont(None, 36)
input_id = ""

pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# カウントダウン
countdown_time = 3
countdown_start = time.time()
countdown_active = True

start_time = 0
show_result = False
result_text = ""
result_start_time = 0
result_screen = False
answer_time = 0
attempt_count = 0

#最小角度
p=30



# 試行制御
trial_count = 0
max_trials = 5
correct_count = 0
trial_active = False
trial_start_time = 0

# CSVヘッダー書き込み
with open('results.csv', 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Answer Time (sec)', 'Attempts'])

def generate_cursors():
    motion_ids = list(range(1, n+1)) + [n+1]
    display_ids = list(range(1, n+2))
    random.shuffle(display_ids)
    cursors = []
    for i in range(total_cursors):
        cursors.append({
            'motion_id': motion_ids[i],
            'display_id': display_ids[i],
            'pos': [random.randint(200, 600), random.randint(150, 450)],
            'delay_buffer': [0, 0]
        })
    return cursors, [400, 300]

# 最初の試行の準備
cursors, virtual_cursor_pos = generate_cursors()
trial_start_time = time.time()

while running:
    current_time = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if not countdown_active and not result_screen and trial_active:
                if event.key == pygame.K_RETURN:
                    if input_id.lower() == "end":
                        running = False
                    elif input_id.isdigit():
                        guess = int(input_id)
                        attempt_count += 1
                        for cursor in cursors:
                            if cursor['display_id'] == guess:
                                answer_time = time.time() - trial_start_time
                                if cursor['motion_id'] == n+1:
                                    correct_count += 1
                                    result_text = "CORRECT !!!"
                                    with open('results.csv', 'a', newline='') as csvfile:
                                        writer = csv.writer(csvfile)
                                        writer.writerow([f"{answer_time:.2f}", "o"]) #attenpy_count
                                    cursors, virtual_cursor_pos = generate_cursors()
                                else:
                                    result_text = "DUMMY (T_T)"
                                    with open('results.csv', 'a', newline='') as csvfile:
                                        writer = csv.writer(csvfile)
                                        writer.writerow([f"{answer_time:.2f}", "x"])
                                    cursors, virtual_cursor_pos = generate_cursors()
                                result_start_time = time.time()
                                result_screen = True
                                trial_count += 1
                                trial_active = False
                                input_id = ""
                                break

                elif event.key == pygame.K_BACKSPACE:
                    input_id = input_id[:-1]
                else:
                    input_id += event.unicode

    if countdown_active:
        screen.fill(WHITE)
        remaining = countdown_time - (current_time - countdown_start)
        if remaining > 0:
            countdown_display = font.render(str(int(remaining) + 1), True, BLACK)
            screen.blit(countdown_display, (380, 250))
        else:
            countdown_active = False
            start_time = time.time()
            trial_active = True
            trial_start_time = time.time()

    elif result_screen:
        screen.fill(WHITE)
        result_display = small_font.render(result_text, True, BLACK)
        time_display = small_font.render(f"Answer Time: {answer_time:.2f} sec", True, BLACK)
        attempt_display = small_font.render(f"Attempts: {attempt_count}", True, BLACK)
        screen.blit(result_display, (300, 250))
        screen.blit(time_display, (300, 300))
        screen.blit(attempt_display, (300, 350))

        if time.time() - result_start_time > 2:
            result_screen = False
            input_id = ""
            if trial_count >= max_trials:
                accuracy = correct_count / max_trials
                with open('results.csv', 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Accuracy', f"{accuracy:.2f}"])
                running = False
            else:
                trial_active = True
                trial_start_time = time.time()

    else:
        screen.fill(WHITE)
        """ for x in range(0, 800, 50):
            pygame.draw.line(screen, (200, 200, 200), (x, 0), (x, 600))
        for y in range(0, 600, 50):
            pygame.draw.line(screen, (200, 200, 200), (0, y), (800, y)) """

        dx, dy = pygame.mouse.get_rel()
        dx *= cursor_speed_multiplier
        dy *= cursor_speed_multiplier

        # 仮想カーソルの移動
        virtual_cursor_pos[0] += dx
        virtual_cursor_pos[1] += dy

        # 遅延履歴のダミー実装（未使用）
        history = []
        history.append(virtual_cursor_pos[:])
        if len(history) > delay_frames:
            delayed_pos = history[-delay_frames]
        else:
            delayed_pos = history[0]

        for cursor in cursors:
            if cursor['motion_id'] == n+1:
                cursor['pos'] = virtual_cursor_pos.copy()
            else:
                #theta = math.radians(360 / n * (cursor['motion_id'] - 1) + 20) #ダミーカーソル角度
                theta = p + (cursor['motion_id'] - 1) * (math.radians(360) - 2 * p) / (n - 1)
                rotated_dx = dx * math.cos(theta) - dy * math.sin(theta)
                rotated_dy = dx * math.sin(theta) + dy * math.cos(theta)

                if delay_time > 0:
                    cursor['delay_buffer'][0] += rotated_dx
                    cursor['delay_buffer'][1] += rotated_dy
                    if time.time() - start_time >= delay_time:
                        cursor['pos'][0] += cursor['delay_buffer'][0]
                        cursor['pos'][1] += cursor['delay_buffer'][1]
                        cursor['delay_buffer'] = [0, 0]
                else:
                    cursor['pos'][0] += rotated_dx
                    cursor['pos'][1] += rotated_dy

            pygame.draw.circle(screen, RED, (int(cursor['pos'][0]), int(cursor['pos'][1])), 22) #カーソルの色、大きさ 22で１ｃｍくらい
            id_text = small_font.render(str(cursor['display_id']), True, BLACK)
            screen.blit(id_text, (cursor['pos'][0] + 10, cursor['pos'][1] - 10))

        input_text = small_font.render("input: " + input_id, True, BLACK)
        screen.blit(input_text, (10, 10))

        if trial_active and time.time() - trial_start_time > limit_time: 
            result_text = "TIME UP"
            with open('results.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([f"time up", "x"])
            result_start_time = time.time()
            result_screen = True
            trial_count += 1
            trial_active = False
            cursors, virtual_cursor_pos = generate_cursors()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
