import tkinter as tk
import os

root = tk.Tk()
def close_windows():
    root.destroy()
    # sys.exit()

def open_round_shape():
    close_windows()
    os.system('python roundShape.py')

def open_ellipse_shape():
    close_windows()
    # os.system('python roundShape.py')

def open_spindle_shape():
    close_windows()
    # os.system('python roundShape.py')


root.title('请选择需要识别的粒子大致形状')
root.protocol('WM_DELETE_WINDOW', close_windows)
windows_height = 200
windows_width = 400
screen_width = root.winfo_screenwidth()/2 - windows_width/2 #获取显示器宽度
screen_height = root.winfo_screenheight()/2 - windows_height/2 #获取显示器高度
#将窗口界面与显示屏相关联，大概在80%左右
root.geometry(f"{windows_width}x{windows_height}+{int(screen_width)}+{int(screen_height)}")

# three_big_btn = tk.Frame(root)
tk.Button(root,text='近似圆形', command=lambda: open_round_shape()).pack(side=tk.LEFT, padx=30)
tk.Button(root,text='近似椭圆形', command=lambda: open_ellipse_shape()).pack(side=tk.LEFT, padx=30)
tk.Button(root,text='近似纺锤形', command=lambda: open_spindle_shape()).pack(side=tk.LEFT, padx=30)

if __name__ == '__main__':
    root.mainloop()