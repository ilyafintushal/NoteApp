import tkinter as tk

from tkinter import messagebox, simpledialog
import json
import os

class NoteApp:
    # Класс NoteApp реализует пользовательское приложение для создания, редактирования и управления заметками.
    def __init__(self, root):
        # Инициализация приложения: создание главного окна, загрузка заметок и настройка интерфейса.
        self.root = root
        self.root.title("NoteApp")
        self.notes = []  # Список всех заметок
        self.current_note_index = None  # Индекс текущей выбранной заметки
        self.notes_file = "notes.json"  # Файл для хранения заметок
        
        # Загрузка заметок из файла
        self.load_notes()

        # Настройка пользовательского интерфейса
        self.setup_ui()

    def setup_ui(self):
        # Настройка главного окна и его элементов
        self.left_frame = tk.Frame(self.root)  # Левая панель для списка заметок
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = tk.Frame(self.root)  # Правая панель для отображения содержимого заметок
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Список заметок
        self.notes_listbox = tk.Listbox(self.left_frame)
        self.notes_listbox.pack(fill=tk.BOTH, expand=True)
        self.notes_listbox.bind("<<ListboxSelect>>", self.display_note)  # Обработчик выбора заметки

        # Кнопки управления заметками
        self.add_button = tk.Button(self.left_frame, text="Add Note", command=self.add_note)
        self.add_button.pack(fill=tk.X)

        self.edit_button = tk.Button(self.left_frame, text="Edit Note", command=self.edit_note)
        self.edit_button.pack(fill=tk.X)

        self.remove_button = tk.Button(self.left_frame, text="Remove Note", command=self.remove_note)
        self.remove_button.pack(fill=tk.X)

        # Отображение содержимого заметки
        self.note_title_label = tk.Label(self.right_frame, text="Title:", font=("Arial", 14))
        self.note_title_label.pack(anchor=tk.W)

        self.note_content_text = tk.Text(self.right_frame, state=tk.DISABLED, wrap=tk.WORD)
        self.note_content_text.pack(expand=True, fill=tk.BOTH)

        # Меню приложения
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)  # Пункт меню для выхода из приложения
        self.menu.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(self.menu, tearoff=0)
        edit_menu.add_command(label="Add Note", command=self.add_note)  # Создание новой заметки
        edit_menu.add_command(label="Edit Note", command=self.edit_note)  # Редактирование текущей заметки
        edit_menu.add_command(label="Remove Note", command=self.remove_note)  # Удаление заметки
        self.menu.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(self.menu, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)  # О программе
        self.menu.add_cascade(label="Help", menu=help_menu)

        self.refresh_notes_list()  # Обновление списка заметок
        
    def add_note_dialog(self, note=None):
        # Окно для создания новой заметки или редактирования существующей
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Note" if note else "Add Note")

        tk.Label(dialog, text="Title:").pack()  # Поле ввода названия заметки
        title_entry = tk.Entry(dialog)
        title_entry.pack(fill=tk.X)
        
        tk.Label(dialog, text="Content:").pack()  # Поле ввода содержимого заметки
        content_text = tk.Text(dialog, height=10)
        content_text.pack(fill=tk.BOTH, expand=True)

        if note:
            # Если редактируется существующая заметка, предзаполняем поля данными
            title_entry.insert(0, note["title"])
            content_text.insert(1.0, note["content"])