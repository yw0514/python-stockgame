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

# 타이머 설정
clock = pygame.time.Clock()
graph_update_event = pygame.USEREVENT + 1
event_change_event = pygame.USEREVENT + 2  # 이벤트 변경 타이머
pygame.time.set_timer(graph_update_event, 1000)
pygame.time.set_timer(event_change_event, 10000)  # 10초마다 이벤트 변경

# 주식 데이터 초기화
stock_data = [random.randint(200, 400)]
max_data_points = 50
y_scale = 1.0

# 플레이어 상태
player_money = 300
player_stocks = []
average_price = 0

# 버튼 효과 관련 변수
buy_button_shake = False
sell_button_shake = False
buy_shake_start_time = 0
sell_shake_start_time = 0
shake_duration = 200  # 흔들림 지속 시간
shake_amplitude = 5   # 흔들림 크기

buy_button_grow = False
sell_button_grow = False
buy_grow_start_time = 0
sell_grow_start_time = 0
grow_duration = 150  # 버튼 크기 변화 지속 시간

# 이벤트 상태
current_event = "기본"  # 현재 이벤트 상태
events = {
    "기본": {"effect": lambda: random.randint(-40, 40), "description": "일반적인 변동"},
    "급등": {"effect": lambda: random.randint(-20, 60), "description": "주가가 상승할 가능성이 큼"},
    "급락": {"effect": lambda: random.randint(-60, 20), "description": "주가가 하락할 가능성이 큼"}
}

# 구매 지점 기록 리스트
buy_points = []  # 구매 지점을 저장 (index, price)

# 평균 가격 계산 함수
def calculate_average_price():
    if not player_stocks:
        return 0
    return sum(player_stocks) // len(player_stocks)

# 이벤트 변경 함수
def change_event():
    global current_event
    available_events = list(events.keys())
    available_events.remove(current_event)
    current_event = random.choice(available_events)
    print(f"이벤트 변경: {current_event} - {events[current_event]['description']}")

# 게임 루프 실행 플래그
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if buy_button_rect.collidepoint(event.pos):
                if stock_data and player_money >= stock_data[-1]:
                    player_money -= stock_data[-1]
                    player_stocks.append(stock_data[-1])
                    average_price = calculate_average_price()
                    buy_points.append((len(stock_data) - 1, stock_data[-1]))  # 구매 지점 저장
                    print(f"매수 완료! 현재 평균가: {average_price}")
                    buy_button_grow = True
                    buy_grow_start_time = pygame.time.get_ticks()
                else:
                    print("매수 실패: 돈이 부족합니다.")
                    buy_button_shake = True
                    buy_shake_start_time = pygame.time.get_ticks()

            elif sell_button_rect.collidepoint(event.pos):
                if stock_data and player_stocks:
                    player_money += stock_data[-1]
                    player_stocks.pop(0)
                    average_price = calculate_average_price()
                    print(f"매도 완료! 현재 평균가: {average_price}")
                    sell_button_grow = True
                    sell_grow_start_time = pygame.time.get_ticks()
                else:
                    print("매도 실패: 보유 주식이 없습니다.")
                    sell_button_shake = True
                    sell_shake_start_time = pygame.time.get_ticks()

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                y_scale = min(y_scale + 0.1, 2.0)
            elif event.y < 0:
                y_scale = max(y_scale - 0.1, 0.5)

        elif event.type == graph_update_event:
            # 주가 변경
            price_change = events[current_event]["effect"]()
            new_price = stock_data[-1] + price_change
            new_price = max(100, min(new_price, 500))
            stock_data.append(new_price)
            if len(stock_data) > max_data_points:
                stock_data.pop(0)
                buy_points = [(i - 1, price) for i, price in buy_points if i > 0]  # 그래프 이동에 따른 구매 지점 업데이트

            # 최고가/최저가 도달 시
            if new_price == 500:
                print("최고가에 도달했습니다! 이벤트를 변경합니다.")
                change_event()
            elif new_price == 100:
                print("최저가에 도달했습니다! 이벤트를 변경합니다.")
                change_event()

        elif event.type == event_change_event:
            # 일반적인 상황에서 이벤트 변경
            print("일반적인 상황에서 이벤트를 변경합니다.")
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

        if stock_data[i] > stock_data[i - 1]:
            color = RED
            rect_y = y2
            rect_height = y1 - y2
        else:
            color = BLUE
            rect_y = y1
            rect_height = y2 - y1

        pygame.draw.rect(screen, color, (x2 - 5, rect_y, 10, rect_height))  # 네모 그래프
        pygame.draw.line(screen, ORANGE, (x1, y1), (x2, y2), 2)  # 선 그래프

    # 구매 지점 표시
    for index, price in buy_points:
        x = index * (screen_width // max_data_points)
        y = center_y - int((price - 300) * y_scale)
        pygame.draw.circle(screen, GREEN, (x, y), 5)

    # 패널 그리기
    pygame.draw.rect(screen, BLACK, (0, panel_y, screen_width, panel_height))

    # 텍스트 표시
    current_price_text = font.render(f"현재가: {stock_data[-1]}", True, WHITE)
    screen.blit(current_price_text, (10, panel_y + 10))

    money_text = font.render(f"보유 금액: {player_money}", True, WHITE)
    screen.blit(money_text, (10, panel_y + 40))

    stocks_text = font.render(f"보유 주식: {len(player_stocks)} (평균가: {average_price})", True, WHITE)
    screen.blit(stocks_text, (10, panel_y + 70))

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
