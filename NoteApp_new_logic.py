import tkinter as tk
from tkinter import messagebox, simpledialog
from enum import Enum
from datetime import datetime
import json
import os

class NoteCategory(Enum):
    """
    Перечисление для категорий заметок
    """
    WORK = "Работа"
    HOME = "Дом"
    HEALTH = "Здоровье и Спорт"
    PEOPLE = "Люди"
    DOCUMENTS = "Документы"
    FINANCE = "Финансы"
    MISC = "Разное"

class Note:
    """
    Класс заметки, содержащий название, категорию, текст, время создания и последнего изменения
    """
    def __init__(self, title="Без названия", category=NoteCategory.MISC, content=""):
        self.title = title[:50]  # Ограничение названия до 50 символов
        self.category = category
        self.content = content
        self.created_at = datetime.now()  # Время создания инициализируется при создании заметки
        self.updated_at = self.created_at  # Изначально совпадает с временем создания

    def update(self, title=None, category=None, content=None):
        """
        Обновление названия, категории и текста заметки. Обновляет время последнего изменения.
        """
        if title:
            self.title = title[:50]
        if category:
            self.category = category
        if content:
            self.content = content
        self.updated_at = datetime.now()  # Обновление времени изменения

    def to_dict(self):
        """
        Преобразование заметки в словарь для сериализации
        """
        return {
            "title": self.title,
            "category": self.category.value,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        """
        Создание заметки из словаря
        """
        note = cls(
            title=data["title"],
            category=NoteCategory(data["category"]),
            content=data["content"]
        )
        note.created_at = datetime.fromisoformat(data["created_at"])
        note.updated_at = datetime.fromisoformat(data["updated_at"])
        return note

class Project:
    """
    Класс проекта, содержащий список заметок
    """
    def __init__(self):
        self.notes = []

    def add_note(self, note):
        """Добавление заметки в проект"""
        self.notes.append(note)

    def remove_note_by_index(self, index):
        """Удаление заметки по индексу"""
        if 0 <= index < len(self.notes):
            del self.notes[index]

    def to_dict(self):
        """Преобразование проекта в словарь для сериализации"""
        return {"notes": [note.to_dict() for note in self.notes]}

    @classmethod
    def from_dict(cls, data):
        """Создание проекта из словаря"""
        project = cls()
        project.notes = [Note.from_dict(note_data) for note_data in data["notes"]]
        return project

class ProjectManager:
    """
    Класс для управления сохранением и загрузкой проекта
    """
    FILE_PATH = os.path.join(os.path.expanduser("~"), "Documents", "NoteApp.notes")

    @staticmethod
    def save_project(project):
        """Сохранение проекта в файл"""
        with open(ProjectManager.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(project.to_dict(), f, ensure_ascii=False, indent=4)

    @staticmethod
    def load_project():
        """Загрузка проекта из файла"""
        if os.path.exists(ProjectManager.FILE_PATH):
            with open(ProjectManager.FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Project.from_dict(data)
        return Project()

class NoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NoteApp")

        # Загрузка проекта
        self.project = ProjectManager.load_project()
        self.current_note_index = None

        # UI Setup
        self.setup_ui()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Список заметок
        self.notes_listbox = tk.Listbox(self.left_frame)
        self.notes_listbox.pack(fill=tk.BOTH, expand=True)
        self.notes_listbox.bind("<<ListboxSelect>>", self.display_note)

        # Кнопки
        self.add_button = tk.Button(self.left_frame, text="Add Note", command=self.add_note)
        self.add_button.pack(fill=tk.X)

        self.edit_button = tk.Button(self.left_frame, text="Edit Note", command=self.edit_note)
        self.edit_button.pack(fill=tk.X)

        self.remove_button = tk.Button(self.left_frame, text="Remove Note", command=self.remove_note)
        self.remove_button.pack(fill=tk.X)

        # Отображение заметки
        self.note_title_label = tk.Label(self.right_frame, text="Title:", font=("Arial", 14))
        self.note_title_label.pack(anchor=tk.W)

        self.note_content_text = tk.Text(self.right_frame, state=tk.DISABLED, wrap=tk.WORD)
        self.note_content_text.pack(expand=True, fill=tk.BOTH)

        # Меню
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(self.menu, tearoff=0)
        edit_menu.add_command(label="Add Note", command=self.add_note)
        edit_menu.add_command(label="Edit Note", command=self.edit_note)
        edit_menu.add_command(label="Remove Note", command=self.remove_note)
        self.menu.add_cascade(label="Edit", menu=edit_menu)

        help_menu = tk.Menu(self.menu, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.menu.add_cascade(label="Help", menu=help_menu)

        self.refresh_notes_list()

    def add_note_dialog(self, note=None):
        """Диалоговое окно для добавления или редактирования заметки"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Note" if note else "Add Note")

        tk.Label(dialog, text="Title:").pack()
        title_entry = tk.Entry(dialog)
        title_entry.pack(fill=tk.X)

        tk.Label(dialog, text="Category:").pack()
        category_var = tk.StringVar(value=NoteCategory.MISC.value)
        category_menu = tk.OptionMenu(dialog, category_var, *[cat.value for cat in NoteCategory])
        category_menu.pack(fill=tk.X)

        tk.Label(dialog, text="Content:").pack()
        content_text = tk.Text(dialog, height=10)
        content_text.pack(fill=tk.BOTH, expand=True)

        if note:
            title_entry.insert(0, note.title)
            category_var.set(note.category.value)
            content_text.insert(1.0, note.content)

        def save():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("Error", "Title cannot be empty!")
                return

            if len(title) > 50:
                messagebox.showerror("Error", "Title cannot exceed 50 characters!")
                return

            category = NoteCategory(category_var.get())
            content = content_text.get(1.0, tk.END).strip()

            if note:
                note.update(title=title, category=category, content=content)
            else:
                new_note = Note(title=title, category=category, content=content)
                self.project.add_note(new_note)

            ProjectManager.save_project(self.project)
            self.refresh_notes_list()
            dialog.destroy()

        tk.Button(dialog, text="OK", command=save).pack(side=tk.LEFT)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)

    def add_note(self):
        self.add_note_dialog()

    def edit_note(self):
        if self.current_note_index is None:
            messagebox.showwarning("Warning", "No note selected!")
            return
        self.add_note_dialog(self.project.notes[self.current_note_index])

    def remove_note(self):
        if self.current_note_index is None:
            messagebox.showwarning("Warning", "No note selected!")
            return

        note = self.project.notes[self.current_note_index]
        confirm = messagebox.askyesno("Confirm", f"Do you really want to remove this note: {note.title}?")
        if confirm:
            self.project.remove_note_by_index(self.current_note_index)
            self.current_note_index = None
            ProjectManager.save_project(self.project)
            self.refresh_notes_list()

    def display_note(self, event=None):
        selected = self.notes_listbox.curselection()
        if not selected:
            return

        index = selected[0]
        self.current_note_index = index
        note = self.project.notes[index]

        self.note_title_label.config(text=f"Title: {note.title}")
        self.note_content_text.config(state=tk.NORMAL)
        self.note_content_text.delete(1.0, tk.END)
        self.note_content_text.insert(1.0, note.content)
        self.note_content_text.config(state=tk.DISABLED)

    def refresh_notes_list(self):
        self.notes_listbox.delete(0, tk.END)
        for note in self.project.notes:
            self.notes_listbox.insert(tk.END, f"{note.title} ({note.category.value})")

    def show_about(self):
        messagebox.showinfo("About", "NoteApp\nVersion 1.0\nDeveloped with Python and Tkinter.")

if __name__ == "__main__":
    root = tk.Tk()
    app = NoteApp(root)
    root.mainloop()
