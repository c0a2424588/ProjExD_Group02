import pygame
import random
import sys
import os
import time  # 追加
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# --- 1. 設定とクラス定義 ---

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 100, 100)

class Unit:
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack_power = attack
        self.defense_power = defense

    def is_alive(self):
        """生きているかどうかの判定"""
        return self.hp > 0

    def attack(self, target):
        """targetに対して攻撃し、ダメージ計算結果とメッセージを返す"""
        
        # ダメージ計算式： (自分の攻撃力 - 相手の防御力) + 乱数(-3〜+3)
        base_damage = self.attack_power - target.defense_power
        variance = random.randint(-3, 3) 
        damage = base_damage + variance

        # ダメージは最低でも1入るようにする（0やマイナスを防ぐ）
        if damage < 1:
            damage = 1

        # 相手のHPを減らす
        target.hp -= damage
        if target.hp < 0:
            target.hp = 0

        # ログ用のメッセージを作成して返す
        return f"{self.name}の攻撃！ {target.name}に {damage} のダメージ！"

# --- 2. Pygame初期化 ---
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("テキストバトル RPG")

# 背景画像のロード
bg_img = pygame.image.load("fig/nohara.jpg")
bg_img = pygame.transform.scale(bg_img, (640, 480))  # 画面サイズに合わせる
bg_img2 = pygame.image.load("fig/mori2.jpg")
bg_img2 = pygame.transform.scale(bg_img2, (640, 480))
bg_img3 = pygame.image.load("fig/maou.jpg")
bg_img3 = pygame.transform.scale(bg_img3, (640, 480)) 
# 日本語フォントの設定（ドラクエ風にMS Gothicを使用）
font_name = pygame.font.match_font('msgothic', 'meiryo', 'yu gothic')
font = pygame.font.Font(font_name, 20)
small_font = pygame.font.Font(font_name, 14)  # 小さいフォント

# --- 3. ゲームデータの準備関数 ---
def init_game():
    global hero, demon, battle_logs, turn, game_over, game_over_time
    hero = Unit(name="勇者", hp=100, attack=30, defense=10)
    demon = Unit(name="魔王", hp=250, attack=25, defense=5)
    battle_logs = ["スペースキーを押してバトル開始！"]
    turn = "PLAYER"
    game_over = False
    game_over_time = None

init_game()  # 初期化

# --- 4. メインループ ---
while True:
    # ゲームオーバー時は3秒後に終了
    if game_over and game_over_time and time.time() - game_over_time > 1:
        break

    screen.blit(bg_img3, [0, 0])  # 背景画像を描画

    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            break
        
        # スペースキーが押されたらターンを進める
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not game_over:
                if turn == "PLAYER":
                    # 勇者の攻撃処理
                    msg = hero.attack(demon)
                    battle_logs.append(msg) # ログに追加
                    
                    if not demon.is_alive():
                        battle_logs.append("魔王を倒した！")
                        game_over = True
                        game_over_time = time.time()
                    else:
                        turn = "ENEMY" # 相手のターンへ
                
                elif turn == "ENEMY":
                    # 魔王の攻撃処理
                    msg = demon.attack(hero)
                    battle_logs.append(msg)
                    
                    if not hero.is_alive():
                        battle_logs.append("勇者は力尽きた...")
                        game_over = True
                        game_over_time = time.time()
                    else:
                        turn = "PLAYER" # プレイヤーのターンへ

    # --- 描画処理 ---
    if game_over:
        screen.fill(BLACK)  # ゲームオーバー時は黒背景
        # ゲームオーバー画面
        gameover_text = font.render("GAME OVER", True, RED)
        screen.blit(gameover_text, (250, 200))
    else:
        screen.blit(bg_img3, [0, 0])  # 通常時は背景画像
        # 通常の描画
        # 1. ステータス表示（画面上部）
        hero_text = font.render(f"{hero.name} HP: {hero.hp}/{hero.max_hp}", True, WHITE)
        demon_text = font.render(f"{demon.name} HP: {demon.hp}/{demon.max_hp}", True, RED)
        screen.blit(hero_text, (50, 50))
        screen.blit(demon_text, (400, 50))

        # 2. ログの表示（ドラクエ風ウィンドウ内、画面下部）
        # ウィンドウの背景と枠を描画
        window_rect = pygame.Rect(50, 250, 540, 200)  # 下部に移動
        pygame.draw.rect(screen, BLACK, window_rect)  # 背景黒
        pygame.draw.rect(screen, WHITE, window_rect, 2)  # 白い枠
        
        # 最新の5行を表示
        recent_logs = battle_logs[-5:]
        y = 270  # ウィンドウ内の開始Y座標
        for log in recent_logs:
            text_surface = font.render(log, True, WHITE)
            screen.blit(text_surface, (70, y))
            y += 35  # 行間

        # 3. 操作ガイド（右下に小さく表示）
        guide_text = small_font.render("[SPACE]でターンを進める", True, (100, 255, 100))
        screen.blit(guide_text, (450, 450))  # 右下に移動

    pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    pygame.quit()
    sys.exit()