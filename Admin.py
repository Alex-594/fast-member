"""
Модуль админской панели (режим организатора)

Функционал:
- Создание контрольных пунктов (КП)
- Привязка QR-кодов к КП
- Просмотр/редактирование списка КП
- Экспорт данных (файл JSON и QR-код)
- Получение координат (GPS или ручной ввод)
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.storage.jsonstore import JsonStore
from kivy.metrics import dp
from kivy.app import App
from kivy.core.window import Window
import os
import re
from datetime import datetime

# PIN-код для доступа к админ-панели
ADMIN_PIN = "1"


def request_admin_access(callback_success, callback_failure=None):
    """
    Запрос PIN-кода для доступа к админ-панели
    
    Args:
        callback_success: Функция, вызываемая при успешном вводе PIN
        callback_failure: Функция, вызываемая при неверном PIN (опционально)
    """
    # Создаем содержимое диалога
    content = BoxLayout(
        orientation='vertical',
        spacing=dp(15),
        padding=dp(20),
        size_hint_y=None
    )
    
    # Метка с инструкцией
    label = Label(
        text='Введите PIN-код для доступа к админ-панели',
        size_hint_y=None,
        height=dp(40),
        text_size=(None, None),
        halign='center'
    )
    content.add_widget(label)
    
    # Поле ввода PIN
    pin_input = TextInput(
        password=True,  # Скрывать ввод
        multiline=False,
        size_hint_y=None,
        height=dp(50),
        font_size=dp(20),
        halign='center'
    )
    content.add_widget(pin_input)
    
    # Метка для сообщения об ошибке
    error_label = Label(
        text='',
        size_hint_y=None,
        height=dp(30),
        color=(1, 0, 0, 1),  # Красный цвет для ошибки
        text_size=(None, None),
        halign='center'
    )
    content.add_widget(error_label)
    
    # Кнопки
    buttons_layout = BoxLayout(
        orientation='horizontal',
        spacing=dp(10),
        size_hint_y=None,
        height=dp(50)
    )
    
    popup = None
    
    def check_pin(instance):
        """Проверка введенного PIN-кода"""
        entered_pin = pin_input.text.strip()
        
        if entered_pin == ADMIN_PIN:
            popup.dismiss()
            callback_success()
        else:
            error_label.text = 'Неверный PIN-код'
            pin_input.text = ''
            if callback_failure:
                callback_failure()
    
    def cancel(instance):
        """Отмена ввода"""
        popup.dismiss()
    
    # Кнопка "Войти"
    enter_btn = Button(
        text='Войти',
        size_hint_x=0.5,
        background_normal='',
        background_color=(0.2, 0.4, 0.8, 1),
        color=(1, 1, 1, 1)
    )
    enter_btn.bind(on_press=check_pin)
    buttons_layout.add_widget(enter_btn)
    
    # Кнопка "Отмена"
    cancel_btn = Button(
        text='Отмена',
        size_hint_x=0.5,
        background_normal='',
        background_color=(0.7, 0.7, 0.7, 1),
        color=(0.2, 0.2, 0.2, 1)
    )
    cancel_btn.bind(on_press=cancel)
    buttons_layout.add_widget(cancel_btn)
    
    content.add_widget(buttons_layout)
    content.height = dp(200)
    
    # Создаем Popup
    popup = Popup(
        title='Доступ к админ-панели',
        content=content,
        size_hint=(0.7, None),
        height=content.height + dp(80),
        auto_dismiss=False
    )
    
    # Фокус на поле ввода при открытии
    def on_open(instance):
        pin_input.focus = True
    
    popup.bind(on_open=on_open)
    
    # Обработка нажатия Enter в поле ввода
    def on_enter(instance):
        check_pin(None)
    
    pin_input.bind(on_text_validate=on_enter)
    
    popup.open()
    
    return popup


class AdminScreen(Screen):
    """Экран админ-панели"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'admin'
        self._build_ui()
    
    def _build_ui(self):
        """Построение интерфейса админ-панели"""
        main_layout = BoxLayout(orientation='vertical', spacing=0)
        
        # Оранжевый заголовок "Админ режим"
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=[dp(20), dp(10)],
            spacing=dp(10)
        )
        
        header_label = Label(
            text='ОРГ',
            font_size=dp(24),
            color=(1, 1, 1, 1),
            size_hint_x=1,
            halign='center'
        )
        header_label.bind(text_size=header_label.setter('text_size'))
        
        # Оранжевый фон заголовка
        from kivy.graphics import Color, Rectangle
        with header.canvas.before:
            Color(1.0, 0.5, 0.0, 1)  # Оранжевый цвет
            self.header_rect = Rectangle(size=header.size, pos=header.pos)
        
        header.bind(size=self._update_header_rect, pos=self._update_header_rect)
        
        # Кнопка "Назад" в заголовке
        back_btn = Button(
            text='←',
            size_hint_x=None,
            width=dp(50),
            background_normal='',
            background_color=(0.8, 0.4, 0.0, 1),
            color=(1, 1, 1, 1),
            font_size=dp(28)
        )
        back_btn.bind(on_press=self._on_back)
        
        header.add_widget(back_btn)
        header.add_widget(header_label)
        main_layout.add_widget(header)
        
        # Основной контент в FloatLayout для размещения кнопки поверх
        content_wrapper = FloatLayout()
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Проверяем наличие соревнования
        self.store = JsonStore('app_data.json')
        
        if not self.store.exists('race'):
            # Нет соревнования - показываем форму создания
            self._build_create_race_form(content)
        else:
            # Есть соревнование - показываем информацию о нем
            self._build_race_info(content)
            # Добавляем кнопку добавления КП
            self._build_add_cp_button(content_wrapper)
        
        content_wrapper.add_widget(content)
        main_layout.add_widget(content_wrapper)
        self.add_widget(main_layout)
    
    def _update_header_rect(self, instance, value):
        """Обновление позиции и размера фона заголовка"""
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
    
    def _build_create_race_form(self, parent):
        """Создание формы для создания соревнования"""
        form_label = Label(
            text='Создайте новое соревнование',
            font_size=dp(20),
            size_hint_y=None,
            height=dp(50)
        )
        parent.add_widget(form_label)
        
        # Поле для названия соревнования
        name_label = Label(
            text='Название соревнования:',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        name_label.bind(text_size=name_label.setter('text_size'))
        parent.add_widget(name_label)
        
        self.name_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            hint_text='Введите название соревнования'
        )
        parent.add_widget(self.name_input)
        
        # Поле для даты соревнования
        date_label = Label(
            text='Дата соревнования (ДД-ММ-ГГГГ):',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        date_label.bind(text_size=date_label.setter('text_size'))
        parent.add_widget(date_label)
        
        self.date_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            hint_text='ДД-ММ-ГГГГ'
        )
        parent.add_widget(self.date_input)
        
        # Кнопка создания
        create_btn = Button(
            text='Создать соревнование',
            size_hint_y=None,
            height=dp(60),
            background_normal='',
            background_color=(0.2, 0.4, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=dp(18)
        )
        create_btn.bind(on_press=self._on_create_race)
        parent.add_widget(create_btn)
        
        # Пустое пространство
        parent.add_widget(Label(size_hint_y=1))
    
    def _build_race_info(self, parent):
        """Отображение информации о существующем соревновании"""
        race_data = self.store.get('race')
        
        # Оранжевая плашка с информацией о соревновании
        info_header = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=[dp(20), dp(15)],
            spacing=dp(10)
        )
        
        # Оранжевый фон плашки
        from kivy.graphics import Color, Rectangle
        with info_header.canvas.before:
            Color(1.0, 0.5, 0.0, 1)  # Оранжевый цвет
            self.info_rect = Rectangle(size=info_header.size, pos=info_header.pos)
        
        info_header.bind(size=self._update_info_rect, pos=self._update_info_rect)
        
        # Название соревнования
        name_label = Label(
            text=race_data.get("name", "Неизвестно"),
            font_size=dp(22),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(40),
            halign='center',
            bold=True
        )
        name_label.bind(text_size=name_label.setter('text_size'))
        info_header.add_widget(name_label)
        
        # Дата соревнования
        date_label = Label(
            text=race_data.get("date", "Неизвестно"),
            font_size=dp(18),
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        date_label.bind(text_size=date_label.setter('text_size'))
        info_header.add_widget(date_label)
        
        parent.add_widget(info_header)
        
        # TODO: Добавить остальной функционал админ-панели
        parent.add_widget(Label(size_hint_y=1))
    
    def _update_info_rect(self, instance, value):
        """Обновление позиции и размера фона плашки с информацией"""
        self.info_rect.pos = instance.pos
        self.info_rect.size = instance.size
    
    def _on_create_race(self, instance):
        """Обработчик создания соревнования"""
        name = self.name_input.text.strip()
        date = self.date_input.text.strip()
        
        if not name:
            self._show_error('Введите название соревнования')
            return
        
        if not date:
            self._show_error('Введите дату соревнования')
            return
        
        # Проверка формата даты (простая проверка)
        try:
            datetime.strptime(date, '%d-%m-%Y')
        except ValueError:
            self._show_error('Неверный формат даты. Используйте ДД-ММ-ГГГГ')
            return
        
        # Сохраняем данные соревнования
        self.store.put('race', name=name, date=date, created_at=datetime.now().isoformat())
        
        # Обновляем интерфейс
        self.clear_widgets()
        self._build_ui()
    
    def _show_error(self, message):
        """Показ сообщения об ошибке"""
        popup = Popup(
            title='Ошибка',
            content=Label(text=message),
            size_hint=(0.7, 0.3),
            auto_dismiss=True
        )
        popup.open()
    
    def _build_add_cp_button(self, parent):
        """Создание круглой кнопки с плюсом для добавления КП"""
        button_size = dp(64)
        button_padding = dp(20)
        
        # Контейнер для кнопки
        button_container = FloatLayout(
            size_hint=(None, None),
            size=(button_size, button_size)
        )
        
        # Круглая форма через canvas
        from kivy.graphics import Color, Ellipse
        with button_container.canvas.before:
            Color(0.2, 0.4, 0.8, 1)  # Синий цвет
            self.add_button_circle = Ellipse(size=(button_size, button_size), pos=(0, 0))
        
        # Кнопка
        add_button = Button(
            text='+',
            size_hint=(1, 1),
            pos=(0, 0),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(1, 1, 1, 1),
            font_size=dp(36),
            border=(0, 0, 0, 0)
        )
        add_button.bind(on_press=self._show_add_cp_dialog)
        
        button_container.add_widget(add_button)
        
        # Устанавливаем позицию в правом нижнем углу
        def update_button_position(instance, size):
            x = size[0] - button_size - button_padding
            y = button_padding
            button_container.pos = (x, y)
            if hasattr(self, 'add_button_circle'):
                self.add_button_circle.pos = (x, y)
        
        Window.bind(size=update_button_position)
        update_button_position(None, Window.size)
        
        parent.add_widget(button_container)
    
    def _show_add_cp_dialog(self, instance):
        """Показ диалога добавления КП"""
        # Создаем содержимое диалога
        dialog_content = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None
        )
        
        # Название КП
        name_label = Label(
            text='Название КП:',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        name_label.bind(text_size=name_label.setter('text_size'))
        dialog_content.add_widget(name_label)
        
        name_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        name_prefix = Label(text='КП ', size_hint_x=None, width=dp(40))
        cp_number_input = TextInput(
            multiline=False,
            hint_text='номер',
            size_hint_x=1
        )
        name_layout.add_widget(name_prefix)
        name_layout.add_widget(cp_number_input)
        dialog_content.add_widget(name_layout)
        
        # Код
        code_label = Label(
            text='Код:',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        code_label.bind(text_size=code_label.setter('text_size'))
        dialog_content.add_widget(code_label)
        
        code_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        code_input = TextInput(
            multiline=False,
            hint_text='Введите код или отсканируйте',
            size_hint_x=1
        )
        scan_btn = Button(
            text='📷',
            size_hint_x=None,
            width=dp(50),
            background_normal='',
            background_color=(0.2, 0.4, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        code_layout.add_widget(code_input)
        code_layout.add_widget(scan_btn)
        dialog_content.add_widget(code_layout)
        
        # Координаты
        coords_label = Label(
            text='Координаты:',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        coords_label.bind(text_size=coords_label.setter('text_size'))
        dialog_content.add_widget(coords_label)
        
        coords_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        lat_input = TextInput(
            multiline=False,
            hint_text='Широта (xx,xxxxx°)',
            size_hint_x=0.4
        )
        lon_input = TextInput(
            multiline=False,
            hint_text='Долгота (yy,yyyyy°)',
            size_hint_x=0.4
        )
        gps_btn = Button(
            text='GPS',
            size_hint_x=None,
            width=dp(60),
            background_normal='',
            background_color=(0.2, 0.4, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        coords_layout.add_widget(lat_input)
        coords_layout.add_widget(lon_input)
        coords_layout.add_widget(gps_btn)
        dialog_content.add_widget(coords_layout)
        
        # Подсказка о формате координат
        coords_hint = Label(
            text='Формат: xx,xxxxx° yy,yyyyy° (можно точка или запятая)',
            size_hint_y=None,
            height=dp(25),
            font_size=dp(12),
            color=(0.5, 0.5, 0.5, 1),
            halign='left'
        )
        coords_hint.bind(text_size=coords_hint.setter('text_size'))
        dialog_content.add_widget(coords_hint)
        
        # Подсказка (большое текстовое поле)
        hint_label = Label(
            text='Подсказка:',
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        hint_label.bind(text_size=hint_label.setter('text_size'))
        dialog_content.add_widget(hint_label)
        
        hint_input = TextInput(
            multiline=True,
            hint_text='Введите подсказку для участника',
            size_hint_y=None,
            height=dp(100)
        )
        dialog_content.add_widget(hint_input)
        
        # Кнопки
        buttons_layout = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50)
        )
        
        popup = None
        
        def validate_coords(lat_str, lon_str):
            """Проверка формата координат"""
            # Заменяем запятую на точку для проверки
            lat_str = lat_str.replace(',', '.').replace('°', '').strip()
            lon_str = lon_str.replace(',', '.').replace('°', '').strip()
            
            try:
                lat = float(lat_str)
                lon = float(lon_str)
                # Проверяем диапазоны
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return True, lat, lon
                return False, None, None
            except ValueError:
                return False, None, None
        
        def get_gps_coords(instance):
            """Получение координат через GPS (заглушка)"""
            self._show_error('GPS будет реализован позже')
        
        def save_cp(instance):
            """Сохранение КП"""
            cp_number = cp_number_input.text.strip()
            code = code_input.text.strip()
            lat_str = lat_input.text.strip()
            lon_str = lon_input.text.strip()
            hint = hint_input.text.strip()
            
            if not cp_number:
                self._show_error('Введите номер КП')
                return
            
            if not code:
                self._show_error('Введите код КП')
                return
            
            if not lat_str or not lon_str:
                self._show_error('Введите координаты')
                return
            
            # Проверка координат
            valid, lat, lon = validate_coords(lat_str, lon_str)
            if not valid:
                self._show_error('Неверный формат координат. Используйте формат: xx,xxxxx° yy,yyyyy°')
                return
            
            # Сохраняем КП
            cp_name = f"КП {cp_number}"
            if not self.store.exists('checkpoints'):
                self.store.put('checkpoints', items=[])
            
            checkpoints = self.store.get('checkpoints').get('items', [])
            checkpoints.append({
                'name': cp_name,
                'code': code,
                'latitude': lat,
                'longitude': lon,
                'hint': hint
            })
            self.store.put('checkpoints', items=checkpoints)
            
            popup.dismiss()
            # Обновляем интерфейс
            self.clear_widgets()
            self._build_ui()
        
        def cancel(instance):
            popup.dismiss()
        
        save_btn = Button(
            text='Сохранить',
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.2, 0.4, 0.8, 1),
            color=(1, 1, 1, 1)
        )
        save_btn.bind(on_press=save_cp)
        buttons_layout.add_widget(save_btn)
        
        cancel_btn = Button(
            text='Отмена',
            size_hint_x=0.5,
            background_normal='',
            background_color=(0.7, 0.7, 0.7, 1),
            color=(0.2, 0.2, 0.2, 1)
        )
        cancel_btn.bind(on_press=cancel)
        buttons_layout.add_widget(cancel_btn)
        
        dialog_content.add_widget(buttons_layout)
        
        # Вычисляем высоту контента
        dialog_content.height = (
            dp(30) + dp(50) +  # Название
            dp(30) + dp(50) +  # Код
            dp(30) + dp(50) +  # Координаты
            dp(25) +  # Подсказка о формате
            dp(30) + dp(100) +  # Подсказка
            dp(50) +  # Кнопки
            dp(15) * 6 + dp(20) * 2  # Отступы
        )
        
        # Создаем Popup
        popup = Popup(
            title='Добавить контрольный пункт',
            content=dialog_content,
            size_hint=(0.9, None),
            height=dialog_content.height + dp(80),
            auto_dismiss=False
        )
        
        # Привязываем обработчики
        gps_btn.bind(on_press=get_gps_coords)
        scan_btn.bind(on_press=lambda x: self._show_error('Сканирование QR будет реализовано позже'))
        
        popup.open()
    
    def _on_back(self, instance):
        """Возврат на главный экран"""
        app = App.get_running_app()
        if hasattr(app, 'root'):
            app.root.current = 'main'
