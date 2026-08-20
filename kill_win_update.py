#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kill_win_update.py
Отключение автообновлений Windows.
Собирается в exe командой:
    pyinstaller --onefile --uac-admin kill_win_update.py
(--uac-admin сразу попросит права администратора при запуске exe)
"""

import ctypes
import subprocess
import sys


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run(cmd: str) -> None:
    """Выполнить команду, подавив вывод и ошибки (аналог >nul 2>&1)."""
    subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def disable_service(name: str) -> None:
    run(f'sc config {name} start= disabled')
    run(f'net stop {name}')


def reg_add(path: str, value: str, data: str, vtype: str = "REG_DWORD") -> None:
    run(f'reg add "{path}" /v "{value}" /t {vtype} /d {data} /f')


def disable_task(task: str) -> None:
    run(f'schtasks /Change /TN "{task}" /Disable')


def main() -> None:
    if not is_admin():
        print("[!] Ошибка: А запустить файл от имени админа не хочешь?")
        input("Нажми Enter для выхода...")
        sys.exit(1)

    print("[1/5] остановка и отключение служб обновлений...(типо мы гаишники и майк тайсон)")
    for svc in ("wuauserv", "bits", "dosvc", "WaasMedicSvc"):
        disable_service(svc)

    print("[2/5] прописывание блокировок в реестр Windows...(типо мы гаишники)")
    au_key = r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
    reg_add(au_key, "NoAutoUpdate", "1")
    reg_add(au_key, "AUOptions", "2")
    reg_add(au_key, "ScheduledInstallDay", "0")
    reg_add(au_key, "ScheduledInstallTime", "3")
    reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate",
             "DisableWindowsUpdateAccess", "1")

    print("[3/5] запрет любимейщей автоперезагрузки при вошедшем пользователе на всякий")
    reg_add(au_key, "NoAutoRebootWithLoggedOnUsers", "1")

    print("[4/5] отключение задач в планировщике (типо мы майк тайсон)")
    tasks = [
        r"\Microsoft\Windows\WindowsUpdate\Scheduled Start",
        r"\Microsoft\Windows\UpdateOrchestrator\Report policies",
        r"\Microsoft\Windows\UpdateOrchestrator\Schedule Scan",
        r"\Microsoft\Windows\UpdateOrchestrator\Schedule Scan Static",
        r"\Microsoft\Windows\UpdateOrchestrator\UpdateModelTask",
        r"\Microsoft\Windows\UpdateOrchestrator\USO_UxBroker",
        r"\Microsoft\Windows\UpdateOrchestrator\Reboot",
        r"\Microsoft\Windows\UpdateOrchestrator\Reboot_AC",
    ]
    for t in tasks:
        disable_task(t)

    print("[5/5] блокировочка авто-восстановления служб через реестр...")
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Services\WaasMedicSvc", "Start", "4")
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Services\wuauserv", "Start", "4")

    print()
    print("===================================================")
    print("[УСПЕХ] Обновления и спонтанные перезагрузки уничтожены и унижены!")
    print("                              by 1nsideent4 =D")
    print('Нажми Win+I и зайди в "Центр обновления Windows" — там должно быть')
    print('"Ваша организация отключила автоматические обновления" =D')
    print("===================================================")
    input("Нажми Enter для выхода...")


if __name__ == "__main__":
    main()
