import time
import zcanpro
import subprocess
from datetime import datetime

stopTask = False

def z_notify(type, obj):
    zcanpro.write_log("Notify " + str(type) + " " + str(obj))
    if type == "stop":
        zcanpro.write_log("Stop...")
        global stopTask
        stopTask = True

def z_main():
    buses = zcanpro.get_buses()
    zcanpro.write_log("Get buses: " + str(buses))

    if len(buses) > 0:
        zcanpro.write_log("Available buses: " + str(buses))
        bus_id = buses[0]["busID"]  # 使用第一個可用的 busID
        test_dev_auto_send(bus_id)
    else:
        zcanpro.write_log("No available buses!")

# 控制設備自動發送的範例
def test_dev_auto_send(busID):
    frms = [
        {
            "can_id": 0x1AB,
            "is_canfd": 1,
            "canfd_brs": 1,
            "data": [0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x00, 0x00],
            "interval_ms": 500
        }
    ]

    result = zcanpro.dev_auto_send_start(busID, frms)
    if result == 0:
        zcanpro.write_log("Start device auto send failed!")
        return
    else:
        zcanpro.write_log("Device auto send started...")

    # 在停止之前執行截圖動作
    capture_and_pull_screenshot()

    global stopTask
    stopTask = False
    while not stopTask:
        time.sleep(0.1)

    result = zcanpro.dev_auto_send_stop(busID)
    if result == 0:
        zcanpro.write_log("Stop device auto send failed!")
    else:
        zcanpro.write_log("Device auto send stopped.")

def capture_and_pull_screenshot():
    try:
        # 獲取當前時間，格式化為文件名
        datetime_str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        # ADB 指令列表 - 截取原始螢幕
        commands_original = [
            "adb root",  # 提升 adb 權限
            "adb shell mkdir -p /data/Picture",  # 確保目錄存在
            f"adb shell screencap -p /data/Picture/item1_original.png",  # 截取原始螢幕
            f"adb pull /data/Picture/item1_original.png .",  # 拉取到本地
        ]

        # 執行原始螢幕截圖指令
        for cmd in commands_original:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                zcanpro.write_log(f"Error executing command: {cmd}")
                zcanpro.write_log(f"Error message: {result.stderr.strip()}")
                return
        zcanpro.write_log(f"Original screenshot saved as item1_original.png.")

        # 模擬下拉動作以顯示通知欄
        result_swipe_down = subprocess.run(
            "adb shell input swipe 500 0 500 1000",  # 模擬下拉通知欄的手勢
            shell=True, capture_output=True, text=True
        )
        if result_swipe_down.returncode != 0:
            zcanpro.write_log("Error executing swipe down gesture.")
            zcanpro.write_log(f"Error message: {result_swipe_down.stderr.strip()}")
            return

        # ADB 指令列表 - 截取下拉後的螢幕
        commands_notification = [
            f"adb shell screencap -p /data/Picture/item1_notification.png",  # 截取通知欄螢幕
            f"adb pull /data/Picture/item1_notification.png .",  # 拉取到本地
        ]

        # 執行通知欄螢幕截圖指令
        for cmd in commands_notification:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                zcanpro.write_log(f"Error executing command: {cmd}")
                zcanpro.write_log(f"Error message: {result.stderr.strip()}")
                return
        zcanpro.write_log(f"Notification screenshot saved as item1_notification.png.")

        # 模擬上拉動作以隱藏通知欄 
        result_swipe_up = subprocess.run(
            "adb shell input swipe 500 1000 500 0",  # 模擬上拉通知欄的手勢
            shell=True, capture_output=True, text=True
        )
        if result_swipe_up.returncode != 0:
            zcanpro.write_log("Error executing swipe up gesture.")
            zcanpro.write_log(f"Error message: {result_swipe_up.stderr.strip()}")
            return
        zcanpro.write_log("Notification bar pulled back up.")

    except Exception as e:
        zcanpro.write_log(f"An error occurred: {str(e)}")