import wx
from utils.AIUtils import model_chat

class ChatFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(ChatFrame, self).__init__(*args, **kw)

        self.InitUI()

    def InitUI(self):
        pnl = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.chat_history = wx.TextCtrl(pnl, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.user_input = wx.TextCtrl(pnl, style=wx.TE_PROCESS_ENTER)
        self.user_input.Bind(wx.EVT_TEXT_ENTER, self.OnSend)

        vbox.Add(self.chat_history, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        vbox.Add(self.user_input, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)

        pnl.SetSizer(vbox)

        self.SetTitle('Chat Interface')
        self.Centre()
        self.Show(True)

    def OnSend(self, e):
        user_message = self.user_input.GetValue()
        if user_message:
            self.chat_history.AppendText(f'客官\n{user_message}\n')
            self.user_input.Clear()
            self.chat_history.AppendText(f'海瑞\n{user_message}\n')
            response = model_chat(user_message,"deepseek-r1:32b",self.chat_history)
            #self.chat_history.AppendText(f'Bot: {response}\n')

def main():
    app = wx.App()
    ex = ChatFrame(None)
    app.MainLoop()

if __name__ == '__main__':
    main()