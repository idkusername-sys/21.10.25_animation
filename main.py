import tkinter as tk
from tkinter import ttk
import threading
import time
import pyautogui
import keyboard
import sys


class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("Автокликер с горячими клавишами")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        # Переменные для хранения настроек
        self.is_clicking = False
        self.click_thread = None
        self.click_speed = tk.DoubleVar(value=5.0)
        self.speed_unit = tk.StringVar(value="кликов/секунду")
        self.total_clicks = 0
        self.start_time = None
        self.click_type = tk.StringVar(value="left")

        self.create_widgets()
        self.setup_hotkeys()
        self.update_speed_info()

    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(self.root, text="🎯 Автокликер Pro",
                               font=("Arial", 16, "bold"), fg="#2E86AB")
        title_label.pack(pady=10)

        # Информация о горячих клавишах
        hotkey_frame = tk.Frame(self.root, bg="#E8F4FD", relief=tk.RAISED, bd=1)
        hotkey_frame.pack(pady=5, padx=20, fill="x")

        hotkey_label = tk.Label(hotkey_frame, text="🔥 Горячие клавиши: F6 - Вкл/Выкл | F7 - Экстренная остановка",
                                font=("Arial", 10, "bold"), bg="#E8F4FD", fg="#D35400")
        hotkey_label.pack(pady=8)

        # Фрейм для настроек скорости
        speed_frame = tk.LabelFrame(self.root, text="⚙️ Настройки скорости",
                                    font=("Arial", 10, "bold"), padx=15, pady=15)
        speed_frame.pack(pady=10, padx=20, fill="x")

        # Выбор единицы измерения скорости
        unit_frame = tk.Frame(speed_frame)
        unit_frame.pack(fill="x", pady=8)

        tk.Label(unit_frame, text="Единица измерения:",
                 font=("Arial", 9)).pack(side="left")

        speed_units = ["кликов/секунду", "кликов/минуту", "кликов/час", "интервал (мс)"]
        unit_combo = ttk.Combobox(unit_frame, textvariable=self.speed_unit,
                                  values=speed_units, state="readonly",
                                  width=18, font=("Arial", 9))
        unit_combo.pack(side="left", padx=10)
        unit_combo.bind('<<ComboboxSelected>>', self.on_unit_change)

        # Шкала скорости
        self.speed_label = tk.Label(speed_frame, text="Скорость: 5.0 кликов/секунду",
                                    font=("Arial", 10))
        self.speed_label.pack(pady=5)

        self.speed_scale = tk.Scale(speed_frame, from_=0.1, to=100.0, resolution=0.1,
                                    orient="horizontal", variable=self.click_speed,
                                    length=350, command=self.on_speed_change)
        self.speed_scale.pack(pady=5)

        # Информация о текущих настройках
        self.info_label = tk.Label(speed_frame, text="", font=("Arial", 9), fg="green")
        self.info_label.pack(pady=5)

        # Фрейм для типа клика
        click_frame = tk.LabelFrame(self.root, text="🖱️ Тип клика",
                                    font=("Arial", 10, "bold"), padx=15, pady=10)
        click_frame.pack(pady=10, padx=20, fill="x")

        tk.Radiobutton(click_frame, text="Левый клик", variable=self.click_type,
                       value="left", font=("Arial", 9)).pack(anchor="w")
        tk.Radiobutton(click_frame, text="Правый клик", variable=self.click_type,
                       value="right", font=("Arial", 9)).pack(anchor="w")
        tk.Radiobutton(click_frame, text="Двойной клик", variable=self.click_type,
                       value="double", font=("Arial", 9)).pack(anchor="w")
        tk.Radiobutton(click_frame, text="Средний клик", variable=self.click_type,
                       value="middle", font=("Arial", 9)).pack(anchor="w")

        # Фрейм для кнопок управления
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)

        # Кнопка старт
        self.start_button = tk.Button(button_frame, text="▶ СТАРТ (F6)",
                                      command=self.start_clicking,
                                      bg="#27AE60", fg="white",
                                      font=("Arial", 11, "bold"),
                                      width=12, height=2)
        self.start_button.grid(row=0, column=0, padx=8)

        # Кнопка стоп
        self.stop_button = tk.Button(button_frame, text="⏹ СТОП (F6)",
                                     command=self.stop_clicking,
                                     bg="#E74C3C", fg="white",
                                     font=("Arial", 11, "bold"),
                                     width=12, height=2,
                                     state="disabled")
        self.stop_button.grid(row=0, column=1, padx=8)

        # Кнопка сброса статистики
        reset_button = tk.Button(button_frame, text="🔄 Сброс",
                                 command=self.reset_stats,
                                 bg="#3498DB", fg="white",
                                 font=("Arial", 11, "bold"),
                                 width=12, height=2)
        reset_button.grid(row=0, column=2, padx=8)

        # Статус и статистика
        status_frame = tk.LabelFrame(self.root, text="📊 Статус",
                                     font=("Arial", 10, "bold"), padx=15, pady=10)
        status_frame.pack(pady=10, padx=20, fill="x")

        self.status_label = tk.Label(status_frame, text="Готов к работе",
                                     font=("Arial", 10, "bold"), fg="#27AE60")
        self.status_label.pack()

        self.stats_label = tk.Label(status_frame, text="Всего кликов: 0",
                                    font=("Arial", 9))
        self.stats_label.pack()

        self.time_label = tk.Label(status_frame, text="Время работы: 00:00:00",
                                   font=("Arial", 9))
        self.time_label.pack()

        # Информация о безопасности
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5, padx=20, fill="x")

        info_label = tk.Label(info_frame,
                              text="⚠ Безопасность:\n• F7 - экстренная остановка\n• Курсор в верхний левый угол - остановка\n• Не заблокируйте курсор!",
                              font=("Arial", 8), fg="red", justify="left")
        info_label.pack()

    def setup_hotkeys(self):
        """Настройка горячих клавиш"""
        try:
            # Регистрируем F6 для включения/выключения
            keyboard.add_hotkey('f6', self.toggle_clicking)
            # Регистрируем F7 для экстренной остановки
            keyboard.add_hotkey('f7', self.emergency_stop)
        except Exception as e:
            self.show_error(f"Ошибка настройки горячих клавиш: {e}")

    def toggle_clicking(self):
        """Переключение состояния кликера по F6"""
        if self.is_clicking:
            self.stop_clicking()
        else:
            self.start_clicking()

    def emergency_stop(self):
        """Экстренная остановка по F7"""
        if self.is_clicking:
            self.stop_clicking()
            self.update_status("⛔ ЭКСТРЕННАЯ ОСТАНОВКА!")

    def on_unit_change(self, event=None):
        """Обновляет шкалу при изменении единицы измерения"""
        unit = self.speed_unit.get()

        if unit == "интервал (мс)":
            self.speed_scale.config(from_=10, to=10000, resolution=10)
            self.click_speed.set(200)  # 200 мс по умолчанию
        elif unit == "кликов/час":
            self.speed_scale.config(from_=1, to=36000, resolution=1)
            self.click_speed.set(1800)  # 0.5 клика в секунду
        elif unit == "кликов/минуту":
            self.speed_scale.config(from_=1, to=600, resolution=1)
            self.click_speed.set(300)  # 5 кликов в секунду = 300 в минуту
        else:  # кликов/секунду
            self.speed_scale.config(from_=0.1, to=50.0, resolution=0.1)
            self.click_speed.set(5.0)

        self.on_speed_change()

    def on_speed_change(self, event=None):
        """Обновляет информацию при изменении скорости"""
        speed = self.click_speed.get()
        unit = self.speed_unit.get()

        if unit == "кликов/секунду":
            self.speed_label.config(text=f"Скорость: {speed:.1f} кликов/секунду")
        elif unit == "кликов/минуту":
            self.speed_label.config(text=f"Скорость: {speed:.0f} кликов/минуту")
        elif unit == "кликов/час":
            self.speed_label.config(text=f"Скорость: {speed:.0f} кликов/час")
        else:  # интервал (мс)
            self.speed_label.config(text=f"Интервал: {speed:.0f} мс")

        self.update_speed_info()

    def update_speed_info(self):
        """Обновляет дополнительную информацию о скорости"""
        speed = self.click_speed.get()
        unit = self.speed_unit.get()

        if unit == "кликов/секунду":
            interval_ms = 1000 / speed if speed > 0 else 1000
            info_text = f"Интервал: {interval_ms:.1f} мс между кликами"
        elif unit == "кликов/минуту":
            interval_ms = 60000 / speed if speed > 0 else 1000
            info_text = f"Интервал: {interval_ms:.1f} мс между кликами"
        elif unit == "кликов/час":
            interval_ms = 3600000 / speed if speed > 0 else 1000
            info_text = f"Интервал: {interval_ms:.1f} мс между кликами"
        else:  # интервал (мс)
            clicks_per_second = 1000 / speed if speed > 0 else 1
            info_text = f"Скорость: {clicks_per_second:.1f} кликов/секунду"

        self.info_label.config(text=info_text)

    def calculate_interval(self):
        """Рассчитывает интервал между кликами в секундах"""
        speed = self.click_speed.get()
        unit = self.speed_unit.get()

        if unit == "кликов/секунду":
            return 1.0 / speed if speed > 0 else 1.0
        elif unit == "кликов/минуту":
            return 60.0 / speed if speed > 0 else 1.0
        elif unit == "кликов/час":
            return 3600.0 / speed if speed > 0 else 1.0
        else:  # интервал (мс)
            return speed / 1000.0

    def click_loop(self):
        """Основной цикл кликов"""
        interval = self.calculate_interval()
        click_type = self.click_type.get()

        self.update_status("🎯 Кликаем... (F6 для остановки)")

        while self.is_clicking:
            try:
                # Получаем текущую позицию курсора
                x, y = pyautogui.position()

                # Совершаем клик в зависимости от выбранного типа
                if click_type == "left":
                    pyautogui.click(x, y)
                elif click_type == "right":
                    pyautogui.rightClick(x, y)
                elif click_type == "double":
                    pyautogui.doubleClick(x, y)
                elif click_type == "middle":
                    pyautogui.middleClick(x, y)

                self.total_clicks += 1
                self.update_stats()

                # Ждем указанный интервал
                time.sleep(interval)

            except pyautogui.FailSafeException:
                # Срабатывает когда курсор в верхнем левом углу
                self.stop_clicking()
                self.update_status("⛔ Остановка: курсор в углу экрана")
                break
            except Exception as e:
                self.stop_clicking()
                self.update_status(f"❌ Ошибка: {str(e)}")
                break

    def start_clicking(self):
        """Запуск автокликера"""
        if not self.is_clicking:
            self.is_clicking = True
            self.start_time = time.time()
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")

            # Запускаем клики в отдельном потоке
            self.click_thread = threading.Thread(target=self.click_loop)
            self.click_thread.daemon = True
            self.click_thread.start()

            # Запускаем обновление времени
            self.update_time()

    def stop_clicking(self):
        """Остановка автокликера"""
        self.is_clicking = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.update_status("⏹ Готов к работе")

    def reset_stats(self):
        """Сброс статистики"""
        self.total_clicks = 0
        self.update_stats()
        self.time_label.config(text="Время работы: 00:00:00")

    def update_status(self, message):
        """Обновляет статус"""
        self.status_label.config(text=message)

    def update_stats(self):
        """Обновляет статистику"""
        self.stats_label.config(text=f"Всего кликов: {self.total_clicks}")
        self.root.update_idletasks()

    def update_time(self):
        """Обновляет время работы"""
        if self.is_clicking and self.start_time:
            elapsed = time.time() - self.start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.time_label.config(text=f"Время работы: {hours:02d}:{minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_time)

    def show_error(self, message):
        """Показывает сообщение об ошибке"""
        error_label = tk.Label(self.root, text=message, fg="red", font=("Arial", 9))
        error_label.pack(pady=5)

    def on_closing(self):
        """Действия при закрытии окна"""
        self.is_clicking = False
        try:
            keyboard.unhook_all()
        except:
            pass
        self.root.destroy()


def main():
    try:
        # Проверяем доступность библиотек
        import pyautogui
        import keyboard

        pyautogui.FAILSAFE = True

        root = tk.Tk()
        app = AutoClicker(root)

        # Обработка закрытия окна
        root.protocol("WM_DELETE_WINDOW", app.on_closing)

        root.mainloop()

    except ImportError as e:
        print("❌ Ошибка: Не установлены необходимые библиотеки")
        print("Установите их командами:")
        print("pip install pyautogui")
        print("pip install keyboard")
        input("Нажмите Enter для выхода...")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()