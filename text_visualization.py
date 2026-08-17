from data_process import read_points
from visualization import plot_points

points = read_points("points.csv")

plot_points(points)