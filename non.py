import pygame
import random
import sys
import os
import time
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# --- 1. 設定とクラス定義 ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 100, 100)
GREEN = (100, 255, 100)
GOLD = (255, 215, 0)

pygame.init()
pygame.mixer.init()

# 音声ファイルの読み込み（ファイルがない場合はスキップ）
def load_sound(file):
    try:
        return pygame.mixer.Sound(file)
    except:
        return None

snd_attack = load_sound("./ccs.wav")

def play_bgm(file):
    try:
        pygame.mixer.music.load(file)
        pygame.mixer.music.play(-1)
    except:
        print(f"BGM {file} が見つかりません")

class Unit:
    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack_power = attack
        self.defense_power = defense
        self.xp = 0
        self.level = 1
        self.nextlevel = self.level * 100

    def is_alive(self):
        return self.hp > 0

    def attack(self, target):
        base_damage = self.attack_power - target.defense_power
        variance = random.randint(-3, 3) 
        damage = max(1, base_damage + variance)
        target.hp = max(0, target.hp - damage)
        
        if snd_attack:
            snd_attack.play()
        return f"{self.name}の攻撃！ {target.name}に {damage} のダメージ！"
    
    def check_level(self, amount: int) -> list:
        """
        レベルが上がるかどうか判定する
        レベルアップ時ステータスを強化する
        amount: 入手した経験値
        """
        self.xp += amount
        messages = [f"{self.name}は経験値{amount}を獲得した！"]
        while self.xp >= self.nextlevel:
            if self.level >= 99:
                self.xp = self.nextlevel - 1
                break
            self.xp -= self.nextlevel
            self.level += 1
            self.max_hp += 10
            self.hp = self.max_hp
            self.attack_power += 3
            self.defense_power += 2
            self.nextlevel = self.level*100
            messages.append(f"{self.name}はレベル{self.level}に上がった！")
        return messages


class BattleSprite:
    """
    戦闘キャラクターの描画
    """
    def __init__(self, image_path, x, y, size=(100, 100)):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.x = x
        self.y = y
        self.base_x = x
        self.base_y = y
        self.visible = False  # ← 最初は表示しない

        self.shake_timer = 0
        self.shake_power = 8 #  揺れの大きさ

    def show(self):
        self.visible = True

    def hide(self):
        """
        表示を消す（SELECTモードに戻したときなど）
        """
        self.visible = False
        self.x = self.base_x
        self.y = self.base_y

    def hit(self):
        """
        被弾時
        """
        self.shake_timer = 40 #  揺れるフレーム数

    def update(self):
        if self.shake_timer > 0:
            offset = random.randint(-self.shake_power, self.shake_power)
            self.x = self.base_x + offset
            self.shake_timer -= 1
        else:
            self.x = self.base_x

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, (self.x, self.y))

class AttackEffect:
    """
    攻撃エフェクトの描画
    """
    def __init__(self, image_path, x, y, size=(50, 50)):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, size)
        self.x = x
        self.y = y
        self.timer = 0
        self.visible = False

    def play(self):
        self.timer = 40   # 表示フレーム数
        self.visible = True

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.visible = False

    def draw(self, screen):
        if self.visible:
            screen.blit(self.image, (self.x, self.y))



             


def draw_xp_bar(surface: pygame.Surface, unit: Unit, x: int, y: int, bar_width: int = 200, bar_height: int = 10) -> None:
    """
    指定されたUnitの経験値バーを画面に描画する

    引数1 surface: 描画先のPygame Surface
    引数2 unit: xpをもつUnitオブジェクト。
    引数3 x: バーの左上X座標
    引数4 y: バーの左上Y座標
    引数5 bar_width: バーの全体の幅
    引数6 bar_height: バーの高さ
    """
    if unit.nextlevel == 0 or unit.level >= 99:
        ratio = 1.0
    else:
        ratio = unit.xp / unit.nextlevel
    
    xp_color = (150, 150, 255)

    background_rect = pygame.Rect(x, y, bar_width, bar_height)
    pygame.draw.rect(surface, WHITE, background_rect, 1)

    current_width = int(bar_width * ratio)
    xp_rect = pygame.Rect(x, y, current_width, bar_height)
    pygame.draw.rect(surface, xp_color, xp_rect)


def draw_health_bar(surface: pygame.Surface, unit: Unit, x: int, y: int, bar_width: int = 200, bar_height: int = 20) -> None:
    """
    指定されたUnitのHPバーを描画する関数
    
    引数1 surface: 描画先のPygame Surface
    引数2 unit: HPを持つUnitオブジェクト
    引数3 x: バーの左上X座標
    引数4 y: バーの左上Y座標
    引数5 bar_width: バーの全体の幅
    引数6 bar_height: バーの高さ
    """
    
    # HPの割合を計算
    ratio = unit.hp / unit.max_hp
    
    # 描画色を決定（勇者は緑、魔王は赤）
    if unit.name == "勇者":
        bar_color = (0, 255, 0) 
    else:
        bar_color = RED         

    # 1. バーの背景（全体）を描画
    background_rect = pygame.Rect(x, y, bar_width, bar_height)
    pygame.draw.rect(surface, WHITE, background_rect, 1) # 白い枠線
    
    # 2. 現在のHPに応じたバー（中身）を描画
    current_width = int(bar_width * ratio)  
    hp_rect = pygame.Rect(x, y, current_width, bar_height)
    pygame.draw.rect(surface, bar_color, hp_rect)

# --- 2. 画面とフォントの設定 ---
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("テキストバトル RPG 統合版")

font_name = pygame.font.match_font('msgothic', 'meiryo', 'yu gothic')
font = pygame.font.Font(font_name, 20)
small_font = pygame.font.Font(font_name, 14)
big_font = pygame.font.Font(font_name, 48)

# 背景画像の読み込み
bg_file_names = ["fig/nohara.jpg", "fig/mori2.jpg", "fig/maou.jpg"]
bg_images = []
for file_name in bg_file_names:
    try:
        img = pygame.image.load(file_name)
        img = pygame.transform.scale(img, (640, 480))
        bg_images.append(img)
    except:
        surf = pygame.Surface((640, 480))
        surf.fill((30, 30, 30))
        bg_images.append(surf)

# --- 3. ゲーム管理変数 ---
hero = Unit(name="勇者", hp=100, attack=30, defense=10)
demon = None
demon_sprite = BattleSprite("images/go-remu.png", 400, 120)  # 敵のインスタンス生成
hero_sprite = BattleSprite("images/hero.png", 50, 120)  # 勇者のインスタンス生成
slash_effect = AttackEffect("images/slash.png", 380, 180)  # 勇者の攻撃エフェクトのインスタンス生成
slash2_effect = AttackEffect("images/slash2.png", 130, 180)  # 敵の攻撃エフェクトのインスタンス生成
battle_logs = []
mode = 'SELECT' # 'SELECT', 'BATTLE', 'CLEAR'
turn = "PLAYER"
game_over = False
current_stage = 1
MAX_STAGE = 5

def init_battle(stage_num):
    global demon, mode, turn, game_over, current_stage, battle_logs
    current_stage = stage_num
    game_over = False
    turn = "PLAYER"
    mode = 'BATTLE'
    
    # ステージごとの敵設定
    if stage_num == 1:
        demon = Unit("スライム", 150, 15, 5)
    elif stage_num == 2:
        demon = Unit("ゴブリン", 250, 25, 10)
    elif stage_num == 3:
        demon = Unit("キメラ", 500, 40, 15)
    elif stage_num == 4:
        demon = Unit("ゴーレム", 1000, 60, 30)
    elif stage_num == 5:
        demon = Unit("魔王", 5000, 100, 50)
    
    battle_logs = [f"ステージ {stage_num}：{demon.name} が現れた！"]
    play_bgm("./honey.mp3")

# 初期状態
play_bgm("./future.mp3")
battle_logs = ["1-5キーでステージを選択してください。"]


# --- 4. メインループ ---
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            # --- ステージ選択モード ---
            if mode == 'SELECT':
                if event.key == pygame.K_1: init_battle(1)
                elif event.key == pygame.K_2: init_battle(2)
                elif event.key == pygame.K_3: init_battle(3)
                elif event.key == pygame.K_4: init_battle(4)
                elif event.key == pygame.K_5: init_battle(5)
            
            # --- バトルモード ---
            elif mode == 'BATTLE':
                if not game_over:
                    if event.key == pygame.K_SPACE:
                        hero_sprite.show()  # 勇者の呼び出し
                        demon_sprite.show()  # 敵の呼び出し
                        if turn == "PLAYER":
                            msg = hero.attack(demon)
                            demon_sprite.hit()  # 敵が揺れる
                            slash_effect.play()  # 勇者の攻撃エフェクト
                            battle_logs.append(msg)
                            if not demon.is_alive():
                                battle_logs.append(f"{demon.name}を倒した！")
                                xp_messages = hero.check_level(200)
                                battle_logs.extend(xp_messages)
                        
                                if current_stage == 5:
                                    mode = 'CLEAR'
                                    play_bgm("./ccs.wav")
                                else:
                                    game_over = True # Rで戻るか次への待機
                            else:
                                turn = "ENEMY"
                        elif turn =="ENEMY":
                            msg = demon.attack(hero)
                            hero_sprite.hit()  # 勇者が揺れる
                            slash2_effect.play()  # 敵の攻撃エフェクト
                            battle_logs.append(msg)
                            if not hero.is_alive():
                                battle_logs.append("勇者は力尽きた...")
                                mode ="gameover"
                            else:
                                turn = "PLAYER"
                        
                        
                # ゲームオーバー/勝利後の操作
                if game_over and event.key == pygame.K_r:
                    mode = 'SELECT'
                    play_bgm("./future.mp3")
                    battle_logs.append("ステージ選択に戻りました。")
                    # キャラ表示を消す
                    try:
                        hero_sprite.hide()
                        demon_sprite.hide()
                        # エフェクトも停止して非表示にする
                        slash_effect.visible = False
                        slash_effect.timer = 0
                        slash2_effect.visible = False
                        slash2_effect.timer = 0
                    except Exception:
                        pass

            # --- クリアモード ---
                elif mode == 'CLEAR':
                    if event.key in [pygame.K_q, pygame.K_ESCAPE]:
                        running = False

    if mode == 'gameover':
        gameover_text = font.render("GAME OVER", True, RED)
        screen.blit(gameover_text, (250, 200))
        

    # --- 描画セクション ---
    if mode == 'SELECT':
        title = font.render("【 ステージ選択 】", True, RED)
        screen.blit(title, (20, 20))
        opts = [
            "1: スライム (Easy)",
            "2: ゴブリン (Normal)",
            "3: キメラ (Hard)",
            "4: ゴーレム (Very Hard)",
            "5: 魔王 (Hell)"
        ]
        for i, opt in enumerate(opts):
            screen.blit(font.render(opt, True, WHITE), (50, 80 + i*30))
        
        # 勇者の現在ステータス表示
        status = font.render(f"勇者 HP:{hero.max_hp} ATK:{hero.attack_power} DEF:{hero.defense_power}", True, GREEN)
        screen.blit(status, (50, 300))

    elif mode == 'BATTLE':
        # 背景（3ステージ目までは画像、それ以降は最後の画像）
        if current_stage==1:
            bg_idx = 0
        elif current_stage==2:
            bg_idx = 0
        elif current_stage==3:
            bg_idx = 1
        elif current_stage==4:
            bg_idx = 1
        else:
            bg_idx = 2
        screen.blit(bg_images[bg_idx], (0, 0))
        
        # ステータス表示
        pygame.draw.rect(screen, BLACK, (40, 40, 220, 40))
        pygame.draw.rect(screen, BLACK, (380, 40, 220, 40))
        hero_txt = font.render(f"{hero.name} HP: {hero.hp}/{hero.max_hp}", True, WHITE)
        demon_txt = font.render(f"{demon.name} HP: {demon.hp}/{demon.max_hp}", True, RED)
        screen.blit(hero_txt, (50, 50))
        screen.blit(demon_txt, (390, 50))
        draw_health_bar(screen, hero, 50, 80)
        draw_health_bar(screen, demon, 400, 80)
        draw_xp_bar(screen, hero, 50, 100)
        
        # ログウィンドウ
        win_rect = pygame.Rect(50, 300, 540, 150)
        pygame.draw.rect(screen, BLACK, win_rect)
        pygame.draw.rect(screen, WHITE, win_rect, 2)
        
        recent_logs = battle_logs[-4:]
        for i, log in enumerate(recent_logs):
            screen.blit(font.render(log, True, WHITE), (70, 310 + i*30))

    elif mode == 'CLEAR':
        screen.fill(BLACK)
        txt = big_font.render("ALL STAGE CLEAR!", True, GOLD)
        sub = font.render("Good Morning, Hero... (Qで終了)", True, WHITE)
        screen.blit(txt, (txt.get_rect(center=(320, 200))))
        screen.blit(sub, (sub.get_rect(center=(320, 280))))

    # 2. ログの表示（最新の5行だけ表示する）
    # リストの後ろから5つを取得して表示
    recent_logs = battle_logs[-5:] 

    # 3. キャラの表示
    hero_sprite.update()
    demon_sprite.update()
    hero_sprite.draw(screen)
    demon_sprite.draw(screen)
    slash_effect.update()
    slash_effect.draw(screen)
    slash2_effect.update()
    slash2_effect.draw(screen)
    
    # y = 150 # テキストを表示し始めるY座標
    # for log in recent_logs:
    #     text_surface = font.render(log, True, WHITE)
    #     # screen.blit(text_surface, (50, y))
    #     y += 40 # 行間をあける


    

    pygame.display.flip()
    clock.tick(30)

    if mode == 'gameover':
        time.sleep(2)
        break

pygame.quit()
sys.exit()