import tkinter as tk


class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y, effect="fire"):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 5
        self.effect = effect  # Either "fire" or "snow"
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='white')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)
        self.add_effect(coords)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()

    def add_effect(self, coords):
        x = (coords[0] + coords[2]) / 2
        y = (coords[1] + coords[3]) / 2
        if self.effect == "fire":
            # Create fire effect
            flame = self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="orange", outline="")
            self.canvas.after(50, lambda: self.canvas.delete(flame))
        elif self.effect == "snow":
            # Create snow effect
            snowflake = self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="lightblue", outline="")
            self.canvas.after(100, lambda: self.canvas.delete(snowflake))


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    COLORS = {1: '#4535AA', 2: '#ED639E', 3: '#8FE1A2'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    LEVEL_COLORS = ['#D6D1F5', '#B9E3F6', '#F3CAB9', '#F3EDB9', '#C2F3B9']

    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.level = 1
        self.score = 0
        self.canvas = tk.Canvas(self, bg=Game.LEVEL_COLORS[self.level % len(Game.LEVEL_COLORS)],
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def setup_game(self):
        self.add_ball()
        self.update_hud()
        self.text = self.draw_text(300, 200, f'Level {self.level} - Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())
        self.add_bricks()

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        # Choose "fire" or "snow" for ball effect
        self.ball = Ball(self.canvas, x, 310, effect="fire")
        self.paddle.set_ball(self.ball)

    def add_bricks(self):
        y_offset = 50
        for row in range(self.level + 2):
            for x in range(5, self.width - 5, 75):
                hits = 3 - (row % 3)
                self.add_brick(x + 37.5, y_offset + row * 20, hits)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_hud(self):
        text = f'Lives: {self.lives}  Score: {self.score}'
        if self.hud is None:
            self.hud = self.draw_text(300, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.level += 1
            self.ball.speed += 1
            self.canvas.config(bg=Game.LEVEL_COLORS[self.level % len(Game.LEVEL_COLORS)])
            self.setup_game()
        elif self.ball.get_position()[3] >= self.height:
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'You Lose! Game Over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)
        for obj in objects:
            if isinstance(obj, Brick):
                self.score += 10
                self.update_hud()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks! (with Fire and Snow Effects)')
    game = Game(root)
    game.mainloop()
