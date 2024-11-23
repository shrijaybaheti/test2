import json
import os
import time
import pyautogui
import pyscreenshot as ImageGrab
import pytesseract
import re

# Configure Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

REGION_FILE = "regions.json"
STATE_FILE = "state.json"  # Save macro state for each number
MACRO_FILE = "macros.json"  # Save macros

def get_region(prompt):
    print(f"{prompt}\nMove your cursor to the top-left corner and press Enter.")
    input()
    x1, y1 = pyautogui.position()

    print("Now move your cursor to the bottom-right corner and press Enter.")
    input()
    x2, y2 = pyautogui.position()

    print(f"Region selected: ({x1}, {y1}, {x2}, {y2})\n")
    return (x1, y1, x2, y2)

def save_regions(region1, region2):
    with open(REGION_FILE, "w") as file:
        json.dump({"region1": region1, "region2": region2}, file)
    print(f"Regions saved to {REGION_FILE}.")

def load_regions():
    if os.path.exists(REGION_FILE):
        with open(REGION_FILE, "r") as file:
            regions = json.load(file)
        print(f"Loaded regions from {REGION_FILE}: {regions}")
        return regions["region1"], regions["region2"]
    return None, None

def extract_numbers(text):
    numbers = re.findall(r'\d+', text)
    return int(numbers[0]) if numbers else None

def capture_and_extract_text(region):
    screenshot = ImageGrab.grab(bbox=region)
    text = pytesseract.image_to_string(screenshot)
    return extract_numbers(text.strip())

def adjust_numbers(number1, number2):
    if number1 is None and number2 is not None:
        number1 = number2 - 100
        print(f"Number1 was None, so using adjusted value: {number1}")
    elif number2 is None and number1 is not None:
        number2 = number1 - 100
        print(f"Number2 was None, so using adjusted value: {number2}")
    
    return number1, number2

def ensure_positive(number1, number2):
    number1 = abs(number1) if number1 is not None else None
    number2 = abs(number2) if number2 is not None else None
    
    return number1, number2

def get_macro_input():
    macros = {}
    while True:
        macro_name = input("Enter macro name (e.g., macro_70_1 or 'done' to finish): ").strip()
        if macro_name.lower() == 'done':
            break
        actions = []
        while True:
            action = input(f"Enter action for {macro_name} (click/stop): ").strip().lower()
            if action == 'stop':
                break
            if action == 'click':
                print(f"Please move your mouse to the desired position for {macro_name} click.")
                input("Press Enter when ready to capture the click position...")
                x, y = pyautogui.position()
                actions.append({"action": "click", "x": x, "y": y})
                print(f"Captured click position: ({x}, {y})")
            else:
                print("Invalid action. Please enter 'click' or 'stop'.")
        macros[macro_name] = actions
    return macros

def save_macros(macros):
    with open(MACRO_FILE, "w") as file:
        json.dump(macros, file)
    print(f"Macros saved to {MACRO_FILE}.")

def load_macros():
    if os.path.exists(MACRO_FILE):
        with open(MACRO_FILE, "r") as file:
            macros = json.load(file)
        print(f"Loaded macros from {MACRO_FILE}: {macros}")
        return macros
    return {}

def run_macro(macro_name, macros):
    if macro_name in macros:
        print(f"Running macro: {macro_name}")
        for action in macros[macro_name]:
            if action['action'] == 'click':
                pyautogui.click(action['x'], action['y'])
    else:
        print(f"No macro found with the name: {macro_name}")

def check_for_macro_trigger(number1, number2, triggered_70_1, triggered_70_2, macros):
    if number1 is not None:
        if number1 >= 70 and not triggered_70_1:
            print(f"Number1 is {number1}, greater than or equal to 70, triggering macro...")
            run_macro("macro_70_1", macros)
            triggered_70_1 = True
        elif number1 <= 60 and triggered_70_1:
            print(f"Number1 is {number1}, less than or equal to 60, stopping macro...")
            run_macro("macro_60_1", macros)
            triggered_70_1 = False

    if number2 is not None:
        if number2 >= 70 and not triggered_70_2:
            print(f"Number2 is {number2}, greater than or equal to 70, triggering macro...")
            run_macro("macro_70_2", macros)
            triggered_70_2 = True
        elif number2 <= 60 and triggered_70_2:
            print(f"Number2 is {number2}, less than or equal to 60, stopping macro...")
            run_macro("macro_60_2", macros)
            triggered_70_2 = False

    return triggered_70_1, triggered_70_2


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as file:
            state = json.load(file)
        return state.get("triggered_70_1", False), state.get("triggered_70_2", False)
    return False, False

def save_state(triggered_70_1, triggered_70_2):
    with open(STATE_FILE, "w") as file:
        json.dump({"triggered_70_1": triggered_70_1, "triggered_70_2": triggered_70_2}, file)
    print(f"State saved: triggered_70_1 = {triggered_70_1}")
    print(f"State saved: triggered_70_2 = {triggered_70_2}")

def main():
    region1, region2 = load_regions()

    if region1 is None or region2 is None:
        print("Regions not found. Please define the regions:")
        region1 = get_region("Define the region for the first number")
        region2 = get_region("Define the region for the second number")
        save_regions(region1, region2)

        # Load existing macros
    macros = load_macros()

    # Ask if the user wants to add new macros
    add_macros = input("Do you want to add new macros? (yes/no): ").strip().lower()
    if add_macros == 'yes':
        new_macros = get_macro_input()
        macros.update(new_macros)  # Add new macros to the existing ones
        save_macros(macros)  # Save the updated macros

        
    if not macros:  # If no macros are loaded, prompt user to create them
        print("No macros found. Please define your macros.")
        macros = get_macro_input()
        save_macros(macros)


    triggered_70_1, triggered_70_2 = load_state()

    while True:
        print("\nCapturing numbers...")
        number1 = capture_and_extract_text(region1)
        number2 = capture_and_extract_text(region2)

        number1, number2 = adjust_numbers(number1, number2)
        number1, number2 = ensure_positive(number1, number2)

        print(f"Captured Number1: {number1}")
        print(f"Captured Number2: {number2}")

        triggered_70_1, triggered_70_2 = check_for_macro_trigger(number1, number2, triggered_70_1, triggered_70_2, macros)

        save_state(triggered_70_1, triggered_70_2)

        time.sleep(5)

if __name__ == "__main__":
    main()