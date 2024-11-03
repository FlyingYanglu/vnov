import JianYingApi, uuid
import uiautomation as api32
import time
import pyperclip  # Allows interacting with the system clipboard
import pyautogui  # Allows simulating keyboard and mouse actions
from vnov.role import Role
from vnov.data.data import Novel
import os
import json
import time
import datetime
class TTS(Role):

    def __init__(self, model=None, **kwargs):
        super().__init__(model=model, **kwargs)
        self.role = "tts"


    def generate_tss(self, novel: Novel, start_scene=0, end_scene=None):
        
        
        # load the combined storyboard
        combined_path = os.path.join(novel.dir, "storyboard/storyboard_combined.json")
        with open(combined_path, "r", encoding="utf-8") as f:
            scenes = json.load(f)
            if end_scene is None:
                end_scene = len(scenes)
            assert start_scene <= end_scene
            scenes = scenes[start_scene:end_scene]
            scenes = [scene["原文起始点"] for scene in scenes]

        cur_index = start_scene
        # for i, scene in enumerate(scenes):
        i = 0
        while True:
            scene = scenes[i]
            if not scene:
                i+=1
                cur_index += 1
                continue
            # print(f"Generating TTS for scene {cur_index}, example: {scene[:min(50, len(scene))]}")
            #     # generate the audio
            # start_time = time.time()
            # time_stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H")
            # self.create_video_from_text(scene, f"{novel.bookname}_tts_{cur_index}")
            # print(f"Time taken for scene {cur_index}: {time.time() - start_time}")
            try:
                print(f"Generating TTS for scene {cur_index}, example: {scene[:min(50, len(scene))]}")
                # generate the audio
                start_time = time.time()
                time_stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H")
                self.create_video_from_text(scene, f"{novel.bookname}_tts_{cur_index}")
                print(f"Time taken for scene {cur_index}: {time.time() - start_time}")
            except Exception as e:
                print(f"Failed to generate TTS for scene {cur_index}: {e}")
                continue
            i += 1
            cur_index += 1





    def create_video_from_text(self, text_content, export_title, jianying_exe_path=r"D:/jianying/JianyingPro"):
        # Step 1: 打开剪映识别
        print("Opening JianYing")
        time.sleep(2)
        ins = JianYingApi.Jy_Warp.Instance(JianYing_Exe_Path=jianying_exe_path)

        time.sleep(5)
        print("Searching JianYing Main Window")
        jy_main = api32.WindowControl(Name="剪映专业版", searchDepth=1)
        print("Found JianYing Main Window")
        print(jy_main)

        time.sleep(4)

        # Step 2: 点击图文成片按钮
        tuwen_button = jy_main.GetChildren()[11]
        x, y = tuwen_button.BoundingRectangle.xcenter(), tuwen_button.BoundingRectangle.ycenter()
        api32.Click(x, y)

        time.sleep(2)
        tuwen = api32.WindowControl(Name="图文成片", searchDepth=1)

        # Step 3: 查找并点击图文窗口中的子元素
        for i, c in enumerate(tuwen.GetChildren()):
            if i == 3:
                print(c, c.Name, c.ControlTypeName)
                x, y = c.BoundingRectangle.xcenter(), c.BoundingRectangle.ycenter()
                api32.Click(x, y)
                break

        # Step 4: 将文本内容复制到剪贴板
        pyperclip.copy(text_content)  # This copies the text to the clipboard

        edit = tuwen.GetChildren()[4]

        # Step 5: 粘贴文本内容
        edit.Click()  # Focus the edit control
        time.sleep(0.5)  # Ensure focus is set
        pyautogui.hotkey('ctrl', 'v')  # Simulates Ctrl + V to paste the clipboard content

        time.sleep(0.5)

        # Step 6: 点击生成按钮
        generate = tuwen.GetChildren()[8]
        button_loc = generate.BoundingRectangle
        button_loc.left += 350
        x, y = button_loc.xcenter(), button_loc.ycenter()
        api32.Click(x, y)

        time.sleep(0.5)

        button_loc.top -= 330
        x, y = button_loc.xcenter(), button_loc.ycenter()
        api32.Click(x, y)

        # print all windows
        # for i, c in enumerate(api32.GetRootControl().GetChildren()):
        #     print("before generation", i, c, c.Name, c.ControlTypeName)


        time.sleep(8)
        # Step 7: 等待生成完毕
        while True:
            print("Checking if video is generated")
            if not api32.WindowControl(Name="图文成片", searchDepth=1).Exists(maxSearchSeconds=1):
                print("Finished generating video")
                break
            time.sleep(1)
        #class name MainWindow_QMLTYPE_327

        # for i, c in enumerate(api32.GetRootControl().GetChildren()):
        #     print("after generation", i, c, c.Name, c.ControlTypeName)
        time.sleep(0.5)
        jy_main = api32.WindowControl(Name="剪映专业版", searchDepth=1)

        # Step 8: Check if already in full-screen mode and switch if necessary
        if not self.is_full_screen(jy_main):
            print("Not in full-screen mode, switching to full screen")
            full_screen = jy_main.GetChildren()[3]
            x, y = full_screen.BoundingRectangle.xcenter(), full_screen.BoundingRectangle.ycenter()
            api32.Click(x, y)
        else:
            print("Already in full-screen mode")

        # Step 9: 删除资源
        for i in range(10):
            source_rec = jy_main.GetChildren()[14].BoundingRectangle
            source_rec.left += 400 * i
            source_rec.top += 1010
            x, y = source_rec.xcenter(), source_rec.ycenter()
            api32.Click(x, y)
            api32.SendKeys("{DELETE}")

        # Step 10: 点击导出按钮
        daochu_button = jy_main.GetChildren()[5]
        x, y = daochu_button.BoundingRectangle.xcenter(), daochu_button.BoundingRectangle.ycenter()
        api32.Click(x, y)

        time.sleep(1)

        # Step 11: 填写导出文件名
        daochu = jy_main.WindowControl(Name="导出", searchDepth=1)
        export_name = daochu.GetChildren()[0]
        export_name_rect = export_name.BoundingRectangle
        x, y = export_name_rect.xcenter(), export_name_rect.ycenter()
        api32.Click(x, y)

        # 删除默认文本
        for i in range(13):
            # api32.SendKeys("{BACKSPACE}")
            pyautogui.press('backspace')

        # 粘贴新的导出文件名
        pyperclip.copy(export_title)
        pyautogui.hotkey('ctrl', 'v')

        # Step 12: 点击导出按钮
        time.sleep(0.5)
        button = daochu.GetChildren()[-2]
        x, y = button.BoundingRectangle.xcenter(), button.BoundingRectangle.ycenter()
        api32.Click(x, y)

        print(f"Finished converting text to video, saved as {export_title}")

    def is_full_screen(self, window):
        # Get screen resolution
        screen_width, screen_height = pyautogui.size()
        screen_height-= 80

        # Get window dimensions
        window_rect = window.BoundingRectangle
        window_width = window_rect.width()
        window_height = window_rect.height()

        # Tolerance for comparison
        tolerance = 30

        print(f"Screen width: {screen_width}, Screen height: {screen_height}")
        print(f"Window width: {window_width}, Window height: {window_height}")

        # Return True if window size is close to screen size
        return (
            abs(window_width - screen_width) <= tolerance and
            abs(window_height - screen_height) <= tolerance
        )
