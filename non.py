import pygame
import random
import sys
import os
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
# --- 1. 設定とクラス定義 ---

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 100, 100)

pygame.mixer.init()
snd = pygame.mixer.Sound("./ccs.wav")
pygame.mixer.music.load("./future.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)


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

        # 攻撃音を再生
        snd.play()
        # ログ用のメッセージを作成して返す
        return f"{self.name}の攻撃！ {target.name}に {damage} のダメージ！"

# --- 2. Pygame初期化 ---
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("テキストバトル RPG")

# 日本語フォントの設定（環境に合わせてフォントを探します）
font_name = pygame.font.match_font('meiryo', 'yu gothic', 'hiragino maru gothic pro')
font = pygame.font.Font(font_name, 24)
# クリア画面用の大きいフォント
big_font = pygame.font.Font(font_name, 48)

# --- 3. ゲームデータの準備 ---
hero = Unit(name="勇者", hp=100, attack=30, defense=10)
demon = Unit(name="敵", hp=250, attack=25, defense=5)

# 戦闘ログ（画面に表示するテキストのリスト）
battle_logs = ["スペースキーを押してバトル開始！"]

turn = "PLAYER" # どちらのターンか
game_over = False

# --- 4. メインループ ---
# モード管理：選択中(SELECT) と バトル中(BATTLE)
stage = None
mode = 'SELECT'  # 'SELECT' or 'BATTLE'
# クリア画面用のタイマー
clear_start_time = None
CLEAR_DURATION_MS = 3000  # 3秒でアプリを終了

# 戦闘ログを初期化（ステージ選択を促す）
battle_logs = ["1/2/3キーでステージを選択してください。"]

running = True
while running:
    screen.fill(BLACK) # 画面をリセット

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
        # クリア画面での即終了キー（QまたはESC）
        if mode == 'CLEAR' and event.type == pygame.KEYDOWN and (event.key == pygame.K_q or event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

        # ステージ選択モード
        if mode == 'SELECT':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    stage = 1
                    demon.max_hp = 150
                    demon.hp = demon.max_hp
                    demon.attack_power = 10
                    demon.defense_power = 5
                    hero.hp = hero.max_hp  # ヒーローを回復して開始
                    battle_logs.append("ステージ1を選択しました（易しい）")
                    mode = 'BATTLE'
                    pygame.mixer.music.load("./honey.mp3")
                    pygame.mixer.music.play(-1)
                elif event.key == pygame.K_2:
                    stage = 2
                    demon.max_hp = 500
                    demon.hp = demon.max_hp
                    demon.attack_power = 30
                    demon.defense_power = 15
                    hero.hp = hero.max_hp
                    battle_logs.append("ステージ2を選択しました（普通）")
                    mode = 'BATTLE'
                    pygame.mixer.music.load("./honey.mp3")
                    pygame.mixer.music.play(-1)

                elif event.key == pygame.K_3:
                    stage = 3
                    demon.max_hp = 1000
                    demon.hp = demon.max_hp
                    demon.attack_power = 100
                    demon.defense_power = 40
                    hero.hp = hero.max_hp
                    battle_logs.append("ステージ3を選択しました（難しい）")
                    mode = 'BATTLE'
                    pygame.mixer.music.load("./honey.mp3")
                    pygame.mixer.music.play(-1)
                    
                elif event.key == pygame.K_4:
                    stage = 4
                    demon.max_hp = 5000
                    demon.hp = demon.max_hp
                    demon.attack_power = 200
                    demon.defense_power = 500
                    hero.hp = hero.max_hp
                    battle_logs.append("ステージ4を選択しました（激ムズ）")
                    mode = 'BATTLE'
                    pygame.mixer.music.load("./honey.mp3")
                    pygame.mixer.music.play(-1)
                elif event.key == pygame.K_5:
                    stage = 5
                    demon.max_hp = 10000
                    demon.hp = demon.max_hp
                    demon.attack_power = 600
                    demon.defense_power = 300
                    hero.hp = hero.max_hp
                    battle_logs.append("ステージ5を選択しました（魔王）")
                    mode = 'BATTLE'
                    pygame.mixer.music.load("./honey.mp3")
                    pygame.mixer.music.play(-1)


        # バトルモード
        elif mode == 'BATTLE':
            # スペースキーが押されたらターンを進める
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not game_over:
                    if turn == "PLAYER":
                        # 勇者の攻撃処理
                        msg = hero.attack(demon)
                        battle_logs.append(msg) # ログに追加

                        if not demon.is_alive():
                            battle_logs.append("魔王を倒した！")
                            if stage == 1:
                                hero.max_hp += 5
                                hero.attack_power += 2
                                hero.defense_power += 1
                                battle_logs.append("勇者のステータスが少し上がった！")
                            elif stage == 2:
                                hero.max_hp += 10
                                hero.attack_power += 5
                                hero.defense_power += 3
                                battle_logs.append("勇者のステータスが上がった！")
                            elif stage == 3:
                                hero.max_hp += 20
                                hero.attack_power += 10
                                hero.defense_power += 5
                                battle_logs.append("勇者のステータスが大きく上がった！")
                            elif stage == 4:
                                hero.max_hp += 30
                                hero.attack_power += 15
                                hero.defense_power += 10
                                battle_logs.append("勇者のステータスが非常に大きく上がった！")
                            elif stage == 5:
                                battle_logs.append("勇者は真の力を手に入れた！")
                                hero.max_hp += 100
                                hero.attack_power += 50
                                hero.defense_power += 25
                                mode = 'CLEAR'
                            game_over = True
                            # クリア画面へ移行
                            clear_start_time = pygame.time.get_ticks()
                            # クリアBGMを再生
                            pygame.mixer.music.load("./ccs.wav")
                            pygame.mixer.music.play(-1)
                        else:
                            turn = "ENEMY" # 相手のターンへ

                    elif turn == "ENEMY":
                        # 魔王の攻撃処理
                        msg = demon.attack(hero)
                        battle_logs.append(msg)

                        if not hero.is_alive():
                            battle_logs.append("勇者は力尽きた...")
                            game_over = True
                        else:
                            turn = "PLAYER" # プレイヤーのターンへ
                else:
                    # ゲームオーバー後の案内（再選択できるようにする）
                    battle_logs.append("ゲーム終了。Rキーで最初に戻り、ステージ選択")
            # ゲームオーバー後にRでリトライ（ステージ選択に戻る）
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                mode = 'SELECT'
                game_over = False
                turn = 'PLAYER'
                # 戻ったら選択BGMに戻す
                try:
                    pygame.mixer.music.load("./future.mp3")
                    pygame.mixer.music.play(-1)
                except Exception:
                    pass
                battle_logs.append("ステージ選択に戻りました。1/2/3キーで選んでください。")

    # --- 描画処理 ---
    # 0. クリア画面の処理
    if mode == 'CLEAR':
        # 画面を全体クリアして大文字で表示
        screen.fill(BLACK)
        ring = pygame.transform.scale(pygame.image.load(f"./ring.jpg"), (200, 200))
        screen.blit(ring, (280, 260))
        tv = pygame.transform.scale(pygame.image.load(f"./tv.jpg"), (200, 200))
        screen.blit(tv, (240, 50))
        violin = pygame.transform.scale(pygame.image.load(f"./violin.jpg"), (200, 200))
        screen.blit(violin, (100, 260))
        clear_text = big_font.render("CLEAR!", True, (255, 215, 0))
        sub_text = font.render("Good Morning, Hero...", True, WHITE)
        clear_rect = clear_text.get_rect(center=(320, 180))
        sub_rect = sub_text.get_rect(center=(320, 240))
        screen.blit(clear_text, clear_rect)
        screen.blit(sub_text, sub_rect)
        pygame.display.flip()
        # 一定時間経過で強制終了
        if clear_start_time is not None and pygame.time.get_ticks() - clear_start_time >= CLEAR_DURATION_MS:
            pass
        # クリア画面のときは通常描画をスキップ
        continue
    
    # 1. ヘッダー/モード表示
    if mode == 'SELECT':
        title_text = font.render("ステージ選択:", True, RED)
        screen.blit(title_text, (20, 20))

        # 選択肢の説明
        info1 = font.render("1: Oh slime(HP150, 攻20, 防5)", True, WHITE)
        info2 = font.render("2: 五分リン♡(HP250, 攻25, 防10)", True, WHITE)
        info3 = font.render("3: ケンタウロス", True, WHITE)
        info4 = font.render("4: ゴーレム(HP400, 攻35, 防15)", True, WHITE)
        info5 = font.render("5: 魔王(⃔ *`꒳´ * )⃕↝(???)", True, WHITE)
        screen.blit(info1, (50, 80))
        screen.blit(info2, (50, 110))
        screen.blit(info3, (50, 140))
        screen.blit(info4, (50, 170))
        screen.blit(info5, (50, 200))

    else: # BATTLE
        hero_text = font.render(f"{hero.name} HP: {hero.hp}/{hero.max_hp}", True, WHITE)
        demon_text = font.render(f"{demon.name} HP: {demon.hp}/{demon.max_hp}", True, RED)
        stage_text = font.render(f"STAGE: {stage}", True, RED)
        screen.blit(hero_text, (50, 50))
        screen.blit(demon_text, (400, 50))
        screen.blit(stage_text, (250, 20))

    # 2. ログの表示（最新の5行だけ表示する）
    recent_logs = battle_logs[-5:]
    y = 260 if mode == 'SELECT' else 150 # 選択画面は下寄せで表示
    for log in recent_logs:
        text_surface = font.render(log, True, WHITE)
        screen.blit(text_surface, (50, y))
        y += 40 # 行間をあける

    # 3. 操作ガイド
    if mode == 'BATTLE' and not game_over:
        guide_text = font.render("[SPACE]でターンを進める", True, (100, 255, 100))
        screen.blit(guide_text, (200, 400))
    elif mode == 'BATTLE' and game_over:
        guide_text = font.render("Rでステージ選択に戻る", True, (255, 200, 100))
        screen.blit(guide_text, (200, 400))

    pygame.display.flip()

pygame.quit()
sys.exit()