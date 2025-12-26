import streamlit as st
import re

st.set_page_config(
    page_title="Python Code Generator",)

st.title("Python Code Generator")
st.write(
    "Enter a simple natural language instruction and this app will generate the corresponding Python code."
)

instruction = st.text_input("Enter what you want your python code to do:")


"""Normalize user input for simpler pattern matching.

    - Trims surrounding whitespace.
    - Converts to lowercase so keyword checks are case-insensitive.
"""
def preprocess_text(text):
    return text.strip().lower()


def extract_numbers(text):
    """Find integers in the text and return them as a list of ints.

    Uses a simple regex, so it only captures contiguous digits (no
    negative numbers, no spelled-out numbers like "five").
    """
    return list(map(int, re.findall(r"\d+", text)))


def detect_task(text):
    """Heuristic task detection based on keywords.

    Returns one of the task identifiers used by `generate_code`.
    This is intentionally simple and rule-based; it looks for words
    like "sum", "factorial", "fibonacci", "print" and qualifiers
    like "even"/"odd".
    """
    # Check for sum/add requests, with even/odd qualifiers
    if "sum" in text or "add" in text:
        if "even" in text:
            return "sum_even"
        elif "odd" in text:
            return "sum_odd"
        else:
            return "sum"

    # Common algorithmic requests
    elif "factorial" in text:
        return "factorial"
    elif "fibonacci" in text:
        return "fibonacci"

    # Printing ranges of numbers (even/odd/any)
    elif ("print" in text or "display" in text) and "numbers" in text:
        if "even" in text:
            return "print_even"
        elif "odd" in text:
            return "print_odd"
        else:
            return "print_numbers"

    # Printing arbitrary text messages
    elif ("print" in text or "display" in text) and "text" in text:
        return "print_text"

    # Fallback for unsupported instructions
    else:
        return "not_supported"
    
def generate_code(task, numbers, text):
    if task == "sum" and len(numbers) == 2:
        # Sum all integers in the inclusive range [start, end].
        return f"""for i in range({numbers[0]}, {numbers[1]} + 1):
        total += i
        print("Sum of numbers from {numbers[0]} to {numbers[1]} is:", total)"""

    elif task == "sum_even" and len(numbers) == 2:
        # Ensure the start is even, then step by 2 to sum even numbers.
        if numbers[0] % 2 != 0:
            numbers[0] += 1
        return f"""for i in range({numbers[0]}, {numbers[1]} + 1, 2):
        total += i
        print("Sum of even numbers from {numbers[0]} to {numbers[1]} is:", total)"""

    elif task == "sum_odd" and len(numbers) == 2:
        # Make start odd if needed, then step by 2 to hit odd numbers.
        if numbers[0] % 2 == 0:
            numbers[0] += 1
        return f"""for i in range({numbers[0]}, {numbers[1]} + 1, 2):
        total += i
        print("Sum of odd numbers from {numbers[0]} to {numbers[1]} is:", total)"""

    elif task == "factorial" and len(numbers) == 1:
        return f"""result = 1
for i in range(1, {numbers[0]} + 1):
    result *= i
print("Factorial of {numbers[0]} is:", result)"""
        
    elif task == "fibonacci" and len(numbers) == 1:
        return f"""a, b = 0, 1
for _ in range({numbers[0]}):
    print(a, end=' ')
    a, b = b, a + b""" 

    elif task == "print_even" and len(numbers) == 2:
        # Print even numbers in the inclusive range.
        if numbers[0] % 2 != 0:
            numbers[0] += 1
        return f"""for i in range({numbers[0]}, {numbers[1]} + 1, 2):
        print(i, end=' ')"""

    elif task == "print_odd" and len(numbers) == 2:
        # Print odd numbers in the inclusive range.
        if numbers[0] % 2 == 0:
            numbers[0] += 1
        return f"""for i in range({numbers[0]}, {numbers[1]} + 1, 2):
        print(i, end=' ')"""

    elif task == "print_numbers" and len(numbers) == 2:
        # Print every number in the inclusive range.
        return f"""for i in range({numbers[0]}, {numbers[1]} + 1):
        print(i, end=' ')"""

    elif task == "print_text":
        # Try to extract the message to print by removing common words.
        message = text.replace("print", "").strip()
        message = message.replace("display", "").strip()
        message = message.replace("text", "").strip().strip('"').strip("'")
        return f"""print("{message}")"""

    else:
        return "# Task not supported or insufficient parameters."


if st.button("Generate Python Code"):
    # Validate and preprocess the user's instruction, then route it
    # through the simple detector + generator pipeline above.
    if instruction.strip() == "":
        st.warning("Please enter a valid instruction.")
    else:
        text = preprocess_text(instruction)
        task = detect_task(text)
        numbers = extract_numbers(text)

        code = generate_code(task, numbers, text)

        st.subheader("Generated Python Code:")
        st.code(code, language="python")