import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pynput import keyboard

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--window-size=1920x1080")

# Initialize driver
driver = webdriver.Chrome(options=chrome_options)

# Global flag to track if Shift key was pressed
shift_pressed = False

def on_press(key):
    """Callback for key press events"""
    global shift_pressed
    try:
        if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            shift_pressed = True
            return False  # Stop listener
    except AttributeError:
        pass

def wait_for_shift_key():
    """Wait for user to press Shift key"""
    global shift_pressed
    shift_pressed = False
    
    print("\n" + "="*50)
    print("PRESS SHIFT KEY TO START TYPING")
    print("="*50 + "\n")
    
    # Start listening for keyboard events
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
    
    print("Shift key pressed! Starting typing test...")
    time.sleep(0.5)

def wait_for_test_ready():
    """Wait for the typing test to be fully loaded"""
    try:
        print("Waiting for test to load...")
        # Wait for the test-text div to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "test-text"))
        )
        # Wait for the input box
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "test-input"))
        )
        print("Test content loaded!")
        return True
    except TimeoutException:
        print("Timed out waiting for test to load")
        return False

def get_all_words():
    """Extract all words from the test using the exact structure"""
    try:
        script = """
        var words = [];
        var testText = document.getElementById('test-text');
        
        if (testText) {
            var wordSpans = testText.querySelectorAll('.test-word');
            
            wordSpans.forEach(function(wordSpan) {
                var word = '';
                var charSpans = wordSpan.querySelectorAll('.test-char');
                
                charSpans.forEach(function(charSpan) {
                    word += charSpan.textContent;
                });
                
                if (word.trim()) {
                    words.push(word.trim());
                }
            });
        }
        
        return words;
        """
        words = driver.execute_script(script)
        return words
    except Exception as e:
        print(f"Error extracting words: {e}")
        return []

def get_current_word():
    """Get the current active word that needs to be typed"""
    try:
        script = """
        var testText = document.getElementById('test-text');
        if (!testText) return null;
        
        var wordSpans = testText.querySelectorAll('.test-word');
        
        // Try to find the word that's currently active/incomplete
        for (var i = 0; i < wordSpans.length; i++) {
            var wordSpan = wordSpans[i];
            var classes = wordSpan.className;
            
            // Skip completed/correct words
            if (classes.includes('correct') || 
                classes.includes('complete') || 
                classes.includes('done')) {
                continue;
            }
            
            // This should be the current word
            var word = '';
            var charSpans = wordSpan.querySelectorAll('.test-char');
            charSpans.forEach(function(charSpan) {
                word += charSpan.textContent;
            });
            
            return word.trim();
        }
        
        // Fallback: return first word if no special classes found
        if (wordSpans.length > 0) {
            var word = '';
            var charSpans = wordSpans[0].querySelectorAll('.test-char');
            charSpans.forEach(function(charSpan) {
                word += charSpan.textContent;
            });
            return word.trim();
        }
        
        return null;
        """
        word = driver.execute_script(script)
        return word
    except Exception as e:
        print(f"Error getting current word: {e}")
        return None

def debug_word_states():
    """Debug function to see word states"""
    try:
        script = """
        var testText = document.getElementById('test-text');
        if (!testText) return 'No test-text found';
        
        var wordSpans = testText.querySelectorAll('.test-word');
        var info = [];
        
        for (var i = 0; i < Math.min(5, wordSpans.length); i++) {
            var wordSpan = wordSpans[i];
            var word = '';
            var charSpans = wordSpan.querySelectorAll('.test-char');
            charSpans.forEach(function(charSpan) {
                word += charSpan.textContent;
            });
            
            info.push({
                word: word.trim(),
                classes: wordSpan.className
            });
        }
        
        return info;
        """
        result = driver.execute_script(script)
        return result
    except Exception as e:
        return f"Error: {e}"

def get_input_box():
    """Find the input box"""
    try:
        input_box = driver.find_element(By.ID, "test-input")
        return input_box
    except NoSuchElementException:
        print("Could not find input box")
        return None

def type_character(char, input_box):
    """Type a single character with error handling"""
    try:
        input_box.send_keys(char)
        return True
    except Exception as e:
        # Check if it's an "element not interactable" error - test might have ended
        if "not interactable" in str(e):
            return False
        print(f"\nError typing '{char}': {e}")
        try:
            input_box.send_keys(char)
            return True
        except:
            return False

def is_input_active(input_box):
    """Check if the input box is still active and interactable"""
    try:
        return input_box.is_enabled() and input_box.is_displayed()
    except:
        return False

def get_human_delay(base_wpm=60):
    """
    Get a human-like delay for typing
    base_wpm: target WPM (will vary around this)
    Returns delay in seconds
    """
    # Average word is ~5 characters
    # WPM to chars per second: WPM * 
    chars_per_sec = base_wpm * 10/60
    base_delay = 1 / chars_per_sec
    
    # Add variation: ±20%
    variation = random.uniform(-0.2, 0.2)
    delay = base_delay * (1 + variation)
    
    return delay

def should_make_typo():
    """Decide if we should make a typo (2-3% chance)"""
    return random.random() < 0.025

def get_typo_char(correct_char):
    """Get a nearby key for a typo"""
    # Common typo patterns - nearby keys on QWERTY keyboard
    typo_map = {
        'a': ['s', 'q', 'w', 'z'],
        'b': ['v', 'g', 'h', 'n'],
        'c': ['x', 'd', 'f', 'v'],
        'd': ['s', 'e', 'r', 'f', 'c'],
        'e': ['w', 'r', 'd'],
        'f': ['d', 'r', 't', 'g', 'v'],
        'g': ['f', 't', 'y', 'h', 'b'],
        'h': ['g', 'y', 'u', 'j', 'n'],
        'i': ['u', 'o', 'k'],
        'j': ['h', 'u', 'i', 'k', 'm'],
        'k': ['j', 'i', 'o', 'l'],
        'l': ['k', 'o', 'p'],
        'm': ['n', 'j', 'k'],
        'n': ['b', 'h', 'j', 'm'],
        'o': ['i', 'p', 'l'],
        'p': ['o', 'l'],
        'q': ['w', 'a'],
        'r': ['e', 't', 'f'],
        's': ['a', 'w', 'e', 'd', 'x'],
        't': ['r', 'y', 'g'],
        'u': ['y', 'i', 'j'],
        'v': ['c', 'f', 'g', 'b'],
        'w': ['q', 'e', 's'],
        'x': ['z', 's', 'd', 'c'],
        'y': ['t', 'u', 'h'],
        'z': ['a', 's', 'x']
    }
    
    char_lower = correct_char.lower()
    if char_lower in typo_map and typo_map[char_lower]:
        return random.choice(typo_map[char_lower])
    return 'x'  # Default typo

def type_continuously_dynamic(input_box, duration=65):
    """Type continuously by fetching current word dynamically with human-like variation"""
    start_time = time.time()
    char_count = 0
    word_count = 0
    last_word = None
    consecutive_same = 0
    consecutive_errors = 0
    
    # Variable WPM - will change throughout the test, centered around 50
    current_wpm = random.uniform(48, 52)  # Start at ~50 WPM
    wpm_change_timer = time.time()
    
    print(f"Typing continuously for {duration} seconds with human-like variation...\n")
    print(f"Target WPM: ~50 (range 47-53)\n")
    
    while True:
        elapsed = time.time() - start_time
        
        # Change WPM every 8-15 seconds to create natural speed variation
        if time.time() - wpm_change_timer > random.uniform(8, 15):
            current_wpm = random.uniform(47, 53)  # Centered around 50
            wpm_change_timer = time.time()
            print(f"[{elapsed:.1f}s] Speed variation -> {current_wpm:.0f} WPM")
        
        # Check if time is up
        if elapsed >= duration:
            print(f"\nTime limit of {duration} seconds reached!")
            break
        
        # Check if input is still active (test might have ended)
        if not is_input_active(input_box):
            print(f"\n[{elapsed:.1f}s] Input box is no longer active - test has ended!")
            break
        
        # Get the current word from the page
        current_word = get_current_word()
        
        if not current_word:
            time.sleep(0.2)
            continue
        
        # If it's the same word, wait a bit for page to update
        if current_word == last_word:
            consecutive_same += 1
            if consecutive_same == 5:
                if not is_input_active(input_box):
                    print(f"\n[{elapsed:.1f}s] Input box disabled - test ended!")
                    break
            if consecutive_same > 20:
                if not is_input_active(input_box):
                    print(f"\n[{elapsed:.1f}s] Test has ended!")
                    break
                consecutive_same = 0
            else:
                time.sleep(0.05)
                continue
        
        # Reset counter
        consecutive_same = 0
        
        # Occasionally add a longer thinking pause before a word (5% chance)
        if random.random() < 0.05:
            thinking_pause = random.uniform(0.3, 0.8)
            time.sleep(thinking_pause)
        
        # Type each character in the word
        for i, char in enumerate(current_word):
            # Check if time is up during typing
            if time.time() - start_time >= duration:
                return word_count, char_count
            
            # Check if input is still active
            if not is_input_active(input_box):
                return word_count, char_count
            
            # Decide if we should make a typo
            if should_make_typo() and char.isalpha():
                # Make a typo
                typo_char = get_typo_char(char)
                if type_character(typo_char, input_box):
                    char_count += 1
                    time.sleep(get_human_delay(current_wpm) * 0.7)  # Faster when making mistake
                    
                    # Realize mistake and backspace
                    if type_character(Keys.BACKSPACE, input_box):
                        char_count += 1
                        time.sleep(random.uniform(0.1, 0.2))  # Brief pause after backspace
            
            # Type the correct character
            typed = type_character(char, input_box)
            if typed:
                char_count += 1
                consecutive_errors = 0
                
                # Human-like delay based on current WPM
                delay = get_human_delay(current_wpm)
                time.sleep(delay)
                
                # Occasionally add a micro-pause (finger repositioning)
                if random.random() < 0.08:  # 8% chance
                    time.sleep(random.uniform(0.1, 0.25))
            else:
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    return word_count, char_count
                time.sleep(0.1)
        
        # Check if time is up before adding space
        if time.time() - start_time >= duration:
            break
        
        # Check if input is still active before space
        if not is_input_active(input_box):
            break
            
        # Add space after word
        typed = type_character(' ', input_box)
        if typed:
            char_count += 1
            word_count += 1
            consecutive_errors = 0
        else:
            consecutive_errors += 1
            if consecutive_errors >= 3:
                break
        
        # Small delay after space
        time.sleep(get_human_delay(current_wpm) * 1.2)
        
        # Remember this word
        last_word = current_word
        
        # Print progress every 15 words
        if word_count % 15 == 0 and word_count > 0:
            elapsed = time.time() - start_time
            actual_wpm = (word_count / elapsed) * 60
            print(f"[{elapsed:.1f}s] {word_count} words | {actual_wpm:.1f} WPM")
    
    return word_count, char_count

def debug_page_structure():
    """Debug function to see what elements are on the page"""
    try:
        # Check for test-text div
        test_text = driver.find_element(By.ID, "test-text")
        print(f"\nFound test-text div")
        print(f"  HTML preview: {test_text.get_attribute('outerHTML')[:300]}")
        
        # Count word spans
        word_spans = driver.find_elements(By.CLASS_NAME, "test-word")
        print(f"\nFound {len(word_spans)} test-word spans")
        
        # Show first few words
        for i, word_span in enumerate(word_spans[:5]):
            chars = word_span.find_elements(By.CLASS_NAME, "test-char")
            word = ''.join([char.text for char in chars])
            print(f"  Word {i+1}: '{word}'")
            
    except Exception as e:
        print(f"Debug error: {e}")

def main():
    url = "https://typetest.io/"
    driver.get(url)
    
    print("Page loaded. Waiting for test content...")
    
    # Wait for test to be ready
    if not wait_for_test_ready():
        print("Failed to load test")
        driver.quit()
        return
    
    time.sleep(2)  # Extra time for any animations
    
    # Debug: Check page structure
    print("\n=== DEBUGGING PAGE STRUCTURE ===")
    debug_page_structure()
    print("=== END DEBUG ===\n")
    
    # Get all the words to type
    print("Extracting words from page...")
    words_list = get_all_words()
    
    if not words_list:
        print("Could not extract words from page")
        driver.quit()
        return
    
    print(f"\nFound {len(words_list)} words to type")
    print(f"First 10 words: {' '.join(words_list[:10])}")
    
    # Get input box
    input_box = get_input_box()
    if not input_box:
        print("Could not find input box")
        driver.quit()
        return
    
    print("\nInput box found. Test is ready!")
    
    # Wait for user to press Shift key before starting
    wait_for_shift_key()
    
    # Click input box to focus it
    print("Focusing input box...")
    input_box.click()
    time.sleep(1)
    
    # Debug: Check word states before starting
    print("\n=== WORD STATES CHECK ===")
    word_states = debug_word_states()
    print(f"First 5 words and their states:")
    if isinstance(word_states, list):
        for i, state in enumerate(word_states):
            print(f"  {i+1}. '{state['word']}' - classes: {state['classes']}")
    else:
        print(f"  {word_states}")
    print("=== END CHECK ===\n")
    
    # Start typing
    print("\nStarting to type...\n")
    print("="*50)
    start_time = time.time()
    
    # Type continuously for 65 seconds, fetching words dynamically
    try:
        word_count, char_count = type_continuously_dynamic(input_box, duration=65)
    except Exception as e:
        print(f"\nError during typing: {e}")
        import traceback
        traceback.print_exc()
        elapsed = time.time() - start_time
        print(f"Stopped after {elapsed:.2f} seconds")
        word_count, char_count = 0, 0
    
    elapsed = time.time() - start_time
    print("="*50)
    print(f"\nFinished typing!")
    print(f"Duration: {elapsed:.2f} seconds")
    print(f"Words typed: {word_count}")
    print(f"Characters typed: {char_count}")
    if elapsed > 0:
        print(f"Average WPM: {(word_count / elapsed * 60):.1f}")
    
    print("\n" + "="*50)
    print("TEST COMPLETED!")
    print("Window will remain open until you press Ctrl+C")
    print("Take your screenshot or review results!")
    print("="*50 + "\n")
    
    # Keep window open indefinitely until user closes it
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nClosing browser...")
        driver.quit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        driver.quit()
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        driver.quit()