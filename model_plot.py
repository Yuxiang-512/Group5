from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
import numpy as np

class DynamicPlot(FigureCanvas):
    def __init__(self, parent=None, window_width=50, y_range=(0, 10)):
        fig = Figure()
        self.axes = fig.add_subplot(111)
        super().__init__(fig)  # 使用 super() 更规范的调用父类构造函数
        self.setParent(parent)

        self.line, = self.axes.plot([], [], 'r-')
        self.x_data, self.y_data = [], []
        self.window_width = window_width
        self.y_range = y_range

        # Initialize the plot window
        self.axes.set_xlim(0, self.window_width)
        self.axes.set_ylim(*self.y_range)

    def init(self):
        return self.line,

    def update(self, frame):
        self.x_data.append(frame)
        self.y_data.append(np.random.rand() * (self.y_range[1] - self.y_range[0]) + self.y_range[0])

        # Update the view limits
        if len(self.x_data) > self.window_width:
            self.axes.set_xlim(self.x_data[-self.window_width], self.x_data[-1])

        self.line.set_data(self.x_data, self.y_data)
        return self.line,

    def run(self):
        self.ani = FuncAnimation(self.figure, self.update, frames=np.arange(0, 1000), init_func=self.init, blit=True)
