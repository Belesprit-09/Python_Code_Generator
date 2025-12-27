import streamlit as st
import numpy as np
import tensorflow as tf
import re
import os

# Suppress TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from sklearn.preprocessing import LabelEncoder

# --- 1. THE AI CLASS (Cached for Performance) ---
@st.cache_resource
class LogicCodeGenerator:
    def __init__(self):
        # EXPANDED DATASET: Logic + Printing Text
        # 1. AUGMENTED DATASET (Optimized for High Confidence)
        self.data = [
            # --- INTENT: PRINT TEXT ---
            ("print Hello World", "print_text"),
            ("display Welcome to Python", "print_text"),
            ("show message System Failure", "print_text"),
            ("print the string Good Morning", "print_text"),
            ("output the text Analysis Complete", "print_text"),
            ("log the message Error Found", "print_text"),
            ("write text Hello User", "print_text"),
            ("echo the string Process Started", "print_text"),
            ("show text Task Finished", "print_text"),

            # --- INTENT: PRINT RANGE (Simple Loop) ---
            ("print numbers from 1 to 10", "print_range"),
            ("show values between 5 and 20", "print_range"),
            ("display numbers 100 to 200", "print_range"),
            ("list integers from 1 to 50", "print_range"),
            ("count from 10 to 20", "print_range"),
            ("iterate numbers between 5 and 15", "print_range"),
            ("write values from 1 to 100", "print_range"),
            ("output numbers 50 to 60", "print_range"),

            # --- INTENT: PRINT EVEN NUMBERS ---
            ("display even numbers between 100 to 200", "print_even"),
            ("print even numbers from 10 to 20", "print_even"),
            ("show only even values from 1 to 50", "print_even"),
            ("list all even numbers between 5 and 15", "print_even"),
            ("output even integers from 20 to 40", "print_even"),
            ("get even numbers from 1 to 100", "print_even"),

            # --- INTENT: PRINT ODD NUMBERS ---
            ("display odd numbers between 1 to 50", "print_odd"),
            ("print odd numbers from 21 to 55", "print_odd"),
            ("show only odd values from 10 to 30", "print_odd"),
            ("list all odd numbers between 5 and 25", "print_odd"),
            ("output odd integers from 1 to 20", "print_odd"),
            ("get odd numbers from 50 to 100", "print_odd"),

            # --- INTENT: SUM ALL (Math) ---
            ("sum of numbers from 1 to 10", "sum_all"),
            ("calculate sum between 10 and 50", "sum_all"),
            ("add all numbers from 5 to 15", "sum_all"),
            ("total of values from 1 to 100", "sum_all"),
            ("find the summation of 10 to 20", "sum_all"),
            ("add up numbers between 1 and 5", "sum_all"),
            ("get the total sum from 50 to 60", "sum_all"),
            ("compute sum of 1 to 10", "sum_all"),

            # --- INTENT: SUM EVEN (Math + Logic) ---
            ("sum of even numbers from 1 to 10", "sum_even"),
            ("calculate sum of evens from 50 to 100", "sum_even"),
            ("add up even values between 10 and 20", "sum_even"),
            ("total of even numbers from 1 to 50", "sum_even"),
            ("find sum of evens between 5 and 15", "sum_even"),
            ("compute total of even integers 10 to 30", "sum_even"),

            # --- INTENT: SUM ODD (Math + Logic) ---
            ("sum of odd numbers from 1 to 10", "sum_odd"),
            ("add odd values between 10 and 20", "sum_odd"),
            ("calculate sum of odds from 5 to 15", "sum_odd"),
            ("total of odd numbers from 1 to 100", "sum_odd"),
            ("find sum of odds between 20 and 40", "sum_odd"),
            ("add up all odd integers 1 to 50", "sum_odd"),
            
            # CONDITIONAL LOGIC (Even/Odd)
            ("sum of even numbers from 1 to 10", "sum_even"),
            ("calculate sum of evens from 50 to 100", "sum_even"),
            ("sum of odd numbers from 1 to 10", "sum_odd"),
            ("add odd values between 10 and 20", "sum_odd"),
        ]
        # Training Pipeline
        sentences = [item[0] for item in self.data]
        labels = [item[1] for item in self.data]

        self.tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words=200, oov_token="<OOV>")
        self.tokenizer.fit_on_texts(sentences)
        sequences = self.tokenizer.texts_to_sequences(sentences)
        
        self.max_length = 15
        padded_sequences = tf.keras.preprocessing.sequence.pad_sequences(sequences, maxlen=self.max_length, padding='post')

        self.label_encoder = LabelEncoder()
        training_labels = self.label_encoder.fit_transform(labels)

        self.model = tf.keras.Sequential([
            tf.keras.layers.Embedding(input_dim=200, output_dim=32, input_length=self.max_length),
            tf.keras.layers.GlobalAveragePooling1D(),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dense(len(set(labels)), activation='softmax')
        ])

        self.model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.model.fit(padded_sequences, np.array(training_labels), epochs=250, verbose=0)

    def extract_params(self, text):
        return [int(n) for n in re.findall(r'\d+', text)]

    def extract_message(self, text):
        # Helper to extract text inside quotes or after keywords like "print"
        # 1. Try to find content inside quotes
        match = re.search(r'["\'](.*?)["\']', text)
        if match: return match.group(1)
        
        # 2. Fallback: Take everything after "print" or "display"
        words = text.split()
        if "print" in words: 
            return " ".join(words[words.index("print")+1:])
        if "display" in words:
            return " ".join(words[words.index("display")+1:])
        return "Hello World"

    def generate(self, user_input):
        seq = self.tokenizer.texts_to_sequences([user_input])
        padded = tf.keras.preprocessing.sequence.pad_sequences(seq, maxlen=self.max_length, padding='post')
        prediction = self.model.predict(padded, verbose=0)
        confidence = np.max(prediction)
        class_index = np.argmax(prediction)
        intent = self.label_encoder.inverse_transform([class_index])[0]
        
        numbers = self.extract_params(user_input)
        start = numbers[0] if len(numbers) > 0 else 1
        end = numbers[1] if len(numbers) > 1 else 10


        # --- LOGIC MAPPING ---
        if intent == "print_text":
            msg = self.extract_message(user_input)
            return f"print('{msg}')", intent, confidence

        elif intent == "print_range":
            return f"for i in range({start}, {end} + 1):\n    print(i)", intent, confidence

        elif intent == "sum_all":
            return f"total = 0\nfor i in range({start}, {end} + 1):\n    total += i\nprint(total)", intent, confidence

        elif intent == "sum_even":
            return (f"total = 0\n"
                    f"for i in range({start}, {end} + 1):\n"
                    f"    if i % 2 == 0:\n"
                    f"        total += i\n"
                    f"print(total)"), intent, confidence

        elif intent == "sum_odd":
            return (f"total = 0\n"
                    f"for i in range({start}, {end} + 1):\n"
                    f"    if i % 2 != 0:\n"
                    f"        total += i\n"
                    f"print(total)"), intent, confidence
            
        elif intent == "print_even":
        # Print even numbers in the inclusive range.
            if start % 2 != 0:
                start += 1
            return (f"for i in range({start}, {end} + 1, 2):\n"
                    f"    print(i, end=' ')"), intent, confidence

        elif intent == "print_odd":
            # Print odd numbers in the inclusive range.
            if start % 2 == 0:
                start += 1
            return (f"for i in range({start}, {end} + 1, 2):\n"
                    f"    print(i, end=' ')"), intent, confidence

        else: 
            return "# Error: Unknown intent", intent, confidence

# --- 2. STREAMLIT UI SETUP ---
st.set_page_config(page_title="AI Code Gen")

st.title("Python Code Generator")
st.markdown("Enter a natural language command, and the Neural Network will generate the Python code for you.")

# Sidebar for details
# with st.sidebar:
#     st.header("About the Model")
#     st.info("This app uses a TensorFlow Neural Network with Embedding layers to classify intent.")
#     st.markdown("**Supported Commands:**")
#     st.markdown("- Print text (e.g., 'print Hello World')")
#     st.markdown("- Loops (e.g., 'print numbers 1 to 10')")
#     st.markdown("- Logic (e.g., 'sum of even numbers 10 to 50')")

# Initialize Model (Only runs once!)
with st.spinner("Initializing AI Brain..."):
    bot = LogicCodeGenerator()

# Input Area
user_input = st.text_input("Enter your instruction:", placeholder="e.g., calculate sum of odd numbers between 1 and 20")

if st.button("Generate Code"):
    if user_input:
        code, intent, conf = bot.generate(user_input)
        
        # Display Results
        st.subheader("Generated Python Code:")
        st.code(code, language='python')
        
        # Debugging Info (Impressive for Interviewers)
                
        with st.expander("See Internal Model Details"):
            st.write(f"**Predicted Intent:** `{intent}`")
            st.write(f"**Model Confidence:** `{conf*100:.2f}%`")
            if conf > 0.8:
                st.success("The model is highly confident in this result.")
            elif conf > 0.6:
                st.warning("The model is somewhat confident.")
            else:
                st.error("The model is unsure.")
            
    else:
        st.warning("Please enter an instruction first.")