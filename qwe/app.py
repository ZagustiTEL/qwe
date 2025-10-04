import tkinter as tk
from tkinter import messagebox

class Calculator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Калькулятор")
        self.window.geometry("300x400")
        self.window.resizable(False, False)
        
        # Переменные
        self.current_input = ""
        self.result_var = tk.StringVar()
        self.result_var.set("0")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Поле вывода
        display_frame = tk.Frame(self.window)
        display_frame.pack(pady=20)
        
        display = tk.Entry(
            display_frame, 
            textvariable=self.result_var, 
            font=('Arial', 18), 
            justify='right', 
            state='readonly',
            width=15
        )
        display.pack(padx=10, pady=10)
        
        # Кнопки
        buttons_frame = tk.Frame(self.window)
        buttons_frame.pack()
        
        # Расположение кнопок
        buttons = [
            ['C', '±', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '', '.', '=']
        ]
        
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                if text:  # Пропускаем пустые кнопки
                    btn = tk.Button(
                        buttons_frame,
                        text=text,
                        font=('Arial', 14),
                        width=5,
                        height=2,
                        command=lambda t=text: self.button_click(t)
                    )
                    btn.grid(row=i, column=j, padx=2, pady=2)
        
        # Делаем кнопку 0 широкой
        zero_btn = tk.Button(
            buttons_frame,
            text='0',
            font=('Arial', 14),
            width=11,
            height=2,
            command=lambda: self.button_click('0')
        )
        zero_btn.grid(row=4, column=0, columnspan=2, padx=2, pady=2)
    
    def button_click(self, value):
        if value == 'C':
            self.clear()
        elif value == '=':
            self.calculate()
        elif value == '±':
            self.plus_minus()
        elif value == '%':
            self.percentage()
        else:
            self.add_to_input(value)
    
    def add_to_input(self, value):
        if self.current_input == "0" or self.current_input == "Ошибка":
            self.current_input = ""
        
        self.current_input += str(value)
        self.result_var.set(self.current_input)
    
    def clear(self):
        self.current_input = ""
        self.result_var.set("0")
    
    def plus_minus(self):
        if self.current_input and self.current_input != "0":
            if self.current_input[0] == '-':
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
            self.result_var.set(self.current_input)
    
    def percentage(self):
        try:
            value = float(self.current_input)
            result = value / 100
            self.current_input = str(result)
            self.result_var.set(self.current_input)
        except:
            self.result_var.set("Ошибка")
            self.current_input = ""
    
    def calculate(self):
        try:
            # Заменяем символы для корректного вычисления
            expression = self.current_input.replace('×', '*').replace('÷', '/')
            result = eval(expression)
            self.current_input = str(result)
            self.result_var.set(self.current_input)
        except ZeroDivisionError:
            self.result_var.set("Ошибка: деление на 0")
            self.current_input = ""
        except:
            self.result_var.set("Ошибка")
            self.current_input = ""
    
    def run(self):
        self.window.mainloop()

# Запуск калькулятора
if __name__ == "__main__":
    calc = Calculator()
    calc.run()