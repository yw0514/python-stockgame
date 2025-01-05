import os
import sys
import pygame
import random

# PyInstaller 실행 환경에서 base_path 설정
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# 리소스 경로 설정
buy_button_path = os.path.join(base_path, 'image', '매수버튼(신).png')
sell_button_path = os.path.join(base_path, 'image', '매도버튼(신).png')
font_path = os.path.join(base_path, 'font', 'Galmuri11.ttf')

# Pygame 초기화
pygame.init()

# 화면 크기 설정
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("주식 게임")

# 색상 설정
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)


# 패널 크기 설정
panel_height = 100
panel_y = screen_height - panel_height

# 버튼 이미지 로드 및 크기 조정
buy_button_image_original = pygame.image.load(buy_button_path)
sell_button_image_original = pygame.image.load(sell_button_path)
button_width = 180
button_height = 50
buy_button_image = pygame.transform.scale(buy_button_image_original, (button_width, button_height))
sell_button_image = pygame.transform.scale(sell_button_image_original, (button_width, button_height))

# 버튼 위치 설정
sell_button_x = screen_width - button_width - 10
buy_button_x = sell_button_x - button_width - 10
buy_button_rect = buy_button_image.get_rect(
    topleft=(buy_button_x, panel_y + (panel_height - button_height) // 2))
sell_button_rect = sell_button_image.get_rect(
    topleft=(sell_button_x, panel_y + (panel_height - button_height) // 2))

# 폰트 설정
font = pygame.font.Font(font_path, 20)

# Pygame Clock 초기화
clock = pygame.time.Clock()

# 타이머 설정
graph_update_event = pygame.USEREVENT + 1
pygame.time.set_timer(graph_update_event, 1000)  # 1초마다 자동 그래프 변화

# 주식 데이터 초기화
stock_data = [random.randint(200, 400)]
max_data_points = 50
y_scale = 1.0

# 플레이어 상태
player_money = 300
player_stocks = []
average_price = 0

# 턴 및 이벤트 상태
current_turn = 1
next_event_turn = random.randint(5, 10)
current_event = "기본"
events = {
    "기본": {"effect": lambda: random.randint(-40, 40), "description": "일반적인 변동"},
    "급등": {"effect": lambda: random.randint(10, 60), "description": "주가가 상승할 가능성이 큼"},
    "급락": {"effect": lambda: random.randint(-60, -10), "description": "주가가 하락할 가능성이 큼"}
}

# 구매 및 판매 지점 기록 리스트
buy_points = []
sell_points = []

# 버튼 효과 관련 변수
buy_button_shake = False
sell_button_shake = False
buy_shake_start_time = 0
sell_shake_start_time = 0
shake_duration = 200
shake_amplitude = 5

buy_button_grow = False
sell_button_grow = False
buy_grow_start_time = 0
sell_grow_start_time = 0
grow_duration = 150

# 평균 가격 계산 함수
def calculate_average_price():
    if not player_stocks:
        return 0
    return sum(player_stocks) // len(player_stocks)

# 이벤트 변경 함수
def change_event():
    global current_event, next_event_turn
    available_events = list(events.keys())
    available_events.remove(current_event)
    current_event = random.choice(available_events)
    next_event_turn = current_turn + random.randint(5, 10)
    print(f"이벤트 변경: {current_event} - {events[current_event]['description']} (다음 변경: {next_event_turn} 턴)")

# 최저가/최고가 체크 함수
def check_price_event(price):
    if price <= 100 or price >= 500:
        print(f"특별 이벤트 변경! 가격: {price}")
        change_event()

# 게임 루프 실행
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                current_turn += 1
                price_change = events[current_event]["effect"]()
                new_price = stock_data[-1] + price_change
                new_price = max(100, min(new_price, 500))
                stock_data.append(new_price)
                if len(stock_data) > max_data_points:
                    stock_data.pop(0)
                    buy_points = [(i - 1, price) for i, price in buy_points if i > 0]
                    sell_points = [(i - 1, price) for i, price in sell_points if i > 0]
                check_price_event(new_price)

                if current_turn == next_event_turn:
                    change_event()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if buy_button_rect.collidepoint(event.pos):
                if player_money >= stock_data[-1]:
                    player_money -= stock_data[-1]
                    player_stocks.append(stock_data[-1])
                    average_price = calculate_average_price()
                    buy_points.append((len(stock_data) - 1, stock_data[-1]))
                    print(f"[구매] 현재가 {stock_data[-1]}원")
                    buy_button_grow = True
                    buy_grow_start_time = pygame.time.get_ticks()
                else:
                    print("[구매 실패] 예수금 부족")
                    buy_button_shake = True
                    buy_shake_start_time = pygame.time.get_ticks()

            elif sell_button_rect.collidepoint(event.pos):
                if player_stocks:
                    player_money += stock_data[-1]
                    sell_points.append((len(stock_data) - 1, stock_data[-1]))
                    player_stocks.pop(0)
                    average_price = calculate_average_price()
                    print(f"[판매] 현재가 {stock_data[-1]}원")
                    sell_button_grow = True
                    sell_grow_start_time = pygame.time.get_ticks()
                else:
                    print("[판매 실패] 보유 주식 없음")
                    sell_button_shake = True
                    sell_shake_start_time = pygame.time.get_ticks()

        elif event.type == graph_update_event:
            current_turn += 1
            price_change = events[current_event]["effect"]()
            new_price = stock_data[-1] + price_change
            new_price = max(100, min(new_price, 500))
            stock_data.append(new_price)
            if len(stock_data) > max_data_points:
                stock_data.pop(0)
                buy_points = [(i - 1, price) for i, price in buy_points if i > 0]
                sell_points = [(i - 1, price) for i, price in sell_points if i > 0]
            check_price_event(new_price)

            if current_turn == next_event_turn:
                change_event()

    # 화면 초기화
    screen.fill(GRAY)

    # 그래프 그리기
    center_y = (screen_height - panel_height) // 2
    for i in range(1, len(stock_data)):
        x1 = (i - 1) * (screen_width // max_data_points)
        x2 = i * (screen_width // max_data_points)
        y1 = center_y - int((stock_data[i - 1] - 300) * y_scale)
        y2 = center_y - int((stock_data[i] - 300) * y_scale)
        pygame.draw.rect(screen, RED if stock_data[i] > stock_data[i - 1] else BLUE,
                         (x2 - 5, min(y1, y2), 10, abs(y2 - y1)))
        pygame.draw.line(screen, ORANGE, (x1, y1), (x2, y2), 2)

    # 구매 지점 표시
    for index, price in buy_points:
        x = index * (screen_width // max_data_points)
        y = center_y - int((price - 300) * y_scale)
        pygame.draw.circle(screen, GREEN, (x, y), 5)

    # 판매 지점 표시
    for index, price in sell_points:
        x = index * (screen_width // max_data_points)
        y = center_y - int((price - 300) * y_scale)
        pygame.draw.circle(screen, YELLOW, (x, y), 5)

    # 패널 그리기
    pygame.draw.rect(screen, BLACK, (0, panel_y, screen_width, panel_height))

    # 텍스트 표시
    total_assets = player_money + (len(player_stocks) * stock_data[-1])
    current_price_text = font.render(f"현재가: {stock_data[-1]}", True, WHITE)
    money_text = font.render(f"예수금: {player_money} (총 자산: {total_assets})", True, WHITE)
    stocks_text = font.render(f"보유 주식: {len(player_stocks)} (평균가: {average_price})", True, WHITE)
    turn_text = font.render(f"턴: {current_turn}", True, WHITE)

    screen.blit(current_price_text, (10, panel_y + 10))
    screen.blit(money_text, (10, panel_y + 40))
    screen.blit(stocks_text, (10, panel_y + 70))
    screen.blit(turn_text, (10, 10))

    # 버튼 효과 처리
    current_time = pygame.time.get_ticks()
    if buy_button_shake and current_time - buy_shake_start_time < shake_duration:
        offset = shake_amplitude * (-1 if (current_time // 50) % 2 == 0 else 1)
        screen.blit(buy_button_image, (buy_button_x + offset, buy_button_rect.y))
    elif buy_button_grow and current_time - buy_grow_start_time < grow_duration:
        larger_image = pygame.transform.scale(buy_button_image_original, (button_width + 10, button_height + 10))
        screen.blit(larger_image, buy_button_rect.topleft)
    else:
        screen.blit(buy_button_image, buy_button_rect.topleft)
        buy_button_shake = False
        buy_button_grow = False

    if sell_button_shake and current_time - sell_shake_start_time < shake_duration:
        offset = shake_amplitude * (-1 if (current_time // 50) % 2 == 0 else 1)
        screen.blit(sell_button_image, (sell_button_x + offset, sell_button_rect.y))
    elif sell_button_grow and current_time - sell_grow_start_time < grow_duration:
        larger_image = pygame.transform.scale(sell_button_image_original, (button_width + 10, button_height + 10))
        screen.blit(larger_image, sell_button_rect.topleft)
    else:
        screen.blit(sell_button_image, sell_button_rect.topleft)
        sell_button_shake = False
        sell_button_grow = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
