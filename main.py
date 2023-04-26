import tkinter as tk
import tkinter.ttk as ttk
import cv2
from tkinter import filedialog
from tkinter import messagebox
import keyboard as k
import win32api
import win32con
import numpy as np



zoom = 1
wheel_step = 0.05
wx = 304
wy = 32
x1 = 0
y1 = 0
x2 = 0
y2 = 0

font = cv2.FONT_HERSHEY_SIMPLEX
yellow = (0, 255, 255)
indigo = (255, 255, 0)
white = (255, 255, 255)
black = (0, 0, 0)

counts = {}
pics = {}
masks = {}
history = {}

def show_help():
    messagebox.showinfo('使用说明',
    '''
    操作说明：
    1. 标记
        1. <鼠标左键单击> 标记阳性细胞
        2. <鼠标右键单击> 标记阴性细胞
    2. 移动
        1. <按住Ctrl> + <鼠标左键拖动> 移动图片
        2. <鼠标滚轮> 缩放图片
    3. 管理
        1. 双击 <已经打开的文件> 列表切换显示图片
        2. <Ctrl + Z> 撤回上一步标记
    4. 导出
        1. <Ctrl + S> 导出当前数据
        2. 默认导出 *.csv 格式
    --------
    PS: 中文显示错误是正常现象，编者也没有很好的解决办法，能成功读出图片就已经很好了
    '''
    )


def cv_imread(file_path):
    #imdedcode读取的是RGB图像
    cv_img = cv2.imdecode(np.fromfile(file_path,dtype=np.uint8),-1)
    return cv_img

def zh_ch(string):
    return string.encode("gbk").decode('UTF-8', errors='ignore')

# def set_move():
#     try:
#         cv2.setMouseCallback(zh_ch(current.split('\\')[-1]), move)
#     except:
#         pass
#     btn4['relief'] = tk.SUNKEN
#     btn5['relief'] = tk.RAISED
#
# def set_count():
#     try:
#         cv2.setMouseCallback(zh_ch(current.split('\\')[-1]), count)
#     except:
#         pass
#     btn5['relief'] = tk.SUNKEN
#     btn4['relief'] = tk.RAISED

# def move(event, x, y, flags, param):
#     win32api.SetCursor(win32api.LoadCursor(0, win32con.IDC_SIZEALL))
#     global zoom
#     global wx, wy
#     global x1, y1, x2, y2
#     if event == cv2.EVENT_MOUSEWHEEL:
#         if flags > 0:
#             zoom += wheel_step
#             if zoom > 1 + (wheel_step * 40):
#                 zoom = 1 + (wheel_step * 40)
#                 return
#         else:
#             zoom -= wheel_step
#             if zoom < 1 - (wheel_step * 4):
#                 zoom = 1 - (wheel_step * 4)
#                 return
#         dst = cv2.resize(pics[current], dsize = None, fx = zoom, fy = zoom, interpolation = cv2.INTER_LINEAR)
#         cv2.imshow(zh_ch(current.split('\\')[-1]), dst)
#     if event == cv2.EVENT_LBUTTONDOWN:
#         x1, y1 = x, y
#     elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):
#         x2, y2 = x, y
#         wx = wx + x2 - x1
#         wy = wy + y2 - y1
#         cv2.moveWindow(zh_ch(current.split('\\')[-1]), wx, wy)
#     elif event == cv2.EVENT_LBUTTONUP:
#         x2, y2 = x, y
#         wx = wx + x2 - x1
#         wy = wy + y2 - y1
#         cv2.moveWindow(zh_ch(current.split('\\')[-1]), wx, wy)


def count(event, x, y, flags, param):
    global zoom
    global wx, wy
    global x1, y1, x2, y2

    if event == cv2.EVENT_LBUTTONDOWN and not(flags & cv2.EVENT_FLAG_CTRLKEY):
        cv2.circle(pics[current], (int(x//zoom),int(y//zoom)), 4, black, -1)
        cv2.circle(pics[current], (int(x//zoom), int(y//zoom)), 3, yellow, -1)
        cv2.putText(pics[current], '+', (int(x//zoom - 4),int(y//zoom + 3)), font, 0.3, black, 1)
        dst = cv2.resize(pics[current], dsize=None, fx=zoom, fy=zoom, interpolation=cv2.INTER_LINEAR)
        cv2.imshow(zh_ch(current.split('\\')[-1]), dst)
        pos.set(pos.get()+1)
        total.set(pos.get() + neg.get())
        if total.get() != 0:
            r = pos.get() / total.get() * 100
        rate.set("{:.2f}%".format(r))
        counts[current]['pos'] += 1
        counts[current]['total'] += 1
        counts[current]['rate'] = counts[current]['pos']/counts[current]['total']
        history[current].append([1, int(x//zoom), int(y//zoom)])
    elif event == cv2.EVENT_LBUTTONDOWN and (flags & cv2.EVENT_FLAG_CTRLKEY):
        x1, y1 = x, y
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON) and (flags & cv2.EVENT_FLAG_CTRLKEY):
        x2, y2 = x, y
        wx = wx + x2 - x1
        wy = wy + y2 - y1
        cv2.moveWindow(zh_ch(current.split('\\')[-1]), wx, wy)
    elif event == cv2.EVENT_LBUTTONUP and (flags & cv2.EVENT_FLAG_CTRLKEY):
        x2, y2 = x, y
        wx = wx + x2 - x1
        wy = wy + y2 - y1
        cv2.moveWindow(zh_ch(current.split('\\')[-1]), wx, wy)

    if event == cv2.EVENT_MOUSEWHEEL:
        if flags > 0:
            zoom += wheel_step
            if zoom > 1 + (wheel_step * 40):
                zoom = 1 + (wheel_step * 40)
                return
        else:
            zoom -= wheel_step
            if zoom < 1 - (wheel_step * 4):
                zoom = 1 - (wheel_step * 4)
                return
        dst = cv2.resize(pics[current], dsize = None, fx = zoom, fy = zoom, interpolation = cv2.INTER_LINEAR)
        cv2.imshow(zh_ch(current.split('\\')[-1]), dst)

    if event == cv2.EVENT_RBUTTONDOWN:
        cv2.circle(pics[current], (int(x//zoom),int(y//zoom)), 4, black, -1)
        cv2.circle(pics[current], (int(x//zoom),int(y//zoom)), 3, indigo, -1)
        cv2.putText(pics[current], '-', (int(x//zoom) - 4,int(y//zoom) + 3), font, 0.3, black, 1)
        dst = cv2.resize(pics[current], dsize=None, fx=zoom, fy=zoom, interpolation=cv2.INTER_LINEAR)
        cv2.imshow(zh_ch(current.split('\\')[-1]), dst)
        neg.set(neg.get()+1)
        total.set(pos.get() + neg.get())
        if total.get() != 0:
            r = pos.get() / total.get() * 100
        rate.set("{:.2f}%".format(r))
        counts[current]['neg'] += 1
        counts[current]['total'] += 1
        counts[current]['rate'] = counts[current]['pos']/counts[current]['total']
        history[current].append([0, int(x//zoom), int(y//zoom)])

def open_pic():
    global current
    global zoom
    global wx, wy
    cv2.destroyAllWindows()
    current = filedialog.askopenfilename()
    if '/' in current:
        current = current.replace('/', '\\')
    if current in pics.keys():
        flag = messagebox.askokcancel('图片已打开', '图片已经打开，是否重新打开该图片？（重新打开将会失去该图片当前的计数）')
        if not flag:
            return
    else:
        lst.insert(tk.END, current)
    counts[current] = {
        'pos': 0,
        'neg': 0,
        'total': 0,
        'rate': 0.0
    }
    pics[current] = cv_imread(current)
    cv2.namedWindow(zh_ch(current.split('\\')[-1]),cv2.WINDOW_AUTOSIZE)
    # set_count()

    cv2.setMouseCallback(zh_ch(current.split('\\')[-1]), count)

    cv2.imshow(zh_ch(current.split('\\')[-1]), pics[current])
    wx = 304
    wy = 32
    cv2.moveWindow(zh_ch(current.split('\\')[-1]), wx, wy)
    zoom = 1
    history[current] = []

    p = 0
    n = 0
    t = 0
    r = 0.0
    for pic in counts.keys():
        p += counts[pic]['pos']
        n += counts[pic]['neg']
        t += counts[pic]['total']
    if t != 0:
        r = p/t * 100
    pos.set(p)
    neg.set(n)
    total.set(t)
    rate.set('{:.2f}%'.format(r))

def sel_pic(*args):
    global current, zoom
    cv2.destroyAllWindows()
    current = lst.get(lst.curselection())
    zoom = 1
    cv2.namedWindow(zh_ch(current.split('\\')[-1]))
    wx = 304
    wy = 32
    cv2.moveWindow(zh_ch(current.split('\\')[-1]), wx, wy)
    cv2.imshow(zh_ch(current.split('\\')[-1]), pics[current])
    # set_count()

    cv2.setMouseCallback(zh_ch(current.split('\\')[-1]), count)

def new_count():
    cv2.destroyAllWindows()
    flag = messagebox.askokcancel('开始新的计数', '当前未保存的数据将丢失，是否继续？')
    if flag:
        lst.delete(0, tk.END)
        counts.clear()
        pics.clear()
        pos.set(0)
        neg.set(0)
        rate.set(0)
        open_pic()

def continue_count():
    open_pic()

def undo():
    try:
        if current == '':
            return
    except:
        return
    if cv2.getWindowProperty(zh_ch(current.split('\\')[-1]), cv2.WND_PROP_VISIBLE) < 1:
        return
    pics[current] = cv_imread(current)
    if history[current] != []:
        history[current].pop(-1)
    counts[current]['pos'] = 0
    counts[current]['neg'] = 0
    counts[current]['total'] = 0
    counts[current]['rate'] = 0.0
    for h in history[current]:
        if h[0] == 1:
            cv2.circle(pics[current], (h[1], h[2]), 4, black, -1)
            cv2.circle(pics[current], (h[1], h[2]), 3, yellow, -1)
            cv2.putText(pics[current], '+', (h[1] - 4, h[2] + 3), font, 0.3, black, 1)
            counts[current]['pos'] += 1
        if h[0] == 0:
            cv2.circle(pics[current], (h[1], h[2]), 4, black, -1)
            cv2.circle(pics[current], (h[1], h[2]), 3, indigo, -1)
            cv2.putText(pics[current], '-', (h[1] - 4, h[2] + 3), font, 0.3, black, 1)
            counts[current]['neg'] += 1
    counts[current]['total'] = counts[current]['pos'] + counts[current]['neg']
    if counts[current]['total'] != 0:
        counts[current]['rate'] = counts[current]['pos']/counts[current]['total']
    p = 0
    n = 0
    t = 0
    r = 0.0
    for pic in counts.keys():
        p += counts[pic]['pos']
        n += counts[pic]['neg']
        t += counts[pic]['total']
    if t != 0:
        r = p / t * 100
    pos.set(p)
    neg.set(n)
    total.set(t)
    rate.set('{:.2f}%'.format(r))

    dst = cv2.resize(pics[current], dsize=None, fx=zoom, fy=zoom, interpolation=cv2.INTER_LINEAR)
    cv2.imshow(zh_ch(current.split('\\')[-1]), dst)

def save():
    filename = filedialog.asksaveasfilename(defaultextension = '.csv', initialfile = '*.csv',filetypes = [('CSV文件','.csv'),('文本文档','.txt'),('所有文件','.*')])
    if filename == '':
        return
    try:
        file = open(filename, 'w')
    except:
        messagebox.showerror('错误', '文件已在其他程序中打开，请关闭后再次保存！')
    file.write('总阳性数,' + str(pos.get()) + '\n')
    file.write('总阴性数,' + str(neg.get()) + '\n')
    file.write('总细胞数,' + str(total.get()) + '\n')
    file.write('总阳性率,' + str(rate.get()) + '\n')
    file.write('文件名,阳性数,阴性数,总数,阳性率\n')
    for pic in pics.keys():
        file.write(pic.split('\\')[-1] + ',' + str(counts[pic]['pos'])+ ',' + str(counts[pic]['neg'])+ ',' + str(counts[pic]['total']) + ',' + str(counts[pic]['rate']) + '\n')
    file.close()
    messagebox.showinfo('保存完成','文件已保存在'+filename)



root = tk.Tk()
root.resizable(0, 0)
root.geometry("+32+32")
root.attributes('-topmost', 'true')
root.title("手动细胞计数")
root.iconbitmap('logo.ico')


k.add_hotkey('Ctrl+s', save)
# k.add_hotkey('space', set_move)
# k.add_hotkey('c', set_count)
k.add_hotkey('Ctrl+z', undo)

mb = tk.Menu(root)
mb.add_command(label = '说明', command = show_help)
root.config(menu = mb)

btn1 = tk.Button(root, text = '打开新的图片，并开始新的计数', width = 36, command = new_count)
btn1.grid(row = 0, column = 0, columnspan = 4)

btn2 = tk.Button(root, text = '打开新的图片，继续当前计数', width = 36, command = continue_count)
btn2.grid(row = 1, column = 0, columnspan = 4)

lb1 = tk.Label(root, text = '阳性数：')
lb1.grid(row = 2, column = 0)

pos = tk.IntVar(root)
pos.set(0)
lb2 = tk.Label(root, textvariable = str(pos))
lb2.grid(row = 2, column = 1)

lb3 = tk.Label(root, text = '阴性数：')
lb3.grid(row = 3, column = 0)

neg = tk.IntVar(root)
neg.set(0)
lb4 = tk.Label(root, textvariable = str(neg))
lb4.grid(row = 3, column = 1)

lb8 = tk.Label(root, text = '总数：')
lb8.grid(row = 4, column = 0)

total = tk.IntVar(root)
total.set(0)
lb9 = tk.Label(root, textvariable = str(total))
lb9.grid(row = 4, column = 1)

lb5 = tk.Label(root, text = '阳性率：')
lb5.grid(row = 5, column = 0)

rate = tk.StringVar(root)
rate.set('0.00%')
lb6 = tk.Label(root, textvariable = rate)
lb6.grid(row = 5, column = 1)

btn3 = tk.Button(root, text = '导出当前数据<Ctrl+S>', width = 36, command = save)
btn3.grid(row = 6, column = 0, columnspan = 4)

btn0 = tk.Button(root, text = '撤回\n<Ctrl+Z>', width = 8, command = undo)
btn0.grid(row = 2, column = 2, rowspan = 4, columnspan = 2)

lb7 = tk.Label(root, text = '↓已经打开的文件↓')
lb7.grid(row = 7, column = 0, columnspan = 3)

lst = tk.Listbox(root, width = 34, height = 16)
lst.grid(row = 8, column = 0, columnspan = 3)
lst.bind('<Double-1>', sel_pic)

scrX = tk.Scrollbar(root, orient = 'horizontal')
lst.configure(xscrollcommand = scrX.set)
scrX['command'] = lst.xview
scrX.grid(row = 9, column = 0, columnspan = 3, sticky = 'we')

scrY = tk.Scrollbar(root)
lst.configure(yscrollcommand = scrY.set)
scrY['command'] = lst.yview
scrY.grid(row = 8, column = 3, sticky = 'ns')

# img_move = tk.PhotoImage(file = 'img\\yidong.png')
# img_count = tk.PhotoImage(file = 'img\\bi.png')
#
# btn4 = tk.Button(root, image = img_move, command = set_move)
# btn4.grid(row = 10, column = 0, columnspan = 2)
# lb10 = tk.Label(root, text = '<space>')
# lb10.grid(row = 11, column = 0, columnspan = 2)
#
# btn5 = tk.Button(root, image = img_count, command = set_count)
# btn5.grid(row = 10, column = 1, columnspan = 2)
# lb11 = tk.Label(root, text = '<c>')
# lb11.grid(row = 11, column = 1, columnspan = 2)

root.mainloop()