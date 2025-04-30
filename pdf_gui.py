import wx
from wx.lib.scrolledpanel import ScrolledPanel
import threading
from files.readPDFFiles import main  # Import the main function
import os  # Added for file operations
from datetime import date
import sys

# 获取当前文件所在目录的路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 将当前目录添加到 sys.path 中
sys.path.append(current_dir)

#app = create_app()
# Function to open the conclusion file
def open_conclusion_file(text_output):
    try:
        #以系统默认的方式打开结果.txt
        os.startfile("结果.txt")
        '''
        with open("结果.txt", "r", encoding='utf-8') as file:
            content = file.read()
            text_output.Clear()
            text_output.AppendText(content)
        '''
    except FileNotFoundError:
        wx.MessageBox("结果.txt 文件未找到.", "错误", wx.OK | wx.ICON_ERROR)
    except Exception as e:
        wx.MessageBox(f"读取文件时发生错误: {e}", "错误", wx.OK | wx.ICON_ERROR)

def start_processing(folder_path, text_output):
    if not folder_path:
        wx.MessageBox("请先选择一个文件夹.", "错误", wx.OK | wx.ICON_ERROR)
        return
    
    # Start processing in a separate thread to avoid freezing the GUI
    threading.Thread(target=process_data, args=(folder_path, text_output), daemon=True).start()

def process_data(folder_path, text_output):
    try:
        print("beging to process data")
        # Call the main function with mysqlUtil=None and selected folder path
        main(mysqlUtil=None, g_root_path=folder_path, output_text=text_output)
    except Exception as e:
        text_output.AppendText(f"转换过程中发生错误: {e}\n")

class MyApp(wx.App):
    def OnInit(self):
        frame = wx.Frame(None, title="公共资源交易中心-综合评审表校验", size=(600, 450))
        panel = ScrolledPanel(frame, -1)
        panel.SetupScrolling()

        # Folder selection
        wx.StaticText(panel, label="根目录:", pos=(10, 15))
        self.folder_var = wx.TextCtrl(panel, pos=(80, 10), size=(300, -1))
        wx.Button(panel, label="选择", pos=(400, 10)).Bind(wx.EVT_BUTTON, self.on_select_folder)

        # Start processing button
        wx.Button(panel, label="开始校验", pos=(10, 50)).Bind(wx.EVT_BUTTON, self.on_start_processing)

        # Output text box
        self.text_output = wx.TextCtrl(panel, pos=(10, 90), size=(560, 250), style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Add a clear button to clear the output text box
        wx.Button(panel, label="清理", pos=(10, 350)).Bind(wx.EVT_BUTTON, self.on_clear_output)

        # Add an open conclusion button to open the result.txt file
        wx.Button(panel, label="打开结论", pos=(100, 350)).Bind(wx.EVT_BUTTON, self.on_open_conclusion)

        frame.Show()
        return True

    def on_select_folder(self, event):
        dialog = wx.DirDialog(None, "选择文件夹", style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            self.folder_var.SetValue(dialog.GetPath())
        dialog.Destroy()

    def on_start_processing(self, event):
        folder_path = self.folder_var.GetValue()
        start_processing(folder_path, self.text_output)

    def on_clear_output(self, event):
        self.text_output.Clear()

    def on_open_conclusion(self, event):
        open_conclusion_file(self.text_output)

if __name__ == "__main__":
    app = MyApp(False)
    app.MainLoop()