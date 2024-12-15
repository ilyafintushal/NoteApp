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
