import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import os
import sys

# 导入项目模块
from surveying import distance, azimuth, coordinate_forward, coordinate_inverse
from data_process import read_points, find_point, save_results, validate_points, get_points_stats
from visualization import plot_points
from traverse import (
    read_traverse_data,
    traverse_calculation,
    adjust_traverse,
    save_traverse_report
)

# ==============================
# 全局变量
# ==============================
DATA_DIR = "data"
OUTPUT_DIR = "output"


# ==============================
# 辅助函数：让用户输入多个值
# ==============================
def input_dialog(parent, title, prompts):
    """
    弹出多个输入框，返回用户输入的值列表
    """
    result = []
    for prompt in prompts:
        val = simpledialog.askstring(title, prompt, parent=parent)
        if val is None:
            return None  # 用户取消
        result.append(val)
    return result


# ==============================
# GUI 主类
# ==============================
class SurveyDataToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SurveyDataTool - 测绘数据处理工具")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 顶部标题
        title_label = tk.Label(self.root, text="SurveyDataTool", font=("Arial", 20, "bold"))
        title_label.pack(pady=10)

        # 功能按钮区域（两行）
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        # 第一行按钮（1-8）
        row1 = tk.Frame(button_frame)
        row1.pack()
        buttons = [
            ("1.两点距离", self.cmd_distance),
            ("2.方位角", self.cmd_azimuth),
            ("3.坐标正算", self.cmd_forward),
            ("4.坐标反算", self.cmd_inverse),
            ("5.读取数据", self.cmd_read_points),
            ("6.点距方位角", self.cmd_point_distance_azimuth),
            ("7.批量计算", self.cmd_batch),
            ("8.可视化", self.cmd_visualize),
        ]
        for text, cmd in buttons:
            btn = tk.Button(row1, text=text, width=12, command=cmd)
            btn.pack(side=tk.LEFT, padx=2, pady=2)

        # 第二行按钮（9-11）
        row2 = tk.Frame(button_frame)
        row2.pack()
        buttons2 = [
            ("9.统计", self.cmd_stats),
            ("10.闭合导线", self.cmd_traverse_closed),
            ("11.附和导线", self.cmd_traverse_adjust),
        ]
        for text, cmd in buttons2:
            btn = tk.Button(row2, text=text, width=12, command=cmd)
            btn.pack(side=tk.LEFT, padx=2, pady=2)

        # 文本框（显示结果）
        self.output_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=100, height=25, font=("Consolas", 10))
        self.output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # 底部清空按钮
        clear_btn = tk.Button(self.root, text="清空输出", command=self.clear_output)
        clear_btn.pack(pady=5)

        # 初始提示
        self.output_text.insert(tk.END, "欢迎使用 SurveyDataTool！\n")
        self.output_text.insert(tk.END, "点击上方按钮执行功能，结果将显示在此处。\n")
        self.output_text.insert(tk.END, "-" * 60 + "\n")

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)

    def log(self, message):
        """向文本框追加内容"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)  # 滚动到底部

    # ==============================
    # 功能实现
    # ==============================

    def cmd_distance(self):
        """1. 两点距离"""
        vals = input_dialog(self.root, "两点距离", ["A点X坐标:", "A点Y坐标:", "B点X坐标:", "B点Y坐标:"])
        if vals is None:
            return
        try:
            x1, y1, x2, y2 = map(float, vals)
            d = distance(x1, y1, x2, y2)
            self.log(f"A-B距离：{d:.3f} m")
        except Exception as e:
            self.log(f"错误：{e}")

    def cmd_azimuth(self):
        """2. 方位角"""
        vals = input_dialog(self.root, "方位角", ["A点X坐标:", "A点Y坐标:", "B点X坐标:", "B点Y坐标:"])
        if vals is None:
            return
        try:
            x1, y1, x2, y2 = map(float, vals)
            ang = azimuth(x1, y1, x2, y2)
            self.log(f"A-B方位角：{ang:.3f}°")
        except Exception as e:
            self.log(f"错误：{e}")

    def cmd_forward(self):
        """3. 坐标正算"""
        vals = input_dialog(self.root, "坐标正算", ["起点X坐标:", "起点Y坐标:", "距离:", "方位角(度):"])
        if vals is None:
            return
        try:
            x, y, d, ang = map(float, vals)
            x_end, y_end = coordinate_forward(x, y, d, ang)
            self.log(f"终点X坐标：{x_end:.3f}")
            self.log(f"终点Y坐标：{y_end:.3f}")
        except Exception as e:
            self.log(f"错误：{e}")

    def cmd_inverse(self):
        """4. 坐标反算"""
        vals = input_dialog(self.root, "坐标反算", ["A点X坐标:", "A点Y坐标:", "B点X坐标:", "B点Y坐标:"])
        if vals is None:
            return
        try:
            x1, y1, x2, y2 = map(float, vals)
            d, ang = coordinate_inverse(x1, y1, x2, y2)
            self.log(f"A-B距离：{d:.3f} m")
            self.log(f"A-B方位角：{ang:.3f}°")
        except Exception as e:
            self.log(f"错误：{e}")

    def cmd_read_points(self):
        """5. 读取测量点数据"""
        filename = simpledialog.askstring("读取数据", "请输入CSV文件名（如 points.csv）：", parent=self.root)
        if filename is None:
            return
        try:
            filepath = os.path.join(DATA_DIR, filename)
            points = read_points(filepath)
            valid, msg = validate_points(points)
            if not valid:
                self.log(f"数据检查失败：{msg}")
                return
            self.log(f"读取成功！共 {len(points)} 个有效测量点：")
            for p in points:
                self.log(f"  {p['id']}: X={p['x']:.3f}, Y={p['y']:.3f}")
        except FileNotFoundError:
            self.log("文件不存在！请检查文件名。")
        except Exception as e:
            self.log(f"错误：{e}")

    def cmd_point_distance_azimuth(self):
        """6. 测量点距离及方位角"""
        filename = simpledialog.askstring("选择文件", "请输入CSV文件名：", parent=self.root)
        if filename is None:
            return
        try:
            filepath = os.path.join(DATA_DIR, filename)
            points = read_points(filepath)
            valid, msg = validate_points(points)
            if not valid:
                self.log(f"数据检查失败：{msg}")
                return

            p1_id = simpledialog.askstring("起点", "请输入起点点号：", parent=self.root)
            p2_id = simpledialog.askstring("终点", "请输入终点点号：", parent=self.root)
            if p1_id is None or p2_id is None:
                return

            p1 = find_point(points, p1_id)
            p2 = find_point(points, p2_id)
            if p1 is None or p2 is None:
                self.log("点号不存在！")
                return
            d = distance(p1["x"], p1["y"], p2["x"], p2["y"])
            ang = azimuth(p1["x"], p1["y"], p2["x"], p2["y"])
            self.log(f"{p1_id}-{p2_id}距离：{d:.3f} m")
            self.log(f"{p1_id}-{p2_id}方位角：{ang:.3f}°")
        except FileNotFoundError:
            self.log("文件不存在！")
        except Exception as e:
            self.log(f"错误：{e}")

    def cmd_batch(self):
        """7. 批量计算测量点数据"""
        filename = simpledialog.askstring("批量计算", "请输入CSV文件名：", parent=self.root)
        if filename is None:
            return
        try:
            filepath = os.path.join(DATA_DIR, filename)
            points = read_points(filepath)
            valid, msg = validate_points(points)
            if not valid:
                self.log(f"数据检查失败：{msg}")
                return

            total = len(points) - 1
            if total <= 0:
                self.log("至少需要2个点！")
                return

            self.log(f"共有 {total} 对相邻点，开始计算...")
            results = []
            cumulative = 0
            for i in range(total):
                p1 = points[i]
                p2 = points[i+1]
                d = distance(p1["x"], p1["y"], p2["x"], p2["y"])
                ang = azimuth(p1["x"], p1["y"], p2["x"], p2["y"])
                cumulative += d
                results.append({
                    "起点": p1["id"],
                    "终点": p2["id"],
                    "距离": round(d, 3),
                    "方位角": round(ang, 3),
                    "累计边长": round(cumulative, 3)
                })

            # 保存
            output_file = os.path.join(OUTPUT_DIR, "result.csv")
            save_results(output_file, results, include_cumulative=True)
            self.log(f"计算完成！共 {len(results)} 对点，累计边长 {cumulative:.3f} m")
            self.log(f"结果已保存：{output_file}")
        except FileNotFoundError:
            self.log("文件不存在！")
        except Exception as e:
            self.log(f"错误：{e}")

    def cmd_visualize(self):
        """8. 测量点可视化"""
        filename = simpledialog.askstring("可视化", "请输入CSV文件名：", parent=self.root)
        if filename is None:
            return
        try:
            filepath = os.path.join(DATA_DIR, filename)
            points = read_points(filepath)
            valid, msg = validate_points(points)
            if not valid:
                self.log(f"数据检查失败：{msg}")
                return
            plot_points(points)
            self.log("测量点图已保存：output/survey_points.png")
        except FileNotFoundError:
            self.log("文件不存在！")
        except Exception as e:
            self.log(f"错误：{e}")

    def cmd_stats(self):
        """9. 测量点统计"""
        filename = simpledialog.askstring("统计", "请输入CSV文件名：", parent=self.root)
        if filename is None:
            return
        try:
            filepath = os.path.join(DATA_DIR, filename)
            points = read_points(filepath)
            valid, msg = validate_points(points)
            if not valid:
                self.log(f"数据检查失败：{msg}")
                return
            stats = get_points_stats(points)
            self.log("-" * 40)
            self.log("测量点统计结果")
            self.log("-" * 40)
            self.log(f"点数量：{stats['count']}")
            self.log(f"X坐标范围：{stats['x_min']:.3f}  ~  {stats['x_max']:.3f}")
            self.log(f"Y坐标范围：{stats['y_min']:.3f}  ~  {stats['y_max']:.3f}")
            self.log(f"X平均值：{stats['x_avg']:.3f}")
            self.log(f"Y平均值：{stats['y_avg']:.3f}")
            self.log("-" * 40)
        except FileNotFoundError:
            self.log("文件不存在！")
        except Exception as e:
            self.log(f"错误：{e}")

    def cmd_traverse_closed(self):
        """10. 闭合导线计算"""
        filename = simpledialog.askstring("闭合导线", "请输入导线观测数据文件（如 traverse_data.csv）：", parent=self.root)
        if filename is None:
            return
        try:
            filepath = os.path.join(DATA_DIR, filename)
            data = read_traverse_data(filepath)
            if not data:
                self.log("文件中没有数据！")
                return

            # 输入起点信息
            vals = input_dialog(self.root, "闭合导线起点", ["起点X坐标:", "起点Y坐标:", "起始方位角(度):"])
            if vals is None:
                return
            start_x, start_y, start_az = map(float, vals)

            results, closure = traverse_calculation(start_x, start_y, start_az, data)
            # 显示简略结果
            self.log("导线计算结果：")
            self.log(f"点数：{len(results)}，导线总长：{closure['total_distance']:.3f} m")
            self.log(f"fx={closure['fx']:.6f}, fy={closure['fy']:.6f}, f={closure['f']:.6f}")
            k_str = f"1/{int(1/closure['k'])}" if closure['k'] > 0 else "∞"
            self.log(f"K={k_str}")
            if closure['k'] > 0 and closure['k'] <= 1/2000:
                self.log("✅ 精度合格")
            else:
                self.log("❌ 精度不合格")

            # 是否平差
            do_adjust = messagebox.askyesno("平差", "是否进行平差计算（按边长分配闭合差）？")
            if do_adjust:
                adjusted = adjust_traverse(results, closure)
                self.log("平差完成。")
                # 显示前几个平差点
                for r in adjusted[:3]:
                    if r.get('adj_x') is not None:
                        self.log(f"  {r['name']}: 平差后 ({r['adj_x']:.3f}, {r['adj_y']:.3f})")
                self.log("  ... (完整结果可导出报告)")

            # 导出报告
            do_export = messagebox.askyesno("导出报告", "是否导出计算报告（.txt）？")
            if do_export:
                report_path = save_traverse_report(results, closure, adjusted if do_adjust else None,
                                                    start_x, start_y, start_az)
                self.log(f"报告已保存：{report_path}")

        except FileNotFoundError:
            self.log("文件不存在！")
        except Exception as e:
            self.log(f"错误：{e}")

    def cmd_traverse_adjust(self):
        """11. 附和导线计算"""
        from traverse import traverse_adjust, format_traverse_adjust_report
        filename = simpledialog.askstring("附和导线", "请输入导线观测数据文件：", parent=self.root)
        if filename is None:
            return
        try:
            filepath = os.path.join(DATA_DIR, filename)
            data = read_traverse_data(filepath)
            if not data:
                self.log("文件中没有数据！")
                return

            # 输入起终点信息
            vals = input_dialog(self.root, "附和导线已知点",
                                ["起点X:", "起点Y:", "起始方位角(度):",
                                 "终点X:", "终点Y:", "终边方位角(度):"])
            if vals is None:
                return
            start_x, start_y, start_az, end_x, end_y, end_az = map(float, vals)

            results, closure, adjusted = traverse_adjust(start_x, start_y, end_x, end_y,
                                                         start_az, end_az, data)
            self.log("附和导线计算结果：")
            self.log(f"导线总长：{closure['total_distance']:.3f} m")
            self.log(f"角度闭合差：{closure['angle_error']:.6f}°")
            self.log(f"fx={closure['fx']:.6f}, fy={closure['fy']:.6f}, f={closure['f']:.6f}")
            k_str = f"1/{int(1/closure['k'])}" if closure['k'] > 0 else "∞"
            self.log(f"K={k_str}")
            if closure['k'] > 0 and closure['k'] <= 1/2000:
                self.log("✅ 精度合格")
            else:
                self.log("❌ 精度不合格")

            # 导出报告（复用 txt 导出，但需要调整参数）
            do_export = messagebox.askyesno("导出报告", "是否导出计算报告（.txt）？")
            if do_export:
                # 这里因为 save_traverse_report 只能处理闭合导线，暂不导出，或简单提示
                self.log("报告导出功能暂未支持附和导线，请使用命令行版本。")
        except FileNotFoundError:
            self.log("文件不存在！")
        except Exception as e:
            self.log(f"错误：{e}")


# ==============================
# 主程序入口
# ==============================
if __name__ == "__main__":
    root = tk.Tk()
    app = SurveyDataToolApp(root)
    root.mainloop()