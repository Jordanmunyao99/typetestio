# TypeTest.io Automation Script

A Python-based automation script for [TypeTest.io](https://typetest.io/) that simulates realistic human typing patterns with customizable speed, natural variations, and occasional typos.

## Features

- 🎯 **Realistic Human Typing**: Mimics natural typing patterns with speed variations
- ⚡ **Adjustable WPM**: Configured to type at ~50 WPM (range: 47-53)
- 🔄 **Speed Variations**: Naturally varies typing speed every 8-15 seconds
- ❌ **Simulated Typos**: 2.5% chance of typos with automatic backspace correction
- ⏸️ **Human-like Pauses**: Random thinking pauses and micro-pauses during typing
- 🕐 **Flexible Duration**: Easily configurable test duration (1min, 2min, 5min, etc.)
- 🛑 **Smart Test Detection**: Automatically detects when the test ends
- 📊 **Progress Tracking**: Real-time WPM and progress updates

## Prerequisites

- Python 3.7+
- Chrome browser
- ChromeDriver (compatible with your Chrome version)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Jordanmunyao99/typetestio
cd typetestio
```

2. Install required Python packages:
```bash
pip install selenium pynput
```

3. Download ChromeDriver:
   - Visit [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
   - Download the version matching your Chrome browser
   - Add ChromeDriver to your system PATH

## Usage

1. Run the script:
```bash
python test.py
```

2. The script will:
   - Open TypeTest.io in Chrome
   - Wait for the test to load
   - Show debug information about the page

3. **Press SHIFT** when you're ready to start the automated typing

4. Watch the script complete the test with human-like typing

5. **Press Ctrl+C** when you want to close the browser

## Configuration

### Changing Test Duration

Edit the `TEST_DURATION` variable in the `main()` function (around line 520):

```python
TEST_DURATION = 65   # For 1 minute test
TEST_DURATION = 125  # For 2 minute test  
TEST_DURATION = 305  # For 5 minute test (default)
TEST_DURATION = 605  # For 10 minute test
```

### Adjusting Typing Speed

Modify the WPM range in the `type_continuously_dynamic()` function:

```python
# Current: ~50 WPM (range 47-53)
current_wpm = random.uniform(47, 53)

# For faster typing: ~70 WPM
current_wpm = random.uniform(65, 75)

# For slower typing: ~30 WPM
current_wpm = random.uniform(27, 33)
```

### Adjusting Typo Frequency

Change the typo chance in the `should_make_typo()` function:

```python
# Current: 2.5% chance
return random.random() < 0.025

# For more typos: 5% chance
return random.random() < 0.05

# For fewer typos: 1% chance
return random.random() < 0.01
```

## How It Works

1. **Dynamic Word Fetching**: Continuously fetches the current word from the page using JavaScript
2. **Character-by-Character Typing**: Types each character with variable delays based on target WPM
3. **Typo Simulation**: Randomly types nearby keys (based on QWERTY layout) then backspaces
4. **Speed Variation**: Changes target WPM every 8-15 seconds for natural fluctuation
5. **Test End Detection**: Monitors input box status and stops when test completes

## Output Example

```
Typing continuously for 305 seconds with human-like variation...
Target WPM: ~50 (range 47-53)

[8.3s] Speed variation -> 51 WPM
[15.2s] 15 words | 49.3 WPM
[22.7s] Speed variation -> 48 WPM
[30.5s] 30 words | 50.1 WPM
...
[300.2s] Input box is no longer active - test has ended!

Finished typing!
Duration: 300.21 seconds
Words typed: 250
Characters typed: 1275
Average WPM: 50.0
```

## Troubleshooting

### ChromeDriver Issues
- Ensure ChromeDriver version matches your Chrome browser version
- Add ChromeDriver to system PATH or place in script directory

### Script Stops Early
- The script automatically detects test end
- Check if the test duration on TypeTest.io matches your configuration

### Typing Errors
- If you see "element not interactable" errors, the test may have ended
- This is normal behavior when the 60s/5min timer expires

### Import Errors
```bash
# If pynput fails to install
pip install --upgrade pip
pip install pynput

# If selenium fails
pip install --upgrade selenium
```

## Customization Ideas

- **Different typing patterns**: Modify delay calculations in `get_human_delay()`
- **Custom typo maps**: Edit the `typo_map` dictionary in `get_typo_char()`
- **Pause patterns**: Adjust pause frequencies and durations
- **Multiple test runs**: Wrap `main()` in a loop with delays between runs

## Legal & Ethical Notice

⚠️ **This script is for educational purposes only.**

- Use responsibly and in accordance with TypeTest.io's terms of service
- Automated testing may violate some websites' policies
- Consider the ethical implications of automation
- Results from automated tests should not be represented as genuine human performance

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using [Selenium WebDriver](https://www.selenium.dev/)
- Keyboard simulation powered by [pynput](https://pynput.readthedocs.io/)
- Designed for [TypeTest.io](https://typetest.io/)

## Disclaimer

This tool is not affiliated with, endorsed by, or connected to TypeTest.io. Use at your own risk.
