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
        def save():
            # Сохранение новой заметки или изменений
            title = title_entry.get().strip()
            if not title:
                # Проверка на пустое название
                messagebox.showerror("Error", "Title cannot be empty!")
                return

            if len(title) > 50:
                # Проверка на превышение длины названия
                messagebox.showerror("Error", "Title cannot exceed 50 characters!")
                return

            content = content_text.get(1.0, tk.END).strip()  # Считывание содержимого заметки

            if note:
                # Обновление существующей заметки
                note["title"] = title
                note["content"] = content
                self.refresh_notes_list()
                self.display_note()
            else:
                # Создание новой заметки
                new_note = {"title": title, "content": content}
                self.notes.append(new_note)
                self.refresh_notes_list()

            self.save_notes()  # Сохранение заметок в файл
            dialog.destroy()  # Закрытие окна

        tk.Button(dialog, text="OK", command=save).pack(side=tk.LEFT)  # Кнопка подтверждения
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)  # Кнопка отмены

    def add_note(self):
        # Обработчик для добавления новой заметки
        self.add_note_dialog()

    def edit_note(self):
        # Обработчик для редактирования выбранной заметки
        if self.current_note_index is None:
            messagebox.showwarning("Warning", "No note selected!")
            return
        self.add_note_dialog(self.notes[self.current_note_index])

    def remove_note(self):
        # Обработчик для удаления выбранной заметки
        if self.current_note_index is None:
            messagebox.showwarning("Warning", "No note selected!")
            return

        note = self.notes[self.current_note_index]
        confirm = messagebox.askyesno("Confirm", f"Do you really want to remove this note: {note['title']}?")
        if confirm:
            del self.notes[self.current_note_index]  # Удаление заметки из списка
            self.current_note_index = None
            self.refresh_notes_list()  # Обновление списка заметок
            self.save_notes()  # Сохранение изменений

    def display_note(self, event=None):
        # Отображение содержимого выбранной заметки
        selected = self.notes_listbox.curselection()
        if not selected:
            return
        
        index = selected[0]
        self.current_note_index = index
        note = self.notes[index]

        self.note_title_label.config(text=f"Title: {note['title']}")  # Обновление заголовка
        self.note_content_text.config(state=tk.NORMAL)
        self.note_content_text.delete(1.0, tk.END)
        self.note_content_text.insert(1.0, note["content"])  # Обновление текста заметки
        self.note_content_text.config(state=tk.DISABLED)

    def refresh_notes_list(self):
        # Обновление списка заметок в левой панели
        self.notes_listbox.delete(0, tk.END)
        for note in self.notes:
            self.notes_listbox.insert(tk.END, note["title"])

    def save_notes(self):
        # Сохранение заметок в файл
        with open(self.notes_file, "w") as f:
            json.dump(self.notes, f)

    def load_notes(self):
        # Загрузка заметок из файла, если он существует
        if os.path.exists(self.notes_file):
            with open(self.notes_file, "r") as f:
                self.notes = json.load(f)

    def show_about(self):
        # Отображение окна "О программе"
        messagebox.showinfo("About", "NoteApp\nVersion 1.0\nDeveloped with Python and Tkinter.")

if __name__ == "__main__":
    # Точка входа в приложение
    root = tk.Tk()
    app = NoteApp(root)  # Создание экземпляра приложения
    root.mainloop()  # Запуск основного цикла приложения
