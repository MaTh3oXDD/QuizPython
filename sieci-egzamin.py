import tkinter as tk
from tkinter import messagebox
import random
import os

# Define Colors
BG_COLOR = "#264653"
ACCENT_COLOR = "#2a9d8f"
TEXT_COLOR = "#e9ecef"  # A slightly darker white
BUTTON_COLOR = "#344e41"  # A darker tone of the BG_COLOR


def load_questions(filename):
    questions = []
    with open(filename, "r", encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]
        for line in lines:
            parts = line.split(';')
            if len(parts) >= 2:  # At least a question and one answer
                question = parts[0]
                answers = parts[1:]
                correct_indices = []
                clean_answers = []
                for i, ans in enumerate(answers):
                    if ans.startswith('1'):
                        correct_indices.append(i)
                        clean_answers.append(ans[1:].strip())
                    elif ans.startswith('0'):
                        clean_answers.append(ans[1:].strip())
                    else:
                        clean_answers.append(ans.strip())
                questions.append((line, question, clean_answers, correct_indices))
    return questions


def log_error_question(error_question):
    """Loguje pytanie do pliku z błędnymi pytaniami"""
    try:
        with open("problematyczne_pytania1.txt", "a", encoding='utf-8') as file:
            file.write(error_question + "\n")
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można zapisać pytania do pliku: {e}")


def load_next_question():
    global current_question_vars, checkboxes, correct_indices, question_answered, current_question_index, problem_question_var
    question_answered = False
    problem_question_var.set(0)  # Reset the "problematic question" checkbox

    # Clear previous selections and labels
    score_label.config(text="")
    correct_answers_label.config(text="", bg=BG_COLOR)

    # Destroy previous checkboxes
    for chk in checkboxes:
        chk.destroy()
    checkboxes.clear()
    current_question_vars.clear()

    # Check if we've used up all questions
    if current_question_index >= len(randomized_questions):
        messagebox.showinfo("Koniec", f"Koniec egzaminu. Twój wynik końcowy: {points:.2f}/{len(randomized_questions)}")
        root.destroy()
        return

    # Get the next question from randomized questions
    question_data = randomized_questions[current_question_index]

    # POPRAWKA: Użyj drugiego elementu z tupli (treść pytania)
    question_text = question_data[1]

    # POPRAWKA: Użyj trzeciego elementu z tupli (lista odpowiedzi)
    answers_list = question_data[2]

    # POPRAWKA: Użyj czwartego elementu z tupli (poprawne indeksy)
    correct_indices = question_data[3]

    # Update question counter
    question_counter_label.config(text=f"Pytanie {current_question_index + 1} z {len(randomized_questions)}")
    question_label.config(text=question_text)

    # Create new variables and checkboxes dynamically
    for idx, answer_text in enumerate(answers_list):
        var = tk.IntVar()
        chk = tk.Checkbutton(
            answer_frame,
            text=answer_text,
            variable=var,
            font=("Arial", 16),
            anchor="w",
            justify="left",
            padx=10,
            pady=5,
            bg=TEXT_COLOR,
            fg=BG_COLOR,
            selectcolor='light gray',
            borderwidth=1,
            relief="solid",
            activebackground="light gray",  # Set activebackground
            activeforeground=BG_COLOR,  # Set activeforeground
            wraplength=window_width - 80
        )
        chk.pack(fill='x', padx=20, pady=5)
        current_question_vars.append(var)
        checkboxes.append(chk)


def check_answer():
    global points, question_answered, current_question_index
    if question_answered:
        return
    question_answered = True

    # Clear checkbox backgrounds
    for chk in checkboxes:
        chk.config(bg=TEXT_COLOR, borderwidth=1)
    user_selection = [var.get() for var in current_question_vars]
    selected_indices = [i for i, val in enumerate(user_selection) if val == 1]

    # Highlight selections
    for idx, chk in enumerate(checkboxes):
        if idx in selected_indices and idx in correct_indices:
            chk.config(bg="#208026", borderwidth=2)
        elif idx in selected_indices and idx not in correct_indices:
            chk.config(bg="#FD5252", borderwidth=2)
        elif idx in correct_indices:
            chk.config(bg="#208026", borderwidth=2)

    # Calculate score
    question_score = calculate_score(selected_indices, correct_indices)
    points += question_score

    # Update score labels
    score_counter_label.config(text=f"Wynik całkowity: {points:.2f}/{len(randomized_questions)}")
    score_label.config(text=f"Punkty: {question_score:.2f}")

    # Display correct answers
    correct_answers_text = "Poprawne odpowiedzi:\n" + "\n".join(
        [checkboxes[idx]['text'] for idx in correct_indices]
    )
    correct_answers_label.config(text=correct_answers_text, bg="#FFEA3F", justify="center", anchor="center")

    # Enable next button after checking answer
    next_button.config(state=tk.NORMAL)


def calculate_score(selected, correct):
    total_correct = len(correct)
    total_wrong = len(selected) - len(set(selected) & set(correct))
    correct_selected = len(set(selected) & set(correct))
    incorrect_selected = total_wrong

    if correct_selected == 0 and incorrect_selected > 0:
        return -1.00

    if total_correct > 0:
        score = correct_selected / total_correct
    else:
        score = 0

    penalty = (2 / total_correct) * incorrect_selected if total_correct > 0 else 0
    final_score = score - penalty
    return max(min(final_score, 1.00), -1.00)


def next_question():
    global current_question_index, problem_question_var
    if problem_question_var.get() == 1:  # Check if the checkbox is checked
        log_error_question(randomized_questions[current_question_index][0])
    current_question_index += 1
    next_button.config(state=tk.DISABLED)  # Disable next button until answer is checked
    load_next_question()


def start_exam():
    global randomized_questions, current_question_index
    try:
        start_range = int(start_entry.get()) - 1  # Adjust to 0-based indexing
        end_range = int(end_entry.get())
        max_questions = len(questions)

        if 0 <= start_range < end_range <= max_questions:
            randomized_questions = questions[start_range:end_range].copy()  # Apply range
            random.shuffle(randomized_questions)
            current_question_index = 0
            load_next_question()
            range_window.destroy()  # Close range window
        else:
            messagebox.showerror("Błąd", f"Zakres pytań nieprawidłowy.  Wprowadź zakres od 1 do {max_questions}.")
    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawne liczby całkowite w zakresie pytań.")


def open_range_window():
    global start_entry, end_entry, range_window
    range_window = tk.Toplevel(root)
    range_window.title("Wybierz zakres pytań")
    range_window.geometry("1000x1000")  # Set window size
    range_window.config(bg=BG_COLOR)

    start_label = tk.Label(range_window, text="Od pytania:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 16))
    start_label.pack(pady=15)
    start_entry = tk.Entry(range_window, font=("Arial", 14))
    start_entry.pack(pady=10)

    end_label = tk.Label(range_window, text="Do pytania:", bg=BG_COLOR, fg=TEXT_COLOR, font=("Arial", 16))
    end_label.pack(pady=15)
    end_entry = tk.Entry(range_window, font=("Arial", 14))
    end_entry.pack(pady=10)

    start_button = tk.Button(
        range_window,
        text="Rozpocznij egzamin",
        command=start_exam,
        bg=BUTTON_COLOR,
        fg=TEXT_COLOR,
        font=("Arial", 16),
        padx=20,
        pady=10,
        relief="raised",
        bd=4,
        activebackground=ACCENT_COLOR,
        activeforeground=BG_COLOR,
    )
    start_button.pack(pady=30)


# Initialize Tkinter
root = tk.Tk()
root.title("Egzamin Sieci 2024")

# Set window size and position
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.45)
window_height = int(screen_height * 0.50)
position_right = int((screen_width - window_width) / 2)
position_down = int((screen_height - window_height) / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

# Configure root window background color
root.config(bg=BG_COLOR)

# Create main frame
main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill='both', expand=True, padx=10, pady=10)

# Question counter label
question_counter_label = tk.Label(
    main_frame,
    text="",
    font=("Arial", 16),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
question_counter_label.pack(pady=5)

# Question label
question_label = tk.Label(
    main_frame,
    text="",
    font=("Arial", 20),
    wraplength=window_width - 60,
    justify="center",
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
question_label.pack(pady=10)

# Answer frame
answer_frame = tk.Frame(main_frame, bg=BG_COLOR)
answer_frame.pack(pady=5)

# Initialize variables
points = 0.0
question_answered = False
current_question_vars = []
checkboxes = []
current_question_index = 0
problem_question_var = tk.IntVar()  # Variable for the checkbox

# Button frame
button_frame = tk.Frame(main_frame, bg=BG_COLOR)
button_frame.pack(pady=10)

check_button = tk.Button(
    button_frame,
    text="Sprawdź",
    command=check_answer,
    font=("Arial", 16),
    padx=20,
    pady=10,
    bg=BUTTON_COLOR,
    fg=TEXT_COLOR,
    relief="raised",
    bd=4,
    activebackground=ACCENT_COLOR,  # Set activebackground
    activeforeground=BG_COLOR  # Set activeforeground
)
check_button.pack(side='left', padx=10)

next_button = tk.Button(
    button_frame,
    text="Następne",
    command=next_question,
    font=("Arial", 16),
    padx=20,
    pady=10,
    bg=BUTTON_COLOR,
    fg=TEXT_COLOR,
    relief="raised",
    bd=4,
    state=tk.DISABLED,  # Initially disabled
    activebackground=ACCENT_COLOR,  # Set activebackground
    activeforeground=BG_COLOR  # Set activeforeground
)
next_button.pack(side='left', padx=10)

# Checkbox to mark question as problematic
problem_question_checkbox = tk.Checkbutton(
    button_frame,
    text="Pytanie problematyczne",
    variable=problem_question_var,
    bg=BG_COLOR,
    fg=TEXT_COLOR,
    font=("Arial", 12),
    activebackground=BG_COLOR,  # Set activebackground
    activeforeground=TEXT_COLOR  # Set activeforeground
)
problem_question_checkbox.pack(side='left', padx=10)

# Score labels
score_counter_label = tk.Label(
    main_frame,
    text="Wynik całkowity: 0.00/0",
    font=("Arial", 16),
    fg=BG_COLOR,
    bg=ACCENT_COLOR,
    relief="solid",
    bd=2,
    padx=5,
    pady=5
)
score_counter_label.pack(pady=10)

score_label = tk.Label(
    main_frame,
    text="",
    font=("Arial", 20),
    fg=TEXT_COLOR,
    bg=BG_COLOR
)
score_label.pack(pady=5)

correct_answers_label = tk.Label(
    main_frame,
    text="",
    font=("Arial", 16),
    justify="center",
    wraplength=window_width - 60,
    anchor="center",
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
correct_answers_label.pack(pady=5)

# Load questions
questions = load_questions("pytania.txt")

# Initial state - no questions loaded yet
randomized_questions = []

# Start button to open range window
start_button = tk.Button(
    main_frame,
    text="Wybierz zakres pytań i rozpocznij egzamin",
    command=open_range_window,
    font=("Arial", 16),
    padx=20,
    pady=10,
    bg=BUTTON_COLOR,
    fg=TEXT_COLOR,
    relief="raised",
    bd=4,
    activebackground=ACCENT_COLOR,  # Set activebackground
    activeforeground=BG_COLOR  # Set activeforeground
)
start_button.pack(pady=20)

# Usuń istniejący plik problematyczne_pytania.txt przed rozpoczęciem quizu
if os.path.exists("problematyczne_pytania.txt"):
    os.remove("problematyczne_pytania.txt")

root.mainloop()
