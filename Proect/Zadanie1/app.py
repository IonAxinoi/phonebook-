import tkinter as tk
from tkinter import messagebox
import tkinter.filedialog as filedialog
import sqlite3
import csv
import json

# Объявляем переменные как глобальные
global name_entry
global number_entry
global group_entry
global contact_list
global selected_contact_id
global search_entry

# Функция для создания таблицы контактов, если её не существует
def create_table():
    cursor.execute('''CREATE TABLE IF NOT EXISTS contacts
                    (id INTEGER PRIMARY KEY, name TEXT, number TEXT, group_name TEXT)''')
    connection.commit()

# Функция для добавления контакта в базу данных
def add_contact():
    name = name_entry.get()
    number = number_entry.get()
    group = group_entry.get()
    if name and number:
        cursor.execute("INSERT INTO contacts (name, number, group_name) VALUES (?, ?, ?)", (name, number, group))
        connection.commit()
        messagebox.showinfo("Успех", "Контакт добавлен успешно!")
        name_entry.delete(0, tk.END)
        number_entry.delete(0, tk.END)
        group_entry.delete(0, tk.END)
        show_contacts()
    else:
        messagebox.showerror("Ошибка", "Пожалуйста, введите имя и номер контакта.")

# Функция для отображения всех контактов
def show_contacts():
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    if contacts:
        contact_list.delete(0, tk.END)  # Очищаем список контактов перед обновлением
        for contact in contacts:
            contact_list.insert(tk.END, f"{contact[1]}: {contact[2]}, Группа: {contact[3]}")
    else:
        messagebox.showinfo("Информация", "Нет контактов.")

# Функция для удаления контакта
def delete_contact():
    selected_contact = contact_list.curselection()
    if selected_contact:
        selected_contact_id = selected_contact[0] + 1  # Прибавляем 1, т.к. ID контактов начинаются с 1, а список - с 0
        cursor.execute("DELETE FROM contacts WHERE id=?", (selected_contact_id,))
        connection.commit()
        messagebox.showinfo("Успех", "Контакт успешно удален.")
        show_contacts()
    else:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите контакт для удаления.")

# Функция для редактирования контакта
def edit_contact():
    global selected_contact_id
    selected_contact = contact_list.curselection()
    if selected_contact:
        selected_contact_id = selected_contact[0] + 1  # Прибавляем 1, т.к. ID контактов начинаются с 1, а список - с 0
        new_name = name_entry.get()
        new_number = number_entry.get()
        new_group = group_entry.get()
        cursor.execute("UPDATE contacts SET name=?, number=?, group_name=? WHERE id=?",
                       (new_name, new_number, new_group, selected_contact_id))
        connection.commit()
        messagebox.showinfo("Успех", "Контакт успешно отредактирован.")
        show_contacts()
    else:
        messagebox.showerror("Ошибка", "Пожалуйста, выберите контакт для редактирования.")

# Функция для поиска контакта по имени или номеру телефона
def search_contact():
    search_term = search_entry.get()
    if search_term:
        cursor.execute("SELECT * FROM contacts WHERE name LIKE ? OR number LIKE ?", ('%' + search_term + '%', '%' + search_term + '%'))
        search_result = cursor.fetchall()
        if search_result:
            contact_list.delete(0, tk.END)  # Очищаем список контактов перед обновлением
            for contact in search_result:
                contact_list.insert(tk.END, f"{contact[1]}: {contact[2]}, Группа: {contact[3]}")
        else:
            messagebox.showinfo("Информация", "Контакт не найден.")
    else:
        messagebox.showerror("Ошибка", "Пожалуйста, введите имя или номер телефона для поиска.")

# Функция для импорта контактов из файла CSV
def import_csv(file_name):
    try:
        with open(file_name, 'r', newline='') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                cursor.execute("INSERT INTO contacts (name, number, group_name) VALUES (?, ?, ?)", (row['Name'], row['Number'], row['Group']))
            connection.commit()
            messagebox.showinfo("Успех", "Контакты успешно импортированы из файла CSV.")
            show_contacts()
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Файл CSV не найден.")

# Функция для импорта контактов из файла JSON
def import_json(file_name):
    try:
        with open(file_name, 'r') as file:
            data = json.load(file)
            for contact in data:
                cursor.execute("INSERT INTO contacts (name, number, group_name) VALUES (?, ?, ?)", (contact['name'], contact['number'], contact['group']))
            connection.commit()
            messagebox.showinfo("Успех", "Контакты успешно импортированы из файла JSON.")
            show_contacts()
    except FileNotFoundError:
        messagebox.showerror("Ошибка", "Файл JSON не найден.")

# Функция для выбора файла и импорта контактов
def import_contacts():
    file_name = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("JSON files", "*.json")])
    if file_name:
        if file_name.endswith('.csv'):
            import_csv(file_name)
        elif file_name.endswith('.json'):
            import_json(file_name)
        else:
            messagebox.showerror("Ошибка", "Неподдерживаемый формат файла.")

# Основная функция программы
def main():
    global connection
    global cursor
    global name_entry
    global number_entry
    global group_entry
    global contact_list
    global search_entry

    connection = sqlite3.connect("phonebook.db")  # Подключаемся к базе данных
    cursor = connection.cursor()
    create_table()  # Создаем таблицу, если она еще не создана

    # Создание главного окна
    root = tk.Tk()
    root.title("Телефонный справочник")

    # Создание и размещение элементов управления
    tk.Label(root, text="Имя:").grid(row=0, column=0)
    name_entry = tk.Entry(root)
    name_entry.grid(row=0, column=1)

    tk.Label(root, text="Номер:").grid(row=1, column=0)
    number_entry = tk.Entry(root)
    number_entry.grid(row=1, column=1)

    tk.Label(root, text="Группа:").grid(row=2, column=0)
    group_entry = tk.Entry(root)
    group_entry.grid(row=2, column=1)

    add_button = tk.Button(root, text="Добавить контакт", command=add_contact)
    add_button.grid(row=3, column=0, columnspan=2, pady=10)

    edit_button = tk.Button(root, text="Редактировать контакт", command=edit_contact)
    edit_button.grid(row=4, column=0, columnspan=2, pady=10)

    delete_button = tk.Button(root, text="Удалить контакт", command=delete_contact)
    delete_button.grid(row=5, column=0, columnspan=2, pady=10)

    show_button = tk.Button(root, text="Показать все контакты", command=show_contacts)
    show_button.grid(row=6, column=0, columnspan=2, pady=10)

    contact_list = tk.Listbox(root)
    contact_list.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

    # Добавление элементов управления для поиска контактов
    tk.Label(root, text="Поиск по имени или номеру:").grid(row=8, column=0)
    search_entry = tk.Entry(root)
    search_entry.grid(row=8, column=1)
    search_button = tk.Button(root, text="Найти", command=search_contact)
    search_button.grid(row=8, column=2)

    # Добавление кнопки для импорта контактов
    import_button = tk.Button(root, text="Импортировать контакты", command=import_contacts)
    import_button.grid(row=9, column=0, columnspan=2, pady=10)

    # Запуск главного цикла обработки событий
    root.mainloop()

if __name__ == "__main__":
    main()
