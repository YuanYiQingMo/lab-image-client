import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from tkinter import filedialog
import filetype
import os
from PIL import Image, ImageTk, ImageEnhance, ImageOps
from collections import defaultdict
import csv
import shutil



from skimage import io, feature
import math
import csv
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

'''
算法部分_______________________________________________________________________________________________________________________
'''
output_folder = "output_folder"
os.makedirs(output_folder, exist_ok=True)

enhance_folder = "enhance_folder"
os.makedirs(enhance_folder, exist_ok=True)

def op_file(op_file1, op_file2): # 处理单个图像
    image = io.imread(op_file1)
    cropped_image = image[:2048, :] # 裁剪图像

    # 检测图像中的斑点
    scale_length_mm = allfiles_path[op_file1][op_file2][1]
    scale_length_pixels = allfiles_path[op_file1][op_file2][2]
    max_sigma = allfiles_path[op_file1][op_file2][3]
    min_sigma = allfiles_path[op_file1][op_file2][4]
    num_sigma = allfiles_path[op_file1][op_file2][5]
    threshold = allfiles_path[op_file1][op_file2][6]
    pixels_per_mm = scale_length_pixels / scale_length_mm

    # 根据图片特定的参数检测斑点
    blobs_log = feature.blob_log(cropped_image, 
                                 max_sigma=max_sigma, 
                                 min_sigma=min_sigma, 
                                 num_sigma=num_sigma, 
                                 threshold=threshold)
    blobs_log[:, 2] = blobs_log[:, 2] * math.sqrt(2)
    
    # Filter out overlapping particles
    # filtered_blobs_log = filter_overlapping_particles(blobs_log)
    filtered_blobs_log = blobs_log
    print(f"Number of blobs detected: {len(blobs_log)}")
    print(f"Sample blob: {blobs_log[0]}")

    # 创建CSV文件记录每个斑点的粒径
    with open(allfiles_path[op_file1][op_file2][8], 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Blob Number', 'Diameter (nm)'])
        for j, blob in enumerate(filtered_blobs_log):  # 注意这里使用过滤后的 blobs
            # 将直径转换为纳米单位，假设 scale_length_pixels 对应于 scale_length_mm 毫米
            diameter_pixels = 2 * blob[2]
            diameter_mm = diameter_pixels / pixels_per_mm
            diameter_nm = diameter_mm   
            writer.writerow([j+1, f"{diameter_nm:.4f}"])

    # 创建 Matplotlib 图表，将原图像和检测到的斑点进行可视化
    fig1 = plt.figure()
    ax1 = fig1.subplots(1, 1)
    ax1.imshow(image, cmap='gray', interpolation='nearest')

    # 遍历每个检测到的斑点
    for j, blob in enumerate(filtered_blobs_log):
        y, x, r  = blob
        # 在原图上绘制红色圆圈表示检测到的斑点
        c = plt.Circle((x, y), r, color='red', linewidth=0.5, fill=False)
        ax1.add_patch(c)
        # 添加文本标签来标记斑点的序号
        ax1.text(x, y, str(j+1), color='yellow', fontsize=5)

    # 保存处理后的图像
    fig1.savefig(allfiles_path[op_file1][op_file2][7], dpi=480)
    plt.close(fig1)

    data_op1 = []
    data_op2 = []
    with open(allfiles_path[op_file1][op_file2][8]) as csvfile:
        csv_reader = csv.reader(csvfile)   # 使用csv.reader读取csvfile中的文件
        # header = next(csv_reader)        # 读取第一行每一列的标题
        for row in csv_reader:             # 将csv 文件中的数据保存到data中
            data_op1.append(row[1])        # 选择某一列加入到data数组中
        del data_op1[0]
    for x in data_op1:
        data_op2.append(float(x))
    data_op2.sort()
    fig2 = plt.figure()
    ax2 = fig2.subplots(1, 1)
    ax2.hist(data_op2, density=True, color='lightgreen', ec='black')
    ax2.annotate(f'd = {calculate_mean_diameter(data_op2):.2f} ± {calculate_spread_parameter(data_op2):.2f}', (0.7, 0.8), xycoords='figure fraction', annotation_clip=False)
    sns.kdeplot(data_op2, fill=False)
    fig2.savefig(allfiles_path[op_file1][op_file2][9], dpi=480)
    plt.close(fig2)

def calculate_mean_diameter(data):
    total = float()
    count = 0
    for d in data:
        total += d
        count += 1
    mean_diameter = total/count
    return mean_diameter

def calculate_spread_parameter(data):
    log_data = np.log(data)
    spread_parameter = np.std(log_data)
    return spread_parameter

def output():
    try:
        p1 = tree1.item(tree1.selection()[0],"values")[0]
    except IndexError:
        lab_b.configure(text='请先于一级菜单处选择文件, 再进行相关操作')
        return
    except:
        lab_b.configure(text='错误！(ch p1)')
        return
    try:
        p2 = int(tree2.item(tree2.selection()[0],"values")[0])
    except IndexError:
        p2 = -1
    except:
        lab_b.configure(text='错误！(ch p2)')
        return

    if os.access(allfiles_path[p1][p2][7], os.F_OK):
        lab_b.configure(text='请勿重复处理！')
        return
    else:
        op_file(p1, p2)
    lab_b.configure(text='当前文件已处理完毕！')

def outputs():
    for p1 in allfiles_path:
        p2 = 0
        for qi in allfiles_path[p1]:
            if os.access(allfiles_path[p1][p2][7], os.F_OK):
                continue
            else:
                op_file(p1, p2)
            p2 += 1
    lab_b.configure(text='文件已处理完毕！')

def delete_op():
    if messagebox.askyesnocancel(title='提醒！', message='本窗口关闭后，未导出的文件将会清除，请问是否继续关闭。'):
        file_list = os.listdir(output_folder)
        for file in file_list:
            file_path = os.path.join(output_folder, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        root.destroy()

'''
窗口相关函数_________________________________________________________________________________________________________________________________________
'''
# 菜单1
# p1 = tree1.item(tree1.selection()[0],"values")[0]
def show1(e): # 点击菜单1上节点
    menu_t4.entryconfig(0,state='disabled')
    try:
        p1 = tree1.item(tree1.selection()[0],"values")[0]
    except IndexError:
        lab_b.configure(text='请先于菜单处选择文件，再进行相关操作')
        return 0
    except:
        lab_b.configure(text='出现未知问题，请重复操作。如无法操作，请进行咨询~')
        return 0
    # 显示节点默认参数
    lf1.configure(text=f'scale_length_mm : {allfiles_path[p1][0][1]}')
    lf2.configure(text=f'scale_length_pixels : {allfiles_path[p1][0][2]}')
    lf3.configure(text=f'max_sigma : {allfiles_path[p1][0][3]}')
    lf4.configure(text=f'min_sigma : {allfiles_path[p1][0][4]}')
    lf5.configure(text=f'num_sigma : {allfiles_path[p1][0][5]}')
    lf6.configure(text=f'threshold : {allfiles_path[p1][0][6]}')
    # 显示节点不同参数子节点（见菜单2）
    for child in tree2.get_children():
        tree2.delete(child)
    i = 0
    for x in allfiles_path[p1]:
        tree2.insert('', 0, text=allfiles_path[p1][i][0], values=(i))
        i += 1
    show_photo(p1)
    lab_b.configure(text='原图!')
    menu_t4.entryconfig(0,state='disabled')


def pop1(event):
    menu_t1.post(event.x_root,  event.y_root)

def pop2(event):
    menu_t2.post(event.x_root,  event.y_root)

def pop3(event):
    menu_t3.post(event.x_root,  event.y_root)

def pop4(event):
    menu_t4.post(event.x_root,  event.y_root)

def dele1():
    p1 = tree1.item(tree1.selection()[0],"values")[0]
    allfiles_path.pop(p1)
    tree1.delete(tree1.selection()[0])

# 菜单2
# p2 = tree2.item(tree2.selection()[0],"values")[0]
show_photo_cs = 1
def show2(e):
    p1 = tree1.item(tree1.selection()[0],"values")[0]
    p2 = int(tree2.item(tree2.selection()[0],"values")[0])
    # 显示节点默认参数
    lf1.configure(text=f'scale_length_mm : {allfiles_path[p1][p2][1]}')
    lf2.configure(text=f'scale_length_pixels : {allfiles_path[p1][p2][2]}')
    lf3.configure(text=f'max_sigma : {allfiles_path[p1][p2][3]}')
    lf4.configure(text=f'min_sigma : {allfiles_path[p1][p2][4]}')
    lf5.configure(text=f'num_sigma : {allfiles_path[p1][p2][5]}')
    lf6.configure(text=f'threshold : {allfiles_path[p1][p2][6]}')
    # 寻找处理后png，没有，则显示原图
    global show_photo_cs
    if os.access(allfiles_path[p1][p2][7], os.F_OK):
        if show_photo_cs == 1:
            show_photo(allfiles_path[p1][p2][7])
            lab_b.configure(text='结果图！')
            show_photo_cs -= 1
            menu_t4.entryconfig(0,state='normal')
        else:
            show_photo(allfiles_path[p1][p2][9])
            lab_b.configure(text='粒径分布图！')
            show_photo_cs += 1
            menu_t4.entryconfig(0,state='disabled')

        for child in table.get_children():
            table.delete(child)
        data = []
        with open(allfiles_path[p1][p2][8]) as csvfile:
            csv_reader = csv.reader(csvfile)  # 使用csv.reader读取csvfile中的文件
            # header = next(csv_reader)        # 读取第一行每一列的标题
            for row in csv_reader:            # 将csv 文件中的数据保存到data中
                data.append(row[1])           # 选择某一列加入到data数组中
            data[0] = '-'
            for i, j in enumerate(data):
                table.insert("",tk.END,values=[i, j])
    else:
        show_photo(p1)
        lab_b.configure(text='尚未处理, 显示原图')
        menu_t4.entryconfig(0,state='disabled')

# TODO删除点
def delete_point_by_index():
    # 这里使用
    print("删除点")

delete_img_file = list()
def delete_point_by_click():
    #打开删除窗口
    menu_t4.entryconfig(0,state='disabled')
    lab_b.configure(text='请先关闭选择窗口')

    delete_windows = tk.Toplevel()
    delete_windows.title("右键粒径删除")

    p1 = tree1.item(tree1.selection()[0],"values")[0]
    p2 = int(tree2.item(tree2.selection()[0],"values")[0])

    img_path = allfiles_path[p1][p2][7]

    delete_windows.geometry(f"{int(screen_width*0.9)}x{int(screen_height*0.9)}+{int(screen_width*0.025)}+{int(screen_height*0.025)}")

    delete_img_lb = tk.Label(delete_windows)
    delete_img_lb.pack(fill='both')

    w, h = Image.open(os.path.abspath(img_path)).size
    factor = min([1.0*int(delete_windows.winfo_screenwidth())/w, 1.0*int(delete_windows.winfo_screenheight())/h])
    width = int(w*factor)
    height = int(h*factor)
    resize_img = ImageTk.PhotoImage(Image.open(os.path.abspath(img_path)).resize((width, height)))
    delete_img_file.append(resize_img)
    delete_img_lb.configure(image=delete_img_file[-1])

    delete_windows.bind('<ButtonRelease-3>',pop_delete)
    delete_windows_menu = tk.Menu(delete_windows, tearoff=False)
    delete_windows_menu.add_command(label="删除",command=delete_point)
    
    click_point = list()

    def delete_point():
        x, y = click_point
        print(x,y)
    def pop_delete(event):
        delete_windows_menu.post(event.x_root,  event.y_root)
        click_point.append((event.x_root,  event.y_root))
        print(click_point)

# 衬度翻转
def contrastFlipping():
    image_path = tree1.item(tree1.selection()[0],"values")[0]
    image = Image.open(image_path)
    imgF = Image.fromarray(np.array(image))
    res = ImageOps.invert(imgF)
    save_name = f'{os.path.basename(os.path.splitext(image_path)[0]) }_preFlip.tif'
    res.save(os.path.abspath(os.path.join(os.path.abspath(enhance_folder), save_name)))
    addFile(os.path.join(os.path.abspath(enhance_folder), save_name).replace("\\","/"))


# 对比度增强
def contrastEnhancement():
    image_path = tree1.item(tree1.selection()[0],"values")[0]
    contrast = 1.5
    image = Image.open(image_path)
    imgR = Image.fromarray(np.array(image))
    enh_con = ImageEnhance.Contrast(imgR)
    image_contrasted = enh_con.enhance(contrast)
    save_name = f'{os.path.basename(os.path.splitext(image_path)[0]) }_preCon.tif'
    image_contrasted.save(os.path.abspath(os.path.join(os.path.abspath(enhance_folder), save_name)))
    addFile(os.path.join(os.path.abspath(enhance_folder), save_name).replace("\\","/"))
    return image_contrasted

# 将处理好的图像加入tree1
def addFile(file_path):
    f_path = set()
    f_path.add(file_path)
    for x in f_path.difference(allfiles_path.keys()):
        # 0:name  1,2,3,4,5,6:参数  7:png路径  8:csv路径 9:histogram路径
        allfiles_path[x] = [[os.path.basename(os.path.splitext(x)[0]),
                             float(20), float(218), int(55), int(5), int(20), float(0.1), 
                             os.path.abspath(os.path.join(
                                 output_folder, f'processed_{os.path.basename(os.path.splitext(x)[0])}.png')), 
                             os.path.abspath(os.path.join(
                                 output_folder, f'diameters_{os.path.basename(os.path.splitext(x)[0])}.csv')), 
                             os.path.abspath(os.path.join(
                                 output_folder, f'histogram_{os.path.basename(os.path.splitext(x)[0])}.png'))]]
        tree1.insert('', 0, text=allfiles_path[x][0][0], values=(x))



# 选择文件
allfiles_path = defaultdict(list) # 文件库defaultdict(list)
def select_files():
    f_name = [] # 临时格式错误文件名库
    f_path = set() # 临时文件地址库
    files_path = filedialog.askopenfilenames() # 打开并选择文件
    for x in files_path:
        kind = filetype.guess(x) # 读取文件类型
        if kind is None:
            f_name.append(os.path.basename(x))
            continue
        elif kind.mime == 'image/tiff':
            f_path.add(x)
        else:
            f_name.append(os.path.basename(x))
    if f_path != {}:
        for x in f_path.difference(allfiles_path.keys()):
            # 0:name  1,2,3,4,5,6:参数  7:png路径  8:csv路径 9:histogram路径
            allfiles_path[x] = [[os.path.basename(os.path.splitext(x)[0]), 
                                 float(20), float(218), int(55), int(5), int(20), float(0.1), 
                                 os.path.abspath(os.path.join(
                                     output_folder, f'processed_{os.path.basename(os.path.splitext(x)[0])}.png')), 
                                 os.path.abspath(os.path.join(
                                     output_folder, f'diameters_{os.path.basename(os.path.splitext(x)[0])}.csv')), 
                                 os.path.abspath(os.path.join(
                                     output_folder, f'histogram_{os.path.basename(os.path.splitext(x)[0])}.png'))]]
            tree1.insert('', 0, text=allfiles_path[x][0][0], values=(x))
    if f_name != []:
        lab_b.configure(text='格式错误\t'f'{f_name}不是tif格式')

# 参数相关
def ch():
    try:
        p1 = tree1.item(tree1.selection()[0],"values")[0]
    except IndexError:
        lab_b.configure(text='请先于一级菜单处选择文件, 再进行相关操作')
        return 0
    except:
        lab_b.configure(text='错误！(ch p1)')
        return 0
    try:
        p2 = int(tree2.item(tree2.selection()[0],"values")[0])
    except IndexError:
        p2 = -1
    except:
        lab_b.configure(text='错误！(ch p2)')
        return 0
    c = []
    i = 1
    for x in [en1.get(), en2.get(), en3.get(), en4.get(), en5.get(), en6.get()]:
        try:
            y = float(x)
        except:
            y = allfiles_path[p1][p2][i]
        c.append(y)
        i += 1
    j = 0
    for x in allfiles_path[p1]:
        j += 1
    processed_name = allfiles_path[p1][0][0] + f'({j})'
    diameters_name = allfiles_path[p1][0][0] + f'({j})'
    histogram_name = allfiles_path[p1][0][0] + f'({j})'
    allfiles_path[p1].append([allfiles_path[p1][0][0] + f'({j})', 
                            c[0], c[1], int(c[2]), int(c[3]), int(c[4]), c[5], 
                            os.path.abspath(os.path.join(output_folder, f'processed_{processed_name}.png')), 
                            os.path.abspath(os.path.join(output_folder, f'diameters_{diameters_name}.csv')), 
                            os.path.abspath(os.path.join(output_folder, f'histogram_{histogram_name}.png'))])
    lf1.configure(text=f'scale_length_mm : {allfiles_path[p1][j][1]}')
    lf2.configure(text=f'scale_length_pixels : {allfiles_path[p1][j][2]}')
    lf3.configure(text=f'max_sigma : {allfiles_path[p1][j][3]}')
    lf4.configure(text=f'min_sigma : {allfiles_path[p1][j][4]}')
    lf5.configure(text=f'num_sigma : {allfiles_path[p1][j][5]}')
    lf6.configure(text=f'threshold : {allfiles_path[p1][j][6]}')

    en1.delete(0, tk.END)
    en2.delete(0, tk.END)
    en3.delete(0, tk.END)
    en4.delete(0, tk.END)
    en5.delete(0, tk.END)
    en6.delete(0, tk.END)

    for child in tree2.get_children():
        tree2.delete(child)
    k = 0
    for x in allfiles_path[p1]:
        tree2.insert('', 0, text=allfiles_path[p1][k][0], values=(k))
        k += 1

    lab_b.configure(text='修改完成')

# 图片显示相关
img_path1 = []
p_folder1 = []
def resize(resize1): # resize1:图片地址
    w, h = Image.open(os.path.abspath(resize1)).size
    factor = min([1.0*int(pane4.winfo_width())/w, 1.0*int(pane4.winfo_height())/h])
    width = int(w*factor)
    height = int(h*factor)
    return ImageTk.PhotoImage(Image.open(os.path.abspath(resize1)).resize((width, height)))

filename = list()
def show_photo(show_path1): # show_path1:图片地址
    try:
        filename.append(resize(show_path1))
        img_lb.configure(image=filename[-1])
    except:
        lab_b.configure(text='显示异常')

def open_folder():
    os.startfile(output_folder)

def copy_op():
    try:
        p1 = tree1.item(tree1.selection()[0],"values")[0]
    except IndexError:
        lab_b.configure(text='请先于一级菜单处选择文件, 再进行相关操作')
        return 0
    except:
        lab_b.configure(text='错误！(ch p1)')
        return 0
    try:
        p2 = int(tree2.item(tree2.selection()[0],"values")[0])
    except IndexError:
        p2 = -1
    except:
        lab_b.configure(text='错误！(ch p2)')
        return 0
    if os.access(allfiles_path[p1][p2][7], os.F_OK):   
        Folderpath = filedialog.askdirectory()
        shutil.copy(allfiles_path[p1][p2][7], Folderpath)
        shutil.copy(allfiles_path[p1][p2][8], Folderpath)
        shutil.copy(allfiles_path[p1][p2][9], Folderpath)
    else:
        lab_b.configure(text='尚未进行文件处理')

# 读取csv
# def read_csv(path, i):
#    data = pd.read_csv(allfiles_path[path][i]['csv'], sep=',', header='infer', usecols=[5])
#    print(data)
   
'''
根窗口部分________________________________________________________________________________________________________
'''
root = tk.Tk() #根窗口
root.title("文件处理(推荐全屏使用)") #窗口名称
screen_width = root.winfo_screenwidth() #获取显示器宽度
screen_height = root.winfo_screenheight() #获取显示器高度
#将窗口界面与显示屏相关联，大概在80%左右
root.geometry(f"{int(screen_width*0.8)}x{int(screen_height*0.8)}+{int(screen_width*0.1)}+{int(screen_height*0.05)}")

'''
抬头菜单栏_________________________________________________________________________________________________________
'''
menu = tk.Menu(root, tearoff=False)
menu.add_separator()

menu_wj = tk.Menu(menu, tearoff=False)
menu_wj.add_command(label='选择文件', command=select_files)
menu_wj.add_command(label='打开结果文件夹', command=open_folder)

menu_gj = tk.Menu(menu, tearoff=False)
menu_gj.add_command(label='处理 当前文件', command=output)
menu_gj.add_command(label='批量处理 列表所有文件', command=outputs)
menu_gj.add_separator()
menu_gj.add_command(label='对比度增强 当前文件', command=contrastEnhancement)
menu_gj.add_command(label='衬度翻转 当前文件',command=contrastFlipping)
menu_gj.add_separator()
menu_gj.add_command(label='导出当前文件结果', command=copy_op)

menu_bz = tk.Menu(menu, tearoff=False)
menu_bz.add_command(label='功能说明')

menu.add_cascade(label='文件', menu=menu_wj)
menu.add_cascade(label='工具', menu=menu_gj)
menu.add_cascade(label='帮助', menu=menu_bz)
root.config(menu=menu)

'''
底部信息显示栏________________________________________________________________________________________________________________
'''
frm_b = tk.Frame(root)
lab_b = tk.Label(frm_b, text='欢迎使用')
frm_b.pack(side=tk.BOTTOM, fill=tk.X, expand=True, padx=5, pady=2)
lab_b.pack(anchor=tk.W)

'''
窗口分区___________________________________________________________________________________________________________________________
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
frame1 = tk.Frame(pane2)
frame2 = tk.Frame(pane3)
frame3 = tk.Frame(pane4)
frame1.pack(fill=tk.BOTH, expand=True)
frame2.pack(fill=tk.BOTH, expand=True)
frame3.pack(fill=tk.BOTH, expand=True)

#菜单1
tree1 = ttk.Treeview(frame1)
tree1.heading("#0", text="一级目录(文件名不能重复)", anchor=tk.CENTER)
tree1.pack(fill=tk.BOTH, padx=4, pady=5)

tree1.bind('<ButtonRelease-1>', show1)
tree1.bind('<ButtonRelease-3>', pop1)

menu_t1 = tk.Menu(frame1, tearoff=False)
menu_t1.add_command(label='处理文件', command=output)
menu_t1.add_separator()
menu_t1.add_command(label="删除", command=dele1)

#参数
lab = tk.Label(frame2, text='相关参数')
var = [20, 218, 55, 5, 20, 0.1]
lf1 = tk.LabelFrame(frame2, text=f'scale_length_mm : - ')
lf2 = tk.LabelFrame(frame2, text=f'scale_length_pixels : - ')
lf3 = tk.LabelFrame(frame2, text=f'max_sigma : - ')
lf4 = tk.LabelFrame(frame2, text=f'min_sigma : - ')
lf5 = tk.LabelFrame(frame2, text=f'num_sigma : - ')
lf6 = tk.LabelFrame(frame2, text=f'threshold : - ')
lab.pack(side=tk.TOP, fill=tk.X)
lf1.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
lf2.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
lf3.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
lf4.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
lf5.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
lf6.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

en1 = tk.Entry(lf1)
en1.pack(fill=tk.X, padx=5, pady=2)
en2 = tk.Entry(lf2)
en2.pack(fill=tk.X, padx=5, pady=2)
en3 = tk.Entry(lf3)
en3.pack(fill=tk.X, padx=5, pady=2)
en4 = tk.Entry(lf4)
en4.pack(fill=tk.X, padx=5, pady=2)
en5 = tk.Entry(lf5)
en5.pack(fill=tk.X, padx=5, pady=2)
en6 = tk.Entry(lf6)
en6.pack(fill=tk.X, padx=5, pady=2)

frm_bu = tk.Frame(frame2)
frm_bu.pack(side=tk.TOP, pady=2)
tk.Button(frm_bu, text='修改参数', command=ch).pack(side=tk.LEFT, padx=5)
tk.Button(frm_bu, text='恢复默认').pack(side=tk.LEFT, padx=5)

'''
窗口中间___________________________________________________________________________________________________________________________
'''
frame4 = tk.Frame(pane6)
frame4.pack(fill=tk.BOTH, expand=True)

#菜单2
tree2 = ttk.Treeview(frame4)
tree2.heading("#0", text="二级目录", anchor=tk.CENTER)
tree2.pack(fill=tk.BOTH, padx=4, pady=5)

tree2.bind('<ButtonRelease-1>', show2)
tree2.bind('<ButtonRelease-3>', pop2)

menu_t2 = tk.Menu(frame1, tearoff=False)
menu_t2.add_command(label="处理图片", command=output)

#表格
table = ttk.Treeview(pane7, columns=['Blob Number', 'Diameter (nm)'], show='headings', height=int(screen_height))
for col in table['columns']:
    table.heading(col, text=col)
table.column("#1", anchor=tk.CENTER, width=100)
table.column("#2", anchor=tk.CENTER, width=200)
table.pack(fill=tk.BOTH, expand=True)

table.bind('<ButtonRelease-3>', pop3)
menu_t3 = tk.Menu(frame1, tearoff=False)
menu_t3.add_command(label="删除", command=delete_point_by_index)

info = [[0,'-']]
for itm in info:
    table.insert("",tk.END,values=itm)

'''
窗口右侧___________________________________________________________________________________________________________________________
'''
img_lb = tk.Label(pane4)
img_lb.pack()

img_lb.bind('<ButtonRelease-3>', pop4)
menu_t4 = tk.Menu(img_lb, tearoff=False)
edit_state = 'disable' #恢复 normal
menu_t4.add_command(label="编辑(删除指定粒径)", command=delete_point_by_click,state=edit_state)


root.protocol('WM_DELETE_WINDOW', delete_op)

#——————分割线——————#
if __name__ == "__main__":
    root.mainloop()