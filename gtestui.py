# 处理后图形 四周是白边  分辨率问题
# 优化：可以识别长轴短轴并进行平均后做为粒径大小、
# 误差较大区域的二次分析。添加、缩放标记圆圈.
# 边缘粒子删除 、生成粒径分布图
# 若重绘，粒子csv文件应该从mid中替代
import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel ,ttk , Canvas ,simpledialog
from PIL import Image, ImageTk ,ImageOps, ImageEnhance
from skimage import io, feature
import os
import csv
import math
import matplotlib.pyplot as plt
import shutil  
import cv2
import numpy as np
import re
import scipy.spatial as spt
# 初始化全局变量
img = None
photo = None
canvas = None
rect_id = None
rect_start = None
selected_region = None
selected_file = None
saved_params = None
output_folder = "output_folder"
os.makedirs(output_folder, exist_ok=True)
mid_folder = "mid_folder"
os.makedirs(mid_folder, exist_ok=True)

processed_files = []
processed_files_csv = []
mid_files_csv = []
def process_image(saved_params, selected_file_in1, selected_region = None):
    global processed_files, processed_files_csv, mid_files_csv 
    base_filename = os.path.splitext(os.path.basename(selected_file_in1))[0]
    pattern = r'(_翻转|_对比度)+$'
    if re.search(pattern, base_filename):
        base_filename = re.sub(pattern, '', base_filename)
    max_sigma = saved_params.get('max_sigma', 0)
    min_sigma = saved_params.get('min_sigma', 0)
    num_sigma = saved_params.get('num_sigma', 0)
    threshold = saved_params.get('threshold', 0)
    scale_length_mm = saved_params.get('scale_length_mm', 0)
    scale_length_pixels = saved_params.get('scale_length_pixels', 0)
    pixels_per_mm = scale_length_pixels / scale_length_mm
    image = io.imread(selected_file_in1)
    if selected_region :
        x1, y1, x2, y2 = map(int, selected_region)
        user_image = image[y1:y2, x1:x2]
    else:
        user_image = image  
    blobs_log = feature.blob_log(user_image, max_sigma=max_sigma, min_sigma=min_sigma, num_sigma=num_sigma, threshold=threshold)
    blobs_log[:, 2] = blobs_log[:, 2] * math.sqrt(2)
    with open(os.path.join(output_folder, f'{base_filename}.csv'), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Blob Number', 'Diameter (nm)'])
        for j, blob in enumerate(blobs_log):  
            diameter_pixels = 2 * blob[2]
            diameter_mm = diameter_pixels / pixels_per_mm
            diameter_nm = diameter_mm   
            writer.writerow([j+1, f"{diameter_nm:.4f}"])
    with open(os.path.join(mid_folder, f'{base_filename}.csv'), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Blob Number', 'Diameter (nm)' , 'y' , 'x' , 'r'])
        for j, blob in enumerate(blobs_log):  
            diameter_pixels = 2 * blob[2]
            diameter_mm = diameter_pixels / pixels_per_mm
            diameter_nm = diameter_mm   
            if selected_region :
                if x1 < x2 :
                    y_d, x_d, r_d = blob[0] + y1, blob[1] + x1, blob[2]
                else:
                    y_d, x_d, r_d = blob[0] + y2, blob[1] + x2, blob[2]
            else:
                y_d, x_d, r_d = blob[0], blob[1], blob[2]
            writer.writerow([j+1, f"{diameter_nm:.4f}" , y_d , x_d , r_d])

    for file_path in imported_files:
        if base_filename in file_path:
            if '_翻转' not in file_path and '_对比度' not in file_path:
                draw_file = file_path
                break 
    image_draw = io.imread(draw_file)
    image_height, image_width = image_draw.shape[:2]
    dpi = 480
    figsize = (image_width / dpi, image_height / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.imshow(image_draw, cmap='gray', interpolation='nearest')
    ax.axis('off') 
    

# 去白边
    fig.set_size_inches(image_width/100.0/3.0, image_height/100.0/3.0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.subplots_adjust(top=1,bottom=0,left=0,right=1,hspace=0,wspace=0)
    plt.margins(0,0)

    ax.set_xlim(0, image_width)
    ax.set_ylim(image_height, 0)
    for j, blob in enumerate(blobs_log):
        if selected_region :
            if x1 < x2 :
                y, x, r = blob[0] + y1, blob[1] + x1, blob[2]
            else:
                y, x, r = blob[0] + y2, blob[1] + x2, blob[2]
        else:
            y, x, r = blob[0], blob[1], blob[2]
        c = plt.Circle((x, y), r, color='red', linewidth=0.5, fill=False)
        ax.add_patch(c)
        ax.text(x, y, str(j+1), color='yellow', fontsize=4)
    output_path = os.path.join(output_folder, f'{base_filename}.png')
    output_path_csv = os.path.join(output_folder, f'{base_filename}.csv')
    mid_path_csv = os.path.join(mid_folder, f'{base_filename}.csv')
    plt.savefig(output_path, dpi=dpi, pad_inches=0)
    # plt.savefig(output_path, dpi=dpi, bbox_inches='tight', pad_inches=0)
    plt.close()
    processed_files.append(output_path)
    processed_files_csv.append(output_path_csv)
    mid_files_csv.append(mid_path_csv)
    basename = os.path.basename(output_path)
    existing_items = processed_image_area.get_children()
    basename_exists = any(basename == processed_image_area.item(item, 'text') for item in existing_items)
    if not basename_exists:
        processed_image_area.insert('', 'end', text=basename)
    bottom_tips.configure(text='处理完成！') 

def flip_colors():
    global selected_file_in1 , imported_files
    if selected_file_in1:
        image = io.imread(selected_file_in1)
        image_pil = Image.fromarray(image)
        flipped_image_pil = ImageOps.invert(image_pil)
        base_filename = os.path.basename(selected_file_in1)
        flipped_image_path = os.path.join(mid_folder, f'{os.path.splitext(base_filename)[0]}_翻转{os.path.splitext(base_filename)[1]}')
        flipped_image_pil.save(flipped_image_path)
        imported_files.append(flipped_image_path)
        original_image_area.insert('', 'end', text=f'{os.path.splitext(base_filename)[0]}_翻转{os.path.splitext(base_filename)[1]}')
        bottom_tips.configure(text='颜色翻转完成！')
    else:
        bottom_tips.configure(text='请先选择图像')

def adjust_contrast():
    global selected_file_in1 , imported_files
    if selected_file_in1:
        image = Image.open(selected_file_in1)
        image_np = np.array(image)
        contrast_image_np = cv2.equalizeHist(image_np)
        contrast_image = Image.fromarray(contrast_image_np)
        base_filename = os.path.basename(selected_file_in1)
        contrast_image_path = os.path.join(mid_folder, f'{os.path.splitext(base_filename)[0]}_对比度{os.path.splitext(base_filename)[1]}')
        contrast_image.save(contrast_image_path)
        imported_files.append(contrast_image_path)
        original_image_area.insert('', 'end', text=f'{os.path.splitext(base_filename)[0]}_对比度{os.path.splitext(base_filename)[1]}')
        bottom_tips.configure(text='对比度调整完成！')
    else:
        bottom_tips.configure(text='请先选择图像')

def get_scale_params():
    global scale_length_mm, scale_length_pixels, max_sigma, min_sigma, num_sigma, threshold, saved_params
    stop_measuring()  
    try:
        scale_length_mm = float(blank1.get())  
        scale_length_pixels = float(blank2.get())  
        max_sigma = float(blank3.get()) / 2
        min_sigma = float(blank4.get()) / 2
        num_sigma = int(blank5.get())
        threshold = float(blank6.get())
        if max_sigma <= 0 or min_sigma <= 0 or num_sigma <= 0 or threshold < 0 or scale_length_mm <= 0 or scale_length_pixels <= 0:
            bottom_tips.configure(text='所有参数都应该是正数')
        if min_sigma >= max_sigma:
            bottom_tips.configure(text='最小粒径应小于最大粒径')     
    except ValueError as e:
        bottom_tips.configure(text='参数错误')
        return None  
    saved_params = {
        'max_sigma': max_sigma, 
        'min_sigma': min_sigma,
        'num_sigma': num_sigma,
        'threshold': threshold,
        'scale_length_mm': scale_length_mm,
        'scale_length_pixels': scale_length_pixels,
    }
    bottom_tips.configure(text='参数已保存')
    return saved_params

imported_files = []
def select_file():
    global selected_file
    filetypes = (
        ('图像文件', '*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.ppm;*.pgm;*.pbm;*.tiff;*.tif'),
        ('所有文件', '*.*')
    )
    selected_file = filedialog.askopenfilename(title='打开文件', initialdir='/', filetypes=filetypes)
    if selected_file:
        file_name = selected_file.split("/")[-1]  
        original_image_area.insert('', 'end', text=file_name)
        imported_files.append(selected_file)
        
def select_output_folder():
    global output_folder
    chosen_folder = filedialog.askdirectory(title='选择输出文件夹', initialdir='/')  
    if chosen_folder:
        for file_name in os.listdir(output_folder):
            source = os.path.join(output_folder, file_name)  
            destination = os.path.join(chosen_folder, file_name)  
            shutil.copy(source, destination) 
        output_folder = chosen_folder  
        messagebox.showinfo("保存成功", "已保存到: " + output_folder)  
    else:
        bottom_tips.configure(text="输出文件夹: 未选择")  

def show_image_1(event):
    global selected_file_in1 
    item = original_image_area.selection()
    if item:
        item_text = original_image_area.item(item, "text")
        selected_file_in1 = next(file for file in imported_files if item_text in file)
        show_photo(selected_file_in1)
        bottom_tips.configure(text='原图!')

def show_image_2(event):
    global selected_file_in2 , selected_file_in2_csv
    item = processed_image_area.selection()
    if item:
        item_text = processed_image_area.item(item, "text")
        selected_file_in2 = next(file for file in processed_files if item_text in file)
        show_photo(selected_file_in2)
        csv_file_name = f'{item_text.split(".")[0]}.csv'
        selected_file_in2_csv = next(file for file in mid_files_csv if csv_file_name in file)
        bottom_tips.configure(text='已处理图像!')
        for i in table.get_children():
            table.delete(i)
        try:
            with open(selected_file_in2_csv, newline='') as csvfile:
                csv_reader = csv.reader(csvfile)
                next(csv_reader)  
                for i, row in enumerate(csv_reader, start=1):
                    table.insert("", tk.END, values=[row[0], row[1]])
        except Exception as e:
            bottom_tips.configure(text=f'读取 CSV 文件时出错: {e}')

def size_distribution_chart():
    with open(selected_file_in2_csv, 'r', newline='') as file:
        csv_reader = csv.reader(file)
    None

def handle_current_image():
    global selected_region
    if selected_file_in1 and saved_params:
        bottom_tips.configure(text='处理图片中') 
        process_image(saved_params, selected_file_in1,selected_region)
        selected_region = None
    else:
        messagebox.showinfo("提示", "请选择图像并设置参数。")

def resize(resize1):
    global factor
    w, h = Image.open(os.path.abspath(resize1)).size
    factor = min([1.0*int(pane4.winfo_width())/w, 1.0*int(pane4.winfo_height())/h])
    width = int(w*factor)
    height = int(h*factor)
    return ImageTk.PhotoImage(Image.open(os.path.abspath(resize1)).resize((width, height)))

filename = list()
def show_photo(show_path1): 
    try:
        img = resize(show_path1)
        filename.append(img)  
        img_area.delete("all") 
        img_area.create_image(0, 0, anchor='nw', image=filename[-1])
        w, h = filename[-1].width(), filename[-1].height()
        img_area.config(width=w, height=h)
    except Exception as e: 
        bottom_tips.configure(text=f'显示异常: {e}')

def tools_description():
    popup_window = tk.Toplevel(root)
    popup_window.title("工具功能说明")
    text = "这是按钮的功能说明。\n"
    text += "选择文件后左侧输入参数\n"
    text += "在工具栏选择处理当前图片\n"
    text += "增加阈值会排除较弱的斑点\n"
    text += "导出输出图片与结果。"
    label = tk.Label(popup_window, text=text, padx=20, pady=20, wraplength=300)
    label.pack()

def delete_op():
    if messagebox.askyesnocancel(title='提醒！', message='本窗口关闭后，未导出的文件将会清除，请问是否继续关闭。'):
        delete_folder_contents(output_folder)
        delete_folder_contents(mid_folder)
        root.destroy() 

def delete_folder_contents(folder_path):
    file_list = os.listdir(folder_path)
    for file in file_list:
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            delete_folder_contents(file_path)

def start_area_selection():
    clear_rectangle() 
    img_area.bind('<Button-1>', rectangle_start)
    img_area.bind('<B1-Motion>', rectangle_expand) 
    img_area.bind('<ButtonRelease-1>', rectangle_end) 
    messagebox.showinfo("提示", "请按住鼠标左键从一个角开始拖动到另一个角，然后释放来选择区域。")



def clear_rectangle():
    global rect_id
    if rect_id:  
        img_area.delete(rect_id)
        rect_id = None  

def rectangle_start(event):
    global rect_start, rect_id
    clear_rectangle()  
    rect_start = (event.x, event.y)
    rect_id = img_area.create_rectangle(event.x, event.y, event.x, event.y, outline='blue', width=2, tags="rect")

def rectangle_expand(event):
    global rect_start, rect_id
    if rect_start:
        img_area.coords(rect_id, rect_start[0], rect_start[1], event.x, event.y)

def stop_rectangle():
    img_area.unbind('<Button-1>')
    img_area.unbind('<B1-Motion>')
    img_area.unbind('<ButtonRelease-1>')

def rectangle_end(event):
    global rect_start, rect_id, selected_region
    if rect_start and rect_id:  
        x1, y1, x2, y2 = img_area.coords(rect_id)
        if messagebox.askyesno("确认", "是否保存此矩形区域？"):
            selected_region = tuple(coord / factor for coord in (x1, y1, x2, y2))
            messagebox.showinfo("保存成功", "矩形区域已保存")
            stop_rectangle()
        else:
            clear_rectangle()
        rect_start = None

def on_right_click(event):
    try:
        global selected_blob_index  # 全局变量来存储当前选中的粒子索引
        region_id = table.identify_row(event.y)  # 根据点击位置获取行ID
        if region_id:
            table.selection_set(region_id)  # 选中该行
            selected_blob_index = int(table.item(region_id, 'values')[0])
            popup_menu.post(event.x_root, event.y_root)
    except Exception as e:
        print(f"Error in right click: {e}")

def delete_row_from_csv():
    with open(selected_file_in2_csv, 'r', newline='') as file:
        csv_reader = csv.reader(file)
        rows = list(csv_reader)
    matching_row = None
    for row in rows:
        if row and row[0] == str(selected_blob_index):
            matching_row = row
            break
    if matching_row:
        rows.remove(matching_row)
        with open(selected_file_in2_csv, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(rows)
        refresh_table()
    else:
        print(f"No matching row with value {selected_blob_index}")
# TODO 定位删除指定粒径
delete_windows_img = list()
# coordinate_groups =[]
def delete_row_from_img():

    click_point = list()
    delete_windows = tk.Toplevel()
    delete_windows_menu = tk.Menu(delete_windows, tearoff=False)

    click_point.append((0,0))
    delete_windows.title("左键粒径删除")
    img_path = selected_file_in2
    delete_windows.geometry(f"{int(screen_width*0.9)}x{int(screen_height*0.9)}+{int(screen_width*0.025)}+{int(screen_height*0.025)}")

    try:
        w, h = Image.open(os.path.abspath(img_path)).size
        factor = min([0.8*int(delete_windows.winfo_screenwidth())/w, 0.8*int(delete_windows.winfo_screenheight())/h])
        width = int(w*factor)
        height = int(h*factor)
        resize_img = ImageTk.PhotoImage(Image.open(os.path.abspath(img_path)).resize((width, height)))
        delete_windows.geometry(f'{width}x{height}')
        delete_windows.resizable(width=False, height=False)
        delete_windows_img.append(resize_img)
        delete_img_lb = tk.Canvas(delete_windows,width=width, height=height)
        delete_img_lb.pack()
        DW_show_img = delete_img_lb.create_image(0,0,anchor=tk.NW,image=delete_windows_img[-1])
    except Exception as e: 
        print(f"delete_image_error:{e}")
        # messagebox.showinfo(text=f'显示异常: {e}')
# 每次删除点后重绘图画
    def delete_windows_img_redraw():
        delete_windows_menu.entryconfig(0,label="处理中,请等待处理完成后再次删除", state='disable')

        fig, ax = plt.subplots(1, 1)
        base_filename = os.path.splitext(os.path.basename(selected_file_in2))[0]
        for file_path in imported_files:
            if base_filename in file_path:
                if '_翻转' not in file_path and '_对比度' not in file_path:
                    draw_file = file_path
                    break
        print(draw_file)
        image_draw = io.imread(draw_file)
        ax.imshow(image_draw, cmap='gray', interpolation='nearest')
        ax.axis('off')

        image_height, image_width = image_draw.shape
        fig.set_size_inches(image_width/100.0/3.0, image_height/100.0/3.0)
        plt.gca().xaxis.set_major_locator(plt.NullLocator())
        plt.gca().yaxis.set_major_locator(plt.NullLocator())
        plt.subplots_adjust(top=1,bottom=0,left=0,right=1,hspace=0,wspace=0)
        plt.margins(0,0)
        ax.set_xlim(0, image_width)
        ax.set_ylim(image_height, 0)

        with open(selected_file_in2_csv, newline='') as csvfile:
            csv_reader = csv.reader(csvfile)
            next(csv_reader)  
            for i, row in enumerate(csv_reader, start=1):
                index,y, x, r = int(row[0]),float(row[2]), float(row[3]), float(row[4])
                c = plt.Circle((x, y), r, color='red', linewidth=0.5, fill=False)
                ax.add_patch(c)
                ax.text(x, y, str(index), color='yellow', fontsize=4)
        output_path = os.path.abspath(img_path)
        plt.savefig(output_path, dpi=480, bbox_inches='tight', pad_inches=0)
        plt.close()
        delete_img_lb.delete(DW_show_img)
        delete_windows_img.pop()
        delete_windows_img.append(ImageTk.PhotoImage(Image.open(os.path.abspath(img_path)).resize((width, height))))
        delete_img_lb.pack()
        delete_img_lb.create_image(0,0,anchor=tk.NW,image=delete_windows_img[-1])
        delete_windows_menu.entryconfig(0,label="删除", state='normal')

    def close_edit_win():
        delete_windows.destroy()
# 根据点击位置删除csv中的row
    def delete_csv_point():
        x, y = click_point[0]
        original_image_w ,original_image_h = Image.open(os.path.abspath(selected_file_in1)).size
        click_img_x = int(x*original_image_w/width)
        click_img_y = int(y*original_image_h/height)
        point_index = []
        point_list = []
        with open(selected_file_in2_csv, 'r', newline='') as file:
            csv_reader = csv.reader(file)
            rows = list(csv_reader)
        # matching_row = None
        for item in rows:
            # 将各个点的坐标加入point
            if item[0] != "Blob Number":
                point_index.append(item)
                point_list.append([float(item[3]),float(item[2])])
        ckt = spt.KDTree(point_list)
        d, pIndex = ckt.query([click_img_x,click_img_y])
        matching_row = None
        for row in rows:
            if row and row[0] == point_index[pIndex][0]:
                matching_row = row
                break
        # print(matching_row)
        rows.remove(matching_row)
        with open(selected_file_in2_csv, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(rows)
        # refresh_table()
        delete_windows_img_redraw()


    def pop_delete(event):
        click_point.pop()
        click_point.append((event.x,  event.y))
        delete_windows_menu.post(event.x_root,  event.y_root)

    delete_img_lb.bind("<ButtonRelease-3>", pop_delete)
    delete_windows_menu.add_command(label="删除",command=delete_csv_point)
    delete_windows.protocol('WM_DELETE_WINDOW', close_edit_win)


def refresh_table():
    for i in table.get_children():
        table.delete(i)
    with open(selected_file_in2_csv, newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  
        for i, row in enumerate(csv_reader, start=1):
            table.insert("", tk.END, values=[row[0], row[1]])

def re_draw():
    fig, ax = plt.subplots(1, 1)
    base_filename = os.path.splitext(os.path.basename(selected_file_in2))[0]
    for file_path in imported_files:
        if base_filename in file_path:
            if '_翻转' not in file_path and '_对比度' not in file_path:
                draw_file = file_path
                break     
    image_draw = io.imread(draw_file)
    ax.imshow(image_draw, cmap='gray', interpolation='nearest')
    ax.axis('off') 
    image_height, image_width = image_draw.shape
    ax.set_xlim(0, image_width)
    ax.set_ylim(image_height, 0)
    with open(selected_file_in2_csv, newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        next(csv_reader)  
        for i, row in enumerate(csv_reader, start=1):
            index = row[0]
            y, x, r = float(row[2]), float(row[3]), float(row[4])
            c = plt.Circle((x, y), r, color='red', linewidth=0.5, fill=False)
            ax.add_patch(c)
            ax.text(x, y, str(index), color='yellow', fontsize=4)
    output_path = os.path.join(output_folder, f'{base_filename}.png')
    plt.savefig(output_path, dpi=480, bbox_inches='tight', pad_inches=0)
    plt.close()
    messagebox.showinfo( "提示", "已重新绘制，在“处理后图片”处点击可以显示")



'''
根窗口部分________________________________________________________________________________________________________
'''
root = tk.Tk() #根窗口
root.title("纳米粒径识别(推荐全屏使用)") #窗口名称
screen_width = root.winfo_screenwidth() #获取显示器宽度
screen_height = root.winfo_screenheight() #获取显示器高度
#将窗口界面与显示屏相关联，大概在80%左右
root.geometry(f"{int(screen_width*0.8)}x{int(screen_height*0.8)}+{int(screen_width*0.1)}+{int(screen_height*0.05)}")

'''
抬头菜单栏_________________________________________________________________________________________________________
'''
menu = tk.Menu(root, tearoff=False)
menu.add_separator()

menu_file = tk.Menu(menu, tearoff=False)
menu_file.add_command(label='选择文件', command=select_file)
menu_file.add_command(label='选择输出文件夹', command=select_output_folder)

menu_tool = tk.Menu(menu, tearoff=False)
menu_tool.add_command(label='处理图像', command=handle_current_image)
menu_tool.add_command(label='重绘', command=re_draw)
menu_tool.add_command(label='生成粒径分布图', command=size_distribution_chart)
menu_tool.add_separator()
menu_tool.add_command(label='选择区域', command=start_area_selection)
menu_tool.add_command(label='颜色翻转', command=flip_colors)
menu_tool.add_command(label='调节对比度', command=adjust_contrast)

menu_help = tk.Menu(menu, tearoff=False)
menu_help.add_command(label='功能说明', command=tools_description)

menu.add_cascade(label='文件', menu=menu_file)
menu.add_cascade(label='工具', menu=menu_tool)
menu.add_cascade(label='帮助', menu=menu_help)
root.config(menu=menu)

'''
底部信息显示栏________________________________________________________________________________________________________________
'''
bottom_frame = tk.Frame(root)
bottom_tips = tk.Label(bottom_frame, text='欢迎使用')
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=True, padx=5, pady=2)
bottom_tips.pack(anchor=tk.W)

'''
将窗口分区___________________________________________________________________________________________________________________________
'''
w_pane = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief = tk.SUNKEN)
pane1 = tk.PanedWindow(w_pane, orient=tk.VERTICAL, sashrelief=tk.SUNKEN)
pane2 = tk.PanedWindow(pane1)
pane3 = tk.PanedWindow(pane1)
pane4 = tk.PanedWindow(w_pane)
pane5 = tk.PanedWindow(w_pane, orient=tk.VERTICAL, sashrelief=tk.SUNKEN)
pane6 = tk.PanedWindow(pane5)
pane7 = tk.PanedWindow(pane5)

w_pane.pack(fill=tk.BOTH, expand=True)
w_pane.add(pane1)
w_pane.add(pane5)
w_pane.add(pane4)

pane1.add(pane2)
pane1.add(pane3)

pane5.add(pane6)
pane5.add(pane7)

'''
窗口左侧___________________________________________________________________________________________________________________________
'''
file_name_show = tk.Frame(pane2)
parameter_input = tk.Frame(pane3)
file_name_show.pack(fill=tk.BOTH, expand=True)
parameter_input.pack(fill=tk.BOTH, expand=True)

#菜单1
original_image_area = ttk.Treeview(file_name_show)
original_image_area.heading("#0", text="待处理图像(文件名不能重复)", anchor=tk.CENTER)
original_image_area.pack(fill=tk.BOTH, padx=4, pady=5)

def pop1(event):
    menu_t1.post(event.x_root,  event.y_root)

def show_image_1(event):
    global selected_file_in1
    item = original_image_area.selection()
    if item:
        item_text = original_image_area.item(item, "text")
        selected_file_in1 = next(file for file in imported_files if item_text in file)
        show_photo(selected_file_in1)
        bottom_tips.configure(text='原图!')

def dele1():
    global selected_file_in1 , imported_files
    if selected_file_in1:
        imported_files = [file for file in imported_files if file != selected_file_in1]
        for item in original_image_area.get_children():
            item_text = original_image_area.item(item, "text")
            if item_text in selected_file_in1:
                original_image_area.delete(item)
                break  
        original_image_area.selection_remove(original_image_area.selection())
        selected_file_in1 = None
    else:
        bottom_tips.configure(text='请选中一个文件')


original_image_area.bind('<ButtonRelease-1>', show_image_1)
original_image_area.bind('<ButtonRelease-3>', pop1)
menu_t1 = tk.Menu(file_name_show, tearoff=False)
menu_t1.add_command(label="删除", command=dele1)

lab = tk.Label(parameter_input, text='比例尺信息')
lab.pack(side=tk.TOP, fill=tk.X)
param1 = tk.LabelFrame(parameter_input, text=f'真实长度(nm)')
param2 = tk.LabelFrame(parameter_input, text=f'图中像素长度')
param3 = tk.LabelFrame(parameter_input, text=f'最大粒子直径(像素):')
param4 = tk.LabelFrame(parameter_input, text=f'最小粒子直径(像素):')
param5 = tk.LabelFrame(parameter_input, text=f'Sigma数量:')
param6 = tk.LabelFrame(parameter_input, text=f'阈值:')

param1.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
param2.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
separator = ttk.Separator(parameter_input, orient=tk.HORIZONTAL)
separator.pack(in_=parameter_input, side=tk.TOP, fill=tk.X, pady=5)
lab_para = tk.Label(parameter_input, text='参数')
lab_para.pack(side=tk.TOP, fill=tk.X)
param3.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
param4.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
param5.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
param6.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

def measure_and_set_blank2():
    clear_points()  # 清除现有的点
    img_area.bind('<Button-1>', click_event)  # 鼠标按下
    img_area.bind('<B1-Motion>', move_event)  # 鼠标移动
    img_area.bind('<ButtonRelease-1>', release_event)  # 鼠标释放
    messagebox.showinfo("提示", "请按住鼠标左键从第一个点拖动到第二个点，然后释放。")


blank1 = tk.Entry(param1)
blank1.pack(fill=tk.X, padx=5, pady=2)
measure_button = tk.Button(param2, text='点击测量', command=measure_and_set_blank2)
measure_button.pack(side=tk.LEFT, padx=5)
blank2 = tk.Entry(param2)
blank2.pack(fill=tk.X, padx=5, pady=2)
blank3 = tk.Entry(param3)
blank3.pack(fill=tk.X, padx=5, pady=2)
blank4 = tk.Entry(param4)
blank4.pack(fill=tk.X, padx=5, pady=2)
blank5 = tk.Entry(param5)
blank5.pack(fill=tk.X, padx=5, pady=2)
blank6 = tk.Entry(param6)
blank6.pack(fill=tk.X, padx=5, pady=2)

save_param = tk.Frame(parameter_input)
save_param.pack(side=tk.TOP, pady=2)
tk.Button(save_param, text='保存参数', command=lambda: get_scale_params()).pack(side=tk.LEFT, padx=5)

'''
窗口中间___________________________________________________________________________________________________________________________
'''

file_name_show_2 = tk.Frame(pane6)
file_name_show_2.pack(fill=tk.BOTH, expand=True)

#菜单2
processed_image_area = ttk.Treeview(file_name_show_2)
processed_image_area.heading("#0", text="处理后图片", anchor=tk.CENTER)
processed_image_area.pack(fill=tk.BOTH, padx=4, pady=5)
processed_image_area.bind('<ButtonRelease-1>', show_image_2)

menu_t2 = tk.Menu(original_image_area, tearoff=False)
menu_t2.add_command(label="处理图片")
menu_t2.add_separator()
menu_t2.add_command(label="查看原图")
menu_t2.add_command(label="查看结果图")

table = ttk.Treeview(pane7, columns=['Blob Number', 'Diameter (nm)'], show='headings', height=int(screen_height))
for col in table['columns']:
    table.heading(col, text=col)
table.column("#1", anchor=tk.CENTER, width=100)
table.column("#2", anchor=tk.CENTER, width=200)
table.pack(fill=tk.BOTH, expand=True)
info = [[0,'-']]
for itm in info:
    table.insert("",tk.END,values=itm)

# 创建右键菜单
popup_menu = tk.Menu(root, tearoff=0)
popup_menu.add_command(label="删除", command=lambda: delete_row_from_csv())
table.bind("<Button-3>", on_right_click)
'''
窗口右侧___________________________________________________________________________________________________________________________
'''
distance = None
points = []

def clear_points():
    global points
    points = []

def click_event(event):
    global points, drawing
    clear_points()
    img_area.delete("line") 
    points = [(event.x, event.y)]
    drawing = True  

def move_event(event):
    global points, line_id, drawing
    if drawing and len(points) == 1: 
        img_area.delete("line")
        x0, y0 = points[0]
        x1, y1 = event.x, event.y
        line_id = img_area.create_line(x0, y0, x1, y1, fill='red', width=2, tags="line")

def stop_measuring():
    img_area.unbind('<Button-1>')
    img_area.unbind('<ButtonRelease-1>')

def draw_line(x1, y1, x2, y2):
    global line_id
    img_area.delete("line")
    line_id = img_area.create_line(x1, y1, x2, y2, fill='red', width=2, tags="line")

def clear_line():
    global line_id
    if line_id:  
        img_area.delete(line_id)
        line_id = None 

def release_event(event):
    global points, drawing, distance
    if drawing:
        points.append((event.x, event.y))
        drawing = False
        if len(points) == 2:
            x1, y1 = points[0]
            x2, y2 = points[1]
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) /factor
            draw_line(x1, y1, x2, y2)
            if messagebox.askyesno("确认", f"两点之间的像素距离是: {distance:.2f}。保存此测量结果吗？"):
                blank2.delete(0, tk.END)
                blank2.insert(0, distance)
                clear_line()
                stop_measuring()
            else:
                clear_line()
            clear_points()

def pop_img(event):
    try:
        img_menu.post(event.x_root, event.y_root)
    except Exception as e:
        print(f"Error in right click: {e}")

img_area = tk.Canvas(pane4)
img_area.pack()


img_area.bind('<ButtonRelease-3>', pop_img)
img_menu = tk.Menu(img_area, tearoff=0)
img_menu.add_command(label="编辑", command=delete_row_from_img)

root.protocol('WM_DELETE_WINDOW', delete_op)


if __name__ == "__main__":
    root.mainloop()