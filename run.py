import pygame
import random
import sys

# --- 定数の設定 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 200, 50)  # プレイヤー
RED   = (200, 50, 50)  # 障害物
BLUE  = (135, 206, 235) # 空の色

# --- プレイヤー（自キャラ）クラス ---
class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = 100
        self.y = SCREEN_HEIGHT - self.height - 20 # 地面の上に配置
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # ジャンプ関連の変数
        self.y_velocity = 0
        self.jump_power = -15 # ジャンプ力（上に移動するのでマイナス）
        self.gravity = 0.8    # 重力（下に引っ張る力）
        self.is_jumping = False
        self.ground_y = SCREEN_HEIGHT - self.height - 20

    def jump(self):
        # 地面にいるときだけジャンプできる
        if not self.is_jumping:
            self.y_velocity = self.jump_power
            self.is_jumping = True

    def update(self):
        # 重力を速度に加算
        self.y_velocity += self.gravity
        # 速度を座標に加算（落下または上昇）
        self.rect.y += int(self.y_velocity)

        # 地面より下に行かないようにする処理
        if self.rect.y >= self.ground_y:
            self.rect.y = self.ground_y
            self.is_jumping = False
            self.y_velocity = 0

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)

# --- ゲームの初期化 ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("シンプルランゲーム")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36) # スコア表示用のフォント

# --- ゲーム変数の準備 ---
player = Player()
obstacles = [] # 障害物を入れるリスト
spawn_timer = 0
score = 0
game_over = False

running = True
while running:
    # 1. イベント処理（キー入力など）
    for event in pygame.event.get():
        if event.type == pygame.quit:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_over:
                    player.jump()
                else:
                    # ゲームオーバー時にスペースでリセット
                    player = Player()
                    obstacles = []
                    score = 0
                    game_over = False

    # 2. ゲームロジックの更新
    if not game_over:
        # プレイヤーの更新（重力計算など）
        player.update()

        # 障害物の生成（一定時間ごとに作成）
        spawn_timer += 1
        # 60フレーム～120フレームの間隔でランダムに生成
        if spawn_timer > random.randint(60, 120):
            obstacle_height = random.randint(30, 70)
            # 画面の右端(SCREEN_WIDTH)に作成
            obstacle_rect = pygame.Rect(SCREEN_WIDTH, SCREEN_HEIGHT - obstacle_height - 20, 30, obstacle_height)
            obstacles.append(obstacle_rect)
            spawn_timer = 0

        # 障害物の移動と削除
        for obs in obstacles[:]: # リストをコピーしてループ
            obs.x -= 6 # 左へ移動するスピード
            if obs.x < -50: # 画面外に出たら消す
                obstacles.remove(obs)
                score += 1 # 避けたのでスコア加算

        # 当たり判定
        # プレイヤーの矩形と、障害物リスト内のどれかが重なったらTrue
        for obs in obstacles:
            if player.rect.colliderect(obs):
                game_over = True

    # 3. 描画処理
    screen.fill(BLUE) # 空の色で塗りつぶし

    # 地面の描画
    pygame.draw.rect(screen, (100, 100, 100), (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))

    # キャラと障害物の描画
    player.draw(screen)
    for obs in obstacles:
        pygame.draw.rect(screen, RED, obs)

    # UIの描画
    if game_over:
        text = font.render(f"GAME OVER! Score: {score} [Press SPACE]", True, BLACK)
        screen.blit(text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2))
    else:
        text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(FPS) # 60FPSに固定

pygame.quit()
sys.exit()