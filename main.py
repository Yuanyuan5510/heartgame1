import time
import pygame
import random
import sys
import math


def read_and_validate_number(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read().strip()
            try:
                a = int(content)
            except ValueError:
                print("错误：文件内容不是有效的整数。")
                input("按回车键退出...")
                return None

            if 1 <= a <= 351:
                return a
            else:
                print(f"错误：数字 {a} 不在1-351的范围内。")
                input("按回车键退出...")
                return None

    except FileNotFoundError:
        print(f"错误：找不到文件 '{file_path}'。")
        input("按回车键退出...")
        return None
    except Exception as e:
        print(f"错误：发生未知错误 - {e}")
        input("按回车键退出...")
        return None


# 直接执行代码
file_path = "assets//sprites//number.txt"  # 请替换为实际文件路径
a = read_and_validate_number(file_path)

if a is not None:
    print(f"成功！变量 a 的值为: {a}")
if a is None:
    sys.exit()
# 初始化pygame
pygame.init()

# 确保中文显示正常
pygame.font.init()
try:
    font = pygame.font.Font("simhei.ttf", 24)  # 尝试加载系统中的黑体字
except:
    # 如果找不到指定字体，使用系统默认字体
    font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 24)

# 游戏窗口设置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("传说之下 - Sans战")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
HEART_RED = (255, 50, 50)  # 心形的红色

# 游戏状态
GAME_STATES = {
    'START': 0,
    'BATTLE': 1,
    'DIALOGUE': 2,
    'VICTORY': 3,
    'GAME_OVER': 4
}

# 攻击模式
ATTACK_PATTERNS = {
    'BASIC': 0,  # 基础水平和垂直攻击
    'CROSS': 1,  # 十字交叉攻击
    'CIRCLE': 2,  # 环形攻击
    'WAVE': 3,  # 波浪形攻击
    'SPEED': 4,  # 高速弹幕攻击
    'SPIRAL': 5,  # 螺旋攻击
    'RAIN': 6,  # 雨滴攻击
    'GUN': 7,  # 龙骨炮攻击
    'DROPLET': 8  # 水滴攻击
}


# 绘制心形函数
def draw_heart(surface, x, y, size, color):
    points = []
    for t in range(0, 360, 5):
        rad = math.radians(t)
        heart_x = 16 * math.pow(math.sin(rad), 3)
        heart_y = 13 * math.cos(rad) - 5 * math.cos(2 * rad) - 2 * math.cos(3 * rad) - math.cos(4 * rad)
        points.append((x + heart_x * size / 20, y - heart_y * size / 20))  # 注意y坐标是减号，因为屏幕坐标系向下为正

    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, color, points)


# 玩家类
class Player:
    def __init__(self):
        self.width, self.height = 20, 20
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT // 2 - self.height // 2
        self.speed = 5
        self.invincible = False
        self.invincible_time = 0
        self.max_invincible_time = 360  # 3秒无敌时间(60fps * 3)
        self.health = a  # 初始血量
        self.max_health = a  # 最大血量
        # 初始化 rect 属性
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.speed

        # 更新 rect 的位置
        self.rect.x = self.x
        self.rect.y = self.y

        # 更新无敌状态
        if self.invincible:
            self.invincible_time += 1
            if self.invincible_time >= self.max_invincible_time:
                self.invincible = False
                self.invincible_time = 0

    def draw(self, surface):
        # 无敌状态闪烁效果
        if not self.invincible or (self.invincible and self.invincible_time % 10 < 5):
            draw_heart(surface, self.x + self.width // 2, self.y + self.height // 2, self.width, HEART_RED)

        # 绘制血量条
        self.draw_health_bar(surface)

    def draw_health_bar(self, surface):
        # 血量条背景
        health_bar_bg = pygame.Rect(10, 10, 100, 10)
        pygame.draw.rect(surface, RED, health_bar_bg)

        # 当前血量
        health_width = int(100 * (self.health / self.max_health))
        health_bar = pygame.Rect(10, 10, health_width, 10)
        pygame.draw.rect(surface, GREEN, health_bar)

        # 血量文字
        health_text = font.render(f"HP: {self.health}/{self.max_health}", True, WHITE)
        surface.blit(health_text, (120, 8))

    def hit(self):
        if not self.invincible:
            self.health -= 5  # 被击中扣5血
            self.invincible = True
            self.invincible_time = 0

            # 检查游戏是否结束
            if self.health <= 0:
                return True  # 返回True表示游戏结束

        return False  # 返回False表示游戏继续


# 骨弹类
class Bone:
    def __init__(self, x, y, width, height, direction, color=WHITE, speed=5):
        self.rect = pygame.Rect(x, y, width, height)
        self.direction = direction  # 'horizontal', 'vertical', 'diagonal_up', 'diagonal_down'
        self.speed = speed
        self.color = color
        self.active = True

    def update(self):
        if self.active:
            if self.direction == 'horizontal':
                self.rect.x -= self.speed
            elif self.direction == 'vertical':
                self.rect.y += self.speed
            elif self.direction == 'diagonal_up':
                self.rect.x -= self.speed
                self.rect.y -= self.speed
            elif self.direction == 'diagonal_down':
                self.rect.x -= self.speed
                self.rect.y += self.speed

            # 检查是否超出屏幕
            if (self.rect.x < -50 or self.rect.y > HEIGHT + 50 or
                    self.rect.x > WIDTH + 50 or self.rect.y < -50):
                self.active = False

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, self.color, self.rect)

    def is_active(self):
        return self.active


# 特殊弹幕类 - 环形弹幕
class CircleBone:
    def __init__(self, center_x, center_y, radius, angle, width=10, height=40, speed=3):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.angle = angle
        self.width = width
        self.height = height
        self.speed = speed
        self.color = WHITE
        self.active = True
        self.update_position()

    def update_position(self):
        # 计算圆周上的位置
        self.x = self.center_x + self.radius * pygame.math.Vector2(1, 0).rotate(self.angle).x
        self.y = self.center_y + self.radius * pygame.math.Vector2(1, 0).rotate(self.angle).y
        self.rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)

    def update(self):
        if self.active:
            self.angle = (self.angle + self.speed) % 360
            self.update_position()

            # 检查是否超出屏幕太远
            if (self.x < -100 or self.y < -100 or
                    self.x > WIDTH + 100 or self.y > HEIGHT + 100):
                self.active = False

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, self.color, self.rect)

    def is_active(self):
        return self.active


# 龙骨炮类
class GasterBlaster:
    def __init__(self, x, y, width, height, speed=5):
        # 限制方框范围
        limit_width = WIDTH * 4 // 5
        limit_height = HEIGHT * 4 // 5
        limit_x = (WIDTH - limit_width) // 2
        limit_y = (HEIGHT - limit_height) // 2
        self.rect = pygame.Rect(max(x, limit_x), max(y, limit_y), width, height)
        self.speed = speed
        self.color = PURPLE
        self.active = True

    def update(self):
        if self.active:
            self.rect.y += self.speed
            limit_width = WIDTH * 4 // 5
            limit_height = HEIGHT * 4 // 5
            limit_x = (WIDTH - limit_width) // 2
            limit_y = (HEIGHT - limit_height) // 2
            if self.rect.y > limit_y + limit_height + 50:
                self.active = False

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, self.color, self.rect)

    def is_active(self):
        return self.active


# 水滴类
class Droplet:
    def __init__(self, x, y, width, height, speed=5):
        self.rect = pygame.Rect(x, y, width, height)
        self.speed = speed
        self.color = BLUE
        self.active = True

    def update(self):
        if self.active:
            self.rect.y += self.speed
            if self.rect.y > HEIGHT + 50:
                self.active = False

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, self.color, self.rect)

    def is_active(self):
        return self.active


# Sans类
class Sans:
    def __init__(self):
        self.width, self.height = 60, 80
        self.x = WIDTH // 2 - self.width // 2
        self.y = 100
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color = BLACK
        self.bones = []
        self.circle_bones = []
        self.gaster_blasters = []
        self.droplets = []
        self.teleport_timer = 0
        self.teleport_cooldown = 60  # 帧数
        self.shoot_timer = 0
        self.shoot_cooldown = 30  # 帧数
        self.attack_pattern = ATTACK_PATTERNS['BASIC']
        self.attack_timer = 0
        self.attack_duration = 300  # 每种攻击模式持续的帧数
        self.current_phase = 1  # 战斗阶段
        self.total_phases = 3  # 总战斗阶段
        self.mercy_tested = False  # 是否尝试过仁慈

    def update(self, player, difficulty_multiplier, mercy_count):
        # 瞬移逻辑
        self.teleport_timer += 1
        if self.teleport_timer >= self.teleport_cooldown:
            self.teleport()
            self.teleport_timer = 0

        # 更新攻击计时器
        self.attack_timer += 1
        if self.attack_timer >= self.attack_duration:
            self.change_attack_pattern()
            self.attack_timer = 0

        # 发射骨弹
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_cooldown / difficulty_multiplier:
            self.shoot(player)
            self.shoot_timer = 0

        # 更新骨弹
        for bone in self.bones[:]:
            bone.update()
            if not bone.is_active():
                self.bones.remove(bone)

        # 更新环形骨弹
        for circle_bone in self.circle_bones[:]:
            circle_bone.update()
            if not circle_bone.is_active():
                self.circle_bones.remove(circle_bone)

        # 更新龙骨炮
        for gaster_blaster in self.gaster_blasters[:]:
            gaster_blaster.update()
            if not gaster_blaster.is_active():
                self.gaster_blasters.remove(gaster_blaster)

        # 更新水滴
        for droplet in self.droplets[:]:
            droplet.update()
            if not droplet.is_active():
                self.droplets.remove(droplet)

        # 根据阶段改变行为
        self.update_phase(mercy_count)

    def teleport(self):
        # 瞬移到随机位置
        self.x = random.randint(50, WIDTH - 50 - self.width)
        self.rect.x = self.x

    def shoot(self, player):
        # 根据当前攻击模式发射骨弹
        if self.attack_pattern == ATTACK_PATTERNS['BASIC']:
            self.shoot_basic()
        elif self.attack_pattern == ATTACK_PATTERNS['CROSS']:
            self.shoot_cross()
        elif self.attack_pattern == ATTACK_PATTERNS['CIRCLE']:
            self.shoot_circle()
        elif self.attack_pattern == ATTACK_PATTERNS['WAVE']:
            self.shoot_wave()
        elif self.attack_pattern == ATTACK_PATTERNS['SPEED']:
            self.shoot_speed(player)
        elif self.attack_pattern == ATTACK_PATTERNS['SPIRAL']:
            self.shoot_spiral()
        elif self.attack_pattern == ATTACK_PATTERNS['RAIN']:
            self.shoot_rain()
        elif self.attack_pattern == ATTACK_PATTERNS['GUN']:
            self.shoot_gun(player)
        elif self.attack_pattern == ATTACK_PATTERNS['DROPLET']:
            self.shoot_droplet()

    def shoot_basic(self):
        # 发射水平骨弹
        for i in range(5):
            bone = Bone(WIDTH, HEIGHT // 2 + i * 30, 50, 10, 'horizontal')
            self.bones.append(bone)

        # 发射垂直骨弹
        for i in range(5):
            bone = Bone(WIDTH // 4 + i * 40, 0, 10, 50, 'vertical')
            self.bones.append(bone)

    def shoot_cross(self):
        # 发射对角线骨弹
        for i in range(4):
            bone1 = Bone(WIDTH, i * 100 + 50, 50, 10, 'diagonal_up')
            bone2 = Bone(WIDTH, i * 100 + 100, 50, 10, 'diagonal_down')
            self.bones.append(bone1)
            self.bones.append(bone2)

    def shoot_circle(self):
        # 清空旧的环形骨弹
        self.circle_bones = []

        # 创建新的环形骨弹
        for i in range(12):
            angle = i * 30
            circle_bone = CircleBone(WIDTH // 2, HEIGHT // 2, 200, angle)
            self.circle_bones.append(circle_bone)

    def shoot_wave(self):
        # 发射波浪形骨弹
        color = random.choice([WHITE, RED, BLUE, GREEN])
        for i in range(8):
            x = WIDTH + i * 100
            y = HEIGHT // 2 + 100 * (i % 2)
            bone = Bone(x, y, 50, 10, 'horizontal', color, speed=7)
            self.bones.append(bone)

    def shoot_speed(self, player):
        # 向玩家位置发射高速骨弹
        color = ORANGE
        speed = 10

        # 水平方向
        bone1 = Bone(WIDTH, player.y + player.height // 2 - 5, 50, 10, 'horizontal', color, speed)
        self.bones.append(bone1)

        # 垂直方向
        bone2 = Bone(player.x + player.width // 2 - 5, 0, 10, 50, 'vertical', color, speed)
        self.bones.append(bone2)

    def shoot_spiral(self):
        # 发射螺旋形骨弹
        base_angle = self.attack_timer * 2  # 基于攻击时间的基础角度
        for i in range(8):
            angle = base_angle + i * 45
            speed = 5
            x = WIDTH // 2
            y = HEIGHT // 2

            # 计算方向向量
            dir_x = math.cos(math.radians(angle))
            dir_y = math.sin(math.radians(angle))

            # 创建骨弹
            bone = Bone(x, y, 40, 10, 'custom')
            bone.dir_x = dir_x
            bone.dir_y = dir_y
            bone.speed = speed
            self.bones.append(bone)

    def shoot_rain(self):
        # 发射雨滴式骨弹
        color = BLUE
        for i in range(10):
            x = random.randint(0, WIDTH)
            bone = Bone(x, -50, 10, 40, 'vertical', color, speed=6)
            self.bones.append(bone)

    def shoot_gun(self, player):
        # 发射龙骨炮
        width = 50
        height = 400
        speed = 6
        gaster_blaster = GasterBlaster(player.x + player.width // 2 - width // 2, 0, width, height, speed)
        self.gaster_blasters.append(gaster_blaster)

    def shoot_droplet(self):
        # 发射水滴攻击
        width = 5
        height = 10
        speed = 7
        for i in range(5):
            x = random.randint(0, WIDTH)
            droplet = Droplet(x, -50, width, height, speed)
            self.droplets.append(droplet)

    def change_attack_pattern(self):
        # 随机选择新的攻击模式
        if self.current_phase == 1:
            # 第一阶段只使用前4种攻击模式
            available_patterns = list(range(4))
        elif self.current_phase == 2:
            # 第二阶段添加高速弹幕
            available_patterns = list(range(5))
        else:
            # 第三阶段添加所有攻击模式
            available_patterns = list(range(len(ATTACK_PATTERNS)))

        # 避免连续两次使用相同的攻击模式
        new_pattern = random.choice([p for p in available_patterns if p != self.attack_pattern])
        self.attack_pattern = new_pattern

    def update_phase(self, mercy_count):
        if mercy_count <= 2:
            self.current_phase = 1
            self.teleport_cooldown = 60
            self.shoot_cooldown = 30
        elif 3 <= mercy_count < 5:
            self.current_phase = 2
            self.teleport_cooldown = 40
            self.shoot_cooldown = 25
        else:
            self.current_phase = 3
            self.teleport_cooldown = 30
            self.shoot_cooldown = 20
        # 强制切换攻击模式
        self.change_attack_pattern()

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

        # 绘制骨弹
        for bone in self.bones:
            bone.draw(surface)

        # 绘制环形骨弹
        for circle_bone in self.circle_bones:
            circle_bone.draw(surface)

        # 绘制龙骨炮
        for gaster_blaster in self.gaster_blasters:
            gaster_blaster.draw(surface)

        # 绘制水滴
        for droplet in self.droplets:
            droplet.draw(surface)

        # 显示当前阶段
        phase_text = font.render(f"阶段: {self.current_phase}/{self.total_phases}", True, WHITE)
        surface.blit(phase_text, (10, 40))


# 对话系统
class DialogueSystem:
    def __init__(self, sound_manager):
        self.font = font
        self.sound_manager = sound_manager
        self.dialogues = {
            'START': [
                "（sans拒接了你的仁慈）",
                "花儿在绽放，鸟儿在歌唱。",
                "在这美好的一天里像你这样的孩子应该在地狱",
                "准备好了吗？让我们开始吧。"
            ],
            'PHASE_1': [
                "不错嘛，继续保持。",
                "这种程度可不够哦。",
                "你以为这就结束了？"
            ],
            'PHASE_2': [
                "哈哈，有点意思。",
                "看来我得认真点了。",
                "你很有决心，我喜欢。"
            ],
            'PHASE_3': [
                "终于认真起来了吗？",
                "别以为能轻易通过这里。",
                "让我看看你的极限在哪里。"
            ],
            'MERCY_SUCCESS': [
                "好吧，你赢了...",
                "你很特别，不是吗？",
                "你走吧，别再回来了。"
            ],
            'MERCY_FAIL': [
                "哈哈仁慈我，你以为这样就能结束了？",
                "太天真了！",
                "准备好继续了吗？（按空格继续）"
            ],
            'VICTORY': [
                "做得好，你赢了。",
                "真没想到你能坚持到现在。",
                "好吧，你可以通过了。"
            ],
            'GAME_OVER': [
                "哈哈，看来你还不够强。",
                "再来一次怎么样？",
                "也许下次你能做得更好。"
            ]
        }
        self.current_dialogue = 0
        self.current_section = 'START'
        self.display_time = 0
        self.display_duration = 180  # 帧数
        self.showing = False

    def start_section(self, section):
        self.current_section = section
        self.current_dialogue = 0
        self.display_time = 0
        self.showing = True
        if section in self.dialogues:
            self.sound_manager.play_dialogue_sound()

    def update(self):
        if not self.showing:
            return

        self.display_time += 1
        if self.display_time >= self.display_duration:
            if self.current_dialogue < len(self.dialogues.get(self.current_section, [])) - 1:
                self.current_dialogue += 1
                self.display_time = 0
                self.sound_manager.play_dialogue_sound()
            else:
                self.showing = False

    def draw(self, surface):
        if not self.showing or self.current_section not in self.dialogues:
            return

        # 绘制对话框
        dialogue_box = pygame.Rect(50, HEIGHT - 150, WIDTH - 100, 100)
        pygame.draw.rect(surface, BLACK, dialogue_box)
        pygame.draw.rect(surface, WHITE, dialogue_box, 2)  # 边框

        # 绘制对话文本
        text = self.font.render(self.dialogues[self.current_section][self.current_dialogue], True, WHITE)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 100))
        surface.blit(text, text_rect)


# 音效管理器
class SoundManager:
    def __init__(self):
        self.music_playing = False
        self.current_sound = None  # 当前播放的音效
        self.music_paused = False  # 背景音乐是否暂停
        self.load_sounds()

    def load_sounds(self):
        try:
            # 加载音效（这些应该替换为实际的音效文件）
            self.hit_sound = pygame.mixer.Sound("assets//fonts//mus_dooropen.ogg")
            self.shoot_sound = pygame.mixer.Sound("assets//fonts//mus_doorclose.ogg")
            self.teleport_sound = pygame.mixer.Sound("assets//fonts//mus_coolbeat.ogg")
            self.dialogue_sound = pygame.mixer.Sound("assets//fonts//mus_smallshock.ogg")
            self.victory_sound = pygame.mixer.Sound("assets//fonts//mus_bergentruckung.ogg")
            self.game_over_sound = pygame.mixer.Sound("assets//fonts//mus_gameover.mp3")
            self.mercy_sound = pygame.mixer.Sound("assets//fonts//mus_undynepiano.ogg")

            # 加载背景音乐
            pygame.mixer.music.load("assets//fonts//M800002I2jbJ1WPRI0.mp3")
            pygame.mixer.music.set_volume(0.5)

        except:
            # 如果无法加载音效，创建空的音效对象
            class DummySound:
                def play(self): pass

                def set_volume(self, vol): pass

                def stop(self): pass

                def get_length(self): pass

            self.hit_sound = DummySound()
            self.shoot_sound = DummySound()
            self.teleport_sound = DummySound()
            self.dialogue_sound = DummySound()
            self.victory_sound = DummySound()
            self.game_over_sound = DummySound()
            self.mercy_sound = DummySound()
            self.bone_hit_sound = DummySound()

    def play_sound(self, sound):
        """播放音效并暂停背景音乐"""
        # 如果有背景音乐正在播放，暂停它
        if self.music_playing and not self.music_paused:
            pygame.mixer.music.pause()
            self.music_paused = True

        # 停止当前正在播放的音效
        if self.current_sound:
            self.current_sound.stop()

        # 播放新的音效
        self.current_sound = sound
        sound.play()

        # 安排在音效结束后恢复背景音乐
        try:
            sound_length = sound.get_length() * 1000  # 转换为毫秒
            pygame.time.set_timer(pygame.USEREVENT, int(sound_length))
        except:
            # 如果无法获取音效长度，使用默认值
            pygame.time.set_timer(pygame.USEREVENT, 1000)

    def handle_sound_complete(self):
        """音效播放完成后恢复背景音乐"""
        if self.music_paused:
            pygame.mixer.music.unpause()
            self.music_paused = False
        self.current_sound = None

    def play_hit_sound(self):
        self.play_sound(self.hit_sound)

    def play_shoot_sound(self):
        self.play_sound(self.shoot_sound)

    def play_teleport_sound(self):
        self.play_sound(self.teleport_sound)

    def play_dialogue_sound(self):
        self.play_sound(self.dialogue_sound)

    def play_victory_sound(self):
        self.play_sound(self.victory_sound)

    def play_game_over_sound(self):
        self.play_sound(self.game_over_sound)

    def play_mercy_sound(self):
        self.play_sound(self.mercy_sound)

    def play_battle_music(self):
        if not self.music_playing:
            pygame.mixer.music.play(-1)  # -1 表示循环播放
            self.music_playing = True
            self.music_paused = False

    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False
        self.music_paused = False


# 主游戏类
class Game:
    def __init__(self):
        self.state = GAME_STATES['START']
        self.player = Player()
        self.sound_manager = SoundManager()
        self.sans = Sans()
        self.dialogue = DialogueSystem(self.sound_manager)
        self.clock = pygame.time.Clock()
        self.font = font
        self.victory_font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 48)
        self.mercy_count = 0
        self.mercy_font = pygame.font.SysFont(["SimHei", "WenQuanYi Micro Hei", "Heiti TC", "Arial"], 20)
        self.game_time = 0
        self.difficulty_multiplier = 1.0
        self.max_difficulty = 5.0
        # 新增：记录上次仁慈操作的时间
        self.last_mercy_time = 0
        # 新增：仁慈操作间隔时间（30 秒，按帧数算为 30 * 60）
        self.mercy_interval = 30 * 60

    def run(self):
        running = True
        while running:
            self.game_time += 1

            # 每分钟增加难度0.5
            if self.game_time % 3600 == 0:
                self.difficulty_multiplier = min(self.difficulty_multiplier + 0.3, self.max_difficulty)

            # 根据仁慈次数更新阶段
            self.sans.update_phase(self.mercy_count)

            screen.fill(BLACK)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.state == GAME_STATES['START']:
                            self.state = GAME_STATES['BATTLE']
                            self.sound_manager.play_battle_music()
                        elif self.state == GAME_STATES['DIALOGUE'] and not self.dialogue.showing:
                            # 当对话结束时继续
                            self.state = GAME_STATES['BATTLE']
                        elif self.state in [GAME_STATES['VICTORY'], GAME_STATES['GAME_OVER']]:
                            running = False
                    elif event.key == pygame.K_m and self.state == GAME_STATES['BATTLE']:
                        self.try_mercy()
                elif event.type == pygame.USEREVENT:  # 音效播放完成事件
                    self.sound_manager.handle_sound_complete()

            if self.state == GAME_STATES['START']:
                self.draw_start_screen()
            elif self.state == GAME_STATES['BATTLE']:
                self.update_battle()
            elif self.state == GAME_STATES['DIALOGUE']:
                self.update_dialogue()
            elif self.state == GAME_STATES['VICTORY']:
                self.draw_victory_screen()
            elif self.state == GAME_STATES['GAME_OVER']:
                self.draw_game_over_screen()

            pygame.display.flip()
            self.clock.tick(60)

        self.sound_manager.stop_music()
        pygame.quit()
        sys.exit()

    def update_battle(self):
        self.player.update()
        self.sans.update(self.player, self.difficulty_multiplier, self.mercy_count)

        # 碰撞检测 - 玩家碰到骨头时骨头消失
        bones_to_remove = []
        for bone in self.sans.bones:
            if pygame.Rect.colliderect(self.player.rect, bone.rect):
                if not self.player.invincible:
                    bones_to_remove.append(bone)
                    if self.player.hit():
                        self.state = GAME_STATES['GAME_OVER']
                        self.sound_manager.play_game_over_sound()
                        break

        # 移除被碰到的骨头
        for bone in bones_to_remove:
            if bone in self.sans.bones:
                self.sans.bones.remove(bone)

        # 环形骨弹碰撞检测
        for circle_bone in self.sans.circle_bones:
            if pygame.Rect.colliderect(self.player.rect, circle_bone.rect):
                if not self.player.invincible:
                    if circle_bone in self.sans.circle_bones:
                        self.sans.circle_bones.remove(circle_bone)
                    if self.player.hit():
                        self.state = GAME_STATES['GAME_OVER']
                        self.sound_manager.play_game_over_sound()
                        break

        # 龙骨炮碰撞检测
        for gaster_blaster in self.sans.gaster_blasters:
            if pygame.Rect.colliderect(self.player.rect, gaster_blaster.rect):
                if not self.player.invincible:
                    if gaster_blaster in self.sans.gaster_blasters:
                        self.sans.gaster_blasters.remove(gaster_blaster)
                    if self.player.hit():
                        self.state = GAME_STATES['GAME_OVER']
                        self.sound_manager.play_game_over_sound()
                        break

        # 水滴碰撞检测
        for droplet in self.sans.droplets:
            if pygame.Rect.colliderect(self.player.rect, droplet.rect):
                if not self.player.invincible:
                    if droplet in self.sans.droplets:
                        self.sans.droplets.remove(droplet)
                    if self.player.hit():
                        self.state = GAME_STATES['GAME_OVER']
                        self.sound_manager.play_game_over_sound()
                        break

        self.player.draw(screen)
        self.sans.draw(screen)

        # 显示仁慈按钮提示
        mercy_text = self.mercy_font.render(f"按 M 尝试仁慈 ({self.mercy_count}/8)", True, YELLOW)
        screen.blit(mercy_text, (10, 70))

        # 显示难度
        difficulty_text = self.mercy_font.render(f"难度: {self.difficulty_multiplier:.1f}x", True, YELLOW)
        screen.blit(difficulty_text, (10, 100))

        # 根据阶段显示不同的对话
        if self.sans.current_phase == 2 and len(self.sans.bones) + len(
                self.sans.circle_bones) + len(self.sans.gaster_blasters) == 0 and not self.dialogue.showing:
            self.dialogue.start_section('PHASE_2')
            self.state = GAME_STATES['DIALOGUE']
        elif self.sans.current_phase == 3 and len(self.sans.bones) + len(
                self.sans.circle_bones) + len(self.sans.gaster_blasters) == 0 and not self.dialogue.showing:
            self.dialogue.start_section('PHASE_3')
            self.state = GAME_STATES['DIALOGUE']

    def update_dialogue(self):
        self.dialogue.update()
        self.dialogue.draw(screen)

    def try_mercy(self):
        current_time = self.game_time
        # 检查是否达到仁慈操作间隔时间
        if current_time - self.last_mercy_time < self.mercy_interval:
            return

        self.sans.mercy_tested = True
        self.mercy_count += 1
        self.last_mercy_time = current_time

        # 50%概率仁慈成功
        mercy_success = random.random() < 0.5

        if mercy_success:
            if self.mercy_count >= 8:
                self.state = GAME_STATES['VICTORY']
                self.sound_manager.play_mercy_sound()
                self.dialogue.start_section('MERCY_SUCCESS')
            else:
                self.sound_manager.play_mercy_sound()
                self.dialogue.start_section('MERCY_FAIL')
                self.state = GAME_STATES['DIALOGUE']
        else:
            self.sound_manager.play_mercy_sound()
            self.dialogue.start_section('MERCY_FAIL')
            self.state = GAME_STATES['DIALOGUE']

    def draw_start_screen(self):
        # 绘制开始屏幕背景
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT))

        title = self.font.render("传说之下 - Sans战", True, WHITE)
        start_text = self.font.render("按空格键开始", True, WHITE)
        controls_text = self.font.render("方向键移动，M键尝试仁慈", True, WHITE)

        title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        start_rect = start_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        controls_rect = controls_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

        screen.blit(title, title_rect)
        screen.blit(start_text, start_rect)
        screen.blit(controls_text, controls_rect)

    def draw_victory_screen(self):
        # 绘制胜利屏幕背景
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT))

        victory_text = self.victory_font.render("胜利！", True, YELLOW)
        continue_text = self.font.render("按空格键退出", True, WHITE)

        victory_rect = victory_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

        screen.blit(victory_text, victory_rect)
        screen.blit(continue_text, continue_rect)

        # 显示对话
        self.dialogue.update()
        self.dialogue.draw(screen)

    def draw_game_over_screen(self):
        # 绘制游戏结束屏幕背景
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, HEIGHT))

        game_over_text = self.victory_font.render("游戏结束", True, RED)
        continue_text = self.font.render("按空格键退出", True, WHITE)

        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))

        screen.blit(game_over_text, game_over_rect)
        screen.blit(continue_text, continue_rect)

        # 显示对话
        self.dialogue.start_section('GAME_OVER')
        self.dialogue.update()
        self.dialogue.draw(screen)


# 游戏入口
if __name__ == "__main__":
    game = Game()
    game.run()