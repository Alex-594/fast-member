"""
Главный файл запуска приложения FAST_member

Мобильное приложение для участников автомобильного ориентирования.
Поддерживает режимы: участник и организатор (админ-панель).
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp
import os
import Admin

# Версия приложения
APP_VERSION = "1.0.0"
APP_RELEASE_DATE = "2025-01-15"


class MainScreen(Screen):
    """Главный экран приложения"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        
        # Создаем FloatLayout для содержимого
        content_layout = FloatLayout()
        
        # Фон экрана
        Window.clearcolor = (0.95, 0.95, 0.95, 1)  # Светло-серый фон
        
        self._build_ui(content_layout)
        self.add_widget(content_layout)
    
    def _build_ui(self, parent):
        """Построение интерфейса главного экрана"""
        
        # Основной контент в BoxLayout
        main_content = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=[dp(30), dp(40), dp(30), dp(100)]  # Больше отступ снизу для кнопки
        )
        
        # Приветствие от клуба
        club_label = Label(
            text='Московский клуб автотуристов',
            font_size=dp(18),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_y=None,
            height=dp(40)
        )
        main_content.add_widget(club_label)
        
        # Название приложения
        app_name_label = Label(
            text='FAST',
            font_size=dp(48),
            color=(0.2, 0.4, 0.8, 1),  # Синий цвет
            size_hint_y=None,
            height=dp(80)
        )
        main_content.add_widget(app_name_label)
        
        # Версия и дата
        version_text = f'Версия {APP_VERSION}\nДата выпуска: {APP_RELEASE_DATE}'
        version_label = Label(
            text=version_text,
            font_size=dp(14),
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(50)
        )
        main_content.add_widget(version_label)
        
        # Пустое пространство для центрирования
        main_content.add_widget(Label(size_hint_y=1))
        
        # Инструкция для пользователя
        instruction_label = Label(
            text='Отсканируйте QR код на регистрации',
            font_size=dp(20),
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=None,
            height=dp(50)
        )
        main_content.add_widget(instruction_label)
        
        # Добавляем основной контент
        parent.add_widget(main_content)
        
        # Кнопка меню в правом верхнем углу
        self._build_menu_button(parent)
        
        # Круглая кнопка сканирования QR в правом нижнем углу
        button_size = dp(64)
        button_padding = dp(20)
        
        # Контейнер для кнопки (FloatLayout для правильного позиционирования)
        button_container = FloatLayout(
            size_hint=(None, None),
            size=(button_size, button_size),
            pos_hint={'right': 1, 'y': 0}
        )
        
        # Устанавливаем абсолютную позицию с учетом отступов
        def update_container_pos(instance, size):
            x = size[0] - button_size - button_padding
            y = button_padding
            button_container.pos = (x, y)
        
        Window.bind(size=update_container_pos)
        update_container_pos(None, Window.size)
        
        # Создаем круглую форму через canvas контейнера (позиция относительно контейнера)
        from kivy.graphics import Color, Ellipse
        with button_container.canvas.before:
            Color(0.2, 0.4, 0.8, 1)
            Ellipse(size=(button_size, button_size), pos=(0, 0))
        
        # Кнопка для обработки нажатий (прозрачная, на весь контейнер)
        qr_button = Button(
            size_hint=(1, 1),
            pos=(0, 0),
            background_normal='',
            background_color=(0, 0, 0, 0),  # Прозрачный
            border=(0, 0, 0, 0)
        )
        
        # Изображение QR-кода внутри контейнера
        qr_image_path = os.path.join('Png', 'QR.png')
        if os.path.exists(qr_image_path):
            image_size = button_size * 0.6
            image_offset = (button_size - image_size) / 2
            qr_image = Image(
                source=qr_image_path,
                size_hint=(None, None),
                size=(image_size, image_size),
                pos=(image_offset, image_offset)
            )
            button_container.add_widget(qr_image)
        else:
            # Если изображение не найдено, используем текст на кнопке
            qr_button.text = 'QR'
            qr_button.color = (1, 1, 1, 1)
            qr_button.font_size = dp(20)
        
        button_container.add_widget(qr_button)
        
        # Обработчик нажатия
        qr_button.bind(on_press=self._on_scan_qr)
        
        parent.add_widget(button_container)
    
    def _build_menu_button(self, parent):
        """Создание кнопки меню в правом верхнем углу"""
        menu_button_size = dp(48)
        menu_padding = dp(15)
        
        # Кнопка меню
        menu_button = Button(
            text='☰',  # Символ меню (три горизонтальные линии)
            size_hint=(None, None),
            size=(menu_button_size, menu_button_size),
            font_size=dp(24),
            background_normal='',
            background_color=(0.2, 0.4, 0.8, 1),
            color=(1, 1, 1, 1),
            border=(0, 0, 0, 0)
        )
        
        # Устанавливаем позицию кнопки меню
        def update_menu_position(instance, size):
            x = size[0] - menu_button_size - menu_padding
            y = size[1] - menu_button_size - menu_padding
            menu_button.pos = (x, y)
        
        Window.bind(size=update_menu_position)
        update_menu_position(None, Window.size)
        
        # Обработчик нажатия
        menu_button.bind(on_press=self._show_menu)
        
        parent.add_widget(menu_button)
    
    def _show_menu(self, instance):
        """Показ выпадающего меню"""
        # Создаем содержимое меню
        menu_content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        
        # Пункты меню
        menu_items = [
            ('Настройки', self._on_settings),
            ('Организатору', self._on_admin),
            ('Сдать результаты', self._on_submit_results),
            ('Удалить соревнование', self._on_delete_race)
        ]
        
        for item_text, item_handler in menu_items:
            btn = Button(
                text=item_text,
                size_hint_y=None,
                height=dp(50),
                background_normal='',
                background_color=(0.9, 0.9, 0.9, 1),
                color=(0.2, 0.2, 0.2, 1)
            )
            # Создаем замыкание для правильной работы обработчика
            def make_handler(handler):
                return lambda x: (self._close_menu(), handler())
            btn.bind(on_press=make_handler(item_handler))
            menu_content.add_widget(btn)
        
        menu_content.height = len(menu_items) * dp(50) + (len(menu_items) - 1) * dp(10) + dp(20)
        
        # Создаем Popup
        self.menu_popup = Popup(
            title='Меню',
            content=menu_content,
            size_hint=(0.6, None),
            height=menu_content.height + dp(80),
            auto_dismiss=True
        )
        
        self.menu_popup.open()
    
    def _close_menu(self):
        """Закрытие меню"""
        if hasattr(self, 'menu_popup'):
            self.menu_popup.dismiss()
    
    def _on_settings(self):
        """Обработчик пункта меню 'Настройки'"""
        print("Открытие настроек...")
        # TODO: Реализовать экран настроек
    
    def _on_admin(self):
        """Обработчик пункта меню 'Организатору'"""
        # Запрос PIN-кода для доступа к админ-панели
        Admin.request_admin_access(
            callback_success=self._on_admin_access_granted,
            callback_failure=self._on_admin_access_denied
        )
    
    def _on_admin_access_granted(self):
        """Обработчик успешного ввода PIN-кода"""
        # Переход на экран админ-панели
        app = App.get_running_app()
        if hasattr(app, 'root'):
            app.root.current = 'admin'
    
    def _on_admin_access_denied(self):
        """Обработчик неверного PIN-кода"""
        print("Неверный PIN-код")
    
    def _on_submit_results(self):
        """Обработчик пункта меню 'Сдать результаты'"""
        print("Сдача результатов...")
        # TODO: Реализовать сдачу результатов
    
    def _on_delete_race(self):
        """Обработчик пункта меню 'Удалить соревнование'"""
        print("Удаление соревнования...")
        # TODO: Реализовать удаление соревнования с подтверждением
    
    def _on_scan_qr(self, instance):
        """Обработчик нажатия на кнопку сканирования QR-кода"""
        # TODO: Реализовать открытие камеры для сканирования QR
        print("Открытие камеры для сканирования QR-кода...")
        # Здесь будет вызов функции из QR_codes.py


class FastMemberApp(App):
    """Главный класс приложения"""
    
    def build(self):
        """Создание главного экрана"""
        # Создаем ScreenManager для переключения между экранами
        sm = ScreenManager()
        
        # Добавляем главный экран
        main_screen = MainScreen()
        sm.add_widget(main_screen)
        
        # Добавляем экран админ-панели
        admin_screen = Admin.AdminScreen()
        sm.add_widget(admin_screen)
        
        # Устанавливаем главный экран как текущий
        sm.current = 'main'
        
        return sm


# Главная функция запуска
if __name__ == "__main__":
    app = FastMemberApp()
    app.run()

