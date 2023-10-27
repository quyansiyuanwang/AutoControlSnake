import random
import time
import threading
import keyboard
from queue import Queue


class Const:
    floor = "0"
    snakeBody = "#"
    bean = "*"


class GameState:
    crashSelf = "You crashed onto yourself!"
    crashWall = "You crashed onto wall!"
    mapFull = "You Win!"
    gameRunning = "The game still not end"
    flag = gameRunning


class SnakeMap(list):
    def get(self, position: tuple[int, int]) -> any:
        """
        用元组实现获取
        :param position: 元组包含xy内容
                例子: (2, 3)
        :type position: tuple[int, int]
        :rtype: any
        """
        x, y = position
        return self[x][y]

    def __contains__(self, position: int):
        x, y = position
        if any((i not in range(len(self))) for i in (x, y)):
            return False
        return True

    def isExist(self, target: any) -> bool:
        """
        寻找是否存在target元素于地图(map)中
        :param target: 寻找的元素
        :rtype: bool
        """
        filtrate_line = [line for line in self if target in line]
        return not not filtrate_line

    def update(self, changes: dict[tuple[int, int] : any]) -> bool:
        """
        更新地图内容, 成功/失败 返回 T/F
        :param changes: 字典键为地块，值为替换内容
                example: {(0, 1): 0, ...}
        :type changes: dict[tuple[int]: any]
        :rtype: bool
        """
        for (x, y), rep in changes.items():
            # 是否超出地图
            if any(i not in range(len(self)) for i in (x, y)):
                GameState.flag = GameState.crashWall
                return
            # 替换内容
            self[x][y] = rep
        GameState.flag = GameState.gameRunning

    def beanCreate(self) -> bool:
        """
        随机创建豆子, 成功/失败 为 T/F
        :rtype: bool
        """
        # 推导存在空格地板的行
        line_indexes = [line for line in self if Const.floor in line]
        # 行存在
        if line_indexes:
            # 抽取随机行
            random_line = random.choice(line_indexes)
            # 内容为地板的下标
            floor_indexes = [
                idx for idx, item in enumerate(random_line) if item == Const.floor
            ]
            # 抽取地板替换为豆子
            random_line[random.choice(floor_indexes)] = Const.bean
            GameState.flag = GameState.gameRunning
        else:
            GameState.flag = GameState.mapFull

    def __str__(self):
        string = ""
        for line in self:
            for item in line:
                string += item + ""
            string += "\n"
        return string


class Snake:
    def __init__(self, spawn: tuple[int], map_obj: SnakeMap):
        self.body = [spawn]
        self.map_obj = map_obj
        self.map_obj.update({spawn: Const.snakeBody})

    def move(self, toward: tuple[int, int]) -> bool:
        """
        蛇的移动方法，传入方向以移动
        :param toward: 传入移动方向,
                example: 向下(1, 0)
        :type toward: tuple[int, int]
        :rtype: bool
        """
        # 计算新旧位置
        pos = self.body[-1]
        new_pos = tuple(toward[i] + j for i, j in enumerate(pos))
        # 判断是否撞上自己 / 墙壁
        if new_pos in self.body:
            return GameState.crashSelf
        elif new_pos not in self.map_obj:
            return GameState.crashWall
        # 实现自身移动
        update_content = {new_pos: Const.snakeBody}
        if self.map_obj.get(new_pos) != Const.bean:
            # 删尾
            update_content.update({self.body[0]: Const.floor})
            del self.body[0]
        # 增头
        self.body.append(new_pos)
        # 地图更新
        self.map_obj.update(update_content)
        return GameState.gameRunning


class SnakeController(threading.Thread):
    def __init__(self, snake, direction_queue):
        super().__init__()
        self.snake = snake
        self.direction_queue = direction_queue

    def run(self):
        while GameState.flag == GameState.gameRunning:
            toward = self.direction_queue.get()
            if toward is not None:
                GameState.flag = self.snake.move(toward)
            time.sleep(0.5)

def keyboard_reflect(key: str) -> tuple[int]:
    refl = {
        "w": (-1, 0), 
        "a": (0, -1), 
        "s": (1, 0), 
        "d": (0, 1)
            }
    # 方向的键盘映射
    ret = refl.get(key.lower(), None)
    return ret


def create_map(edge_len: int) -> SnakeMap[list[any]]:
    return SnakeMap([Const.floor] * edge_len for _ in range(edge_len))


def main():
    m = create_map(4)
    s = Snake((0, 0), m)

    direction_queue = Queue()
    controller = SnakeController(s, direction_queue)
    controller.start()
    direction_queue.put((1, 0))

    while True:
        print(m)
        try:
            key_event = keyboard.read_event()
            if key_event.event_type == keyboard.KEY_DOWN:
                key = key_event.name
                toward = keyboard_reflect(key)
                direction_queue.put(toward)
        except KeyboardInterrupt:
            break

        if not m.isExist(Const.bean):
            m.beanCreate()

        if GameState.flag != GameState.gameRunning:
            print(GameState.flag)
            controller.join()
            break


if __name__ == "__main__":
    main()
    print("end")
