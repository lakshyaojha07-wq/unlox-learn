import turtle
import math

screen = turtle.Screen()
screen.bgcolor("black")

t = turtle.Turtle()

t.speed(1)
t.hideturtle()
t.penup()
t.color("red")

for scale in range(11,17):
    for l in range(120):
        angle = l * (math.pi * 2)/120
        x = scale * (16 * math.sin(angle)**3)
        y = scale * (13 * math.cos(angle) - 5 * math.cos(2 * angle) - 2 * math.cos(3 * angle) - math.cos(4 * angle))
        t.goto(x, y)
        t.write("I Love You", align="center", font=("Arial", 12, "bold"))

turtle.done()