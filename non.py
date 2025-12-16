import pygame
import random
import sys
import os
import time

# 絶対パスを取得し、カレントディレクトリを変更
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- 1. 設定とクラス定義 ---

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
GREEN = (100, 255, 100) # 操作ガイドの色

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

# **背景画像データの準備**
# ファイル名リスト。ステージ1: nohara.jpg, ステージ2: mori2.jpg, ステージ3: maou.jpg
bg_file_names = ["fig/nohara.jpg", "fig/mori2.jpg", "fig/maou.jpg"]
bg_images = []
for file_name in bg_file_names:
    try:
        img = pygame.image.load(file_name)
        img = pygame.transform.scale(img, (640, 480)) # 画面サイズに合わせる
        bg_images.append(img)
    except pygame.error as e:
        print(f"背景画像のロードに失敗しました: {file_name}")
        # ロード失敗時はダミーの真っ黒な画像を追加
        dummy_surface = pygame.Surface((640, 480))
        dummy_surface.fill(BLACK)
        bg_images.append(dummy_surface)
        
# **ステージの総数**
MAX_STAGE = len(bg_images)

# 日本語フォントの設定（ドラクエ風にMS Gothicを使用）
font_name = pygame.font.match_font('msgothic', 'meiryo', 'yu gothic')
font = pygame.font.Font(font_name, 20)
small_font = pygame.font.Font(font_name, 14) # 小さいフォント

# --- 3. ゲームデータの準備関数 ---
def init_game(stage=1):
    """
    ゲームデータを初期化する。ステージレベルに応じて敵のステータスを変更。
    :param stage: 開始するステージのレベル (1, 2, 3...)
    """
    global hero, demon, battle_logs, turn, game_over, game_clear, game_over_time, stage_level
    
    stage_level = stage
    game_over = False
    game_clear = False
    game_over_time = None
    
    # 勇者は固定
    hero = Unit(name="勇者", hp=100, attack=30, defense=10)
    
    # ステージレベルに応じた魔王（敵）のステータス設定
    if stage_level == 1:
        demon = Unit(name="スライム魔王", hp=30, attack=10, defense=5)
        battle_logs = [f"ステージ {stage_level}：{demon.name} が現れた！", "スペースキーを押してバトル開始！"]
    elif stage_level == 2:
        demon = Unit(name="ドラゴン魔王", hp=100, attack=20, defense=8)
        battle_logs = [f"ステージ {stage_level}：{demon.name} が現れた！", "スペースキーを押してバトル開始！"]
    elif stage_level == 3:
        demon = Unit(name="真の魔王", hp=250, attack=30, defense=10)
        battle_logs = [f"ステージ {stage_level}：{demon.name} が現れた！", "スペースキーを押してバトル開始！"]
    else:
        # 予期せぬステージレベルの場合は終了処理へ
        game_clear = True
        game_over = True
        battle_logs = ["すべての魔王を打ち破った！"]


    turn = "PLAYER"

# 最初の初期化（ステージ1から開始）
init_game(stage=1)

# --- 4. メインループ ---
while True:
    # ゲームオーバー/ゲームクリア時は3秒後に終了
    if (game_over or game_clear) and game_over_time and time.time() - game_over_time > 3:
        # 全ステージクリア時はここでブレイクしない
        if stage_level > MAX_STAGE or not hero.is_alive():
            break
        
        # ステージクリアで次のステージがある場合
        if stage_level < MAX_STAGE and hero.is_alive():
            init_game(stage=stage_level + 1)
            continue # ループの最初に戻って新しいステージを開始

    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # スペースキーが押されたらターンを進める
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            # ゲームオーバーやステージクリア判定後、次のステージへの移行中は操作を受け付けない
            if not game_over and not game_clear:
                
                if turn == "PLAYER":
                    # 勇者の攻撃処理
                    msg = hero.attack(demon)
                    battle_logs.append(msg) # ログに追加
                    
                    if not demon.is_alive():
                        battle_logs.append(f"ステージ {stage_level} の魔王を倒した！")
                        # 最終ステージでなければステージクリア
                        if stage_level < MAX_STAGE:
                            battle_logs.append(f"ステージ {stage_level+1} へ進む準備中...")
                            game_clear = True
                        else:
                            battle_logs.append("すべての魔王を打ち破った！勇者の勝利！")
                            game_clear = True
                        
                        game_over = True # ステージクリアも一旦 game_over=True で時間経過を制御
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
    screen.fill(BLACK) # 背景を一旦黒でクリア
    
    # 描画する背景画像を選択（リストのインデックスは stage_level - 1）
    if 1 <= stage_level <= MAX_STAGE:
        screen.blit(bg_images[stage_level - 1], [0, 0])
    
    if game_over and not hero.is_alive():
        # 勇者が負けた場合
        # ゲームオーバー画面
        gameover_text = font.render("GAME OVER", True, RED)
        screen.blit(gameover_text, (250, 200))
        # ログ表示ウィンドウはそのまま残す
        
    elif game_clear:
        # 勇者が勝った場合（最終ステージクリア、または次のステージへの移行待ち）
        if stage_level >= MAX_STAGE:
            # 完全勝利
            clear_text = font.render("全ステージクリア！", True, GREEN)
            screen.blit(clear_text, (230, 200))
        else:
            # ステージクリア
            clear_text = font.render(f"ステージ {stage_level} CLEAR！", True, GREEN)
            screen.blit(clear_text, (230, 200))
            next_text = small_font.render(f"ステージ {stage_level+1} へ...", True, WHITE)
            screen.blit(next_text, (260, 250))
        
    else:
        # 通常の描画
        # 1. ステータス表示（画面上部）
        hero_text = font.render(f"{hero.name} HP: {hero.hp}/{hero.max_hp}", True, WHITE)
        demon_text = font.render(f"{demon.name} HP: {demon.hp}/{demon.max_hp}", True, RED)
        stage_text = font.render(f"STAGE {stage_level}", True, WHITE)
        screen.blit(hero_text, (50, 50))
        screen.blit(demon_text, (400, 50))
        screen.blit(stage_text, (280, 10))

        # 2. ログの表示（ドラクエ風ウィンドウ内、画面下部）
        # ウィンドウの背景と枠を描画
        window_rect = pygame.Rect(50, 300, 540, 150) # サイズと位置を調整
        pygame.draw.rect(screen, BLACK, window_rect) # 背景黒
        pygame.draw.rect(screen, WHITE, window_rect, 2) # 白い枠
        
        # 最新の4行を表示
        recent_logs = battle_logs[-4:]
        y = 310 # ウィンドウ内の開始Y座標
        for log in recent_logs:
            text_surface = font.render(log, True, WHITE)
            screen.blit(text_surface, (70, y))
            y += 30 # 行間

        # 3. 操作ガイド（右下に小さく表示）
        guide_text = small_font.render("[SPACE]でターンを進める", True, GREEN)
        screen.blit(guide_text, (450, 460)) # 右下に移動

    pygame.display.flip()

# メインループ終了後の処理
pygame.quit()
sys.exit()