# Kahoot Bot

![GitHub license](https://img.shields.io/github/license/your-username/your-repo)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)

A Python bot for automating Kahoot game participation and answering questions. This bot uses Selenium for web interaction and a HuggingFace GPT-2 model for answering questions.

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

- Python 3.8 or higher
- Chrome WebDriver (ChromeDriver)
- [Selenium](https://pypi.org/project/selenium/)
- [HuggingFace Inference API](https://huggingface.co/api/)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

You may need to install the required Python packages using `pip`:

```bash
pip install selenium huggingface-hub bs4
```
### Installation
Clone the repository to your local machine:
```bash
git clone https://github.com/your-username/your-repo.git
```
Download the Chrome WebDriver and make sure it's in your system's PATH.
Create a configuration.json file in the project directory with the following format:
```json
{
    "MODEL_API_TOKEN": "YOUR_HUGGINGFACE_TOKEN",
    "NICKNAME": "YourKahootNickname"
}
```
Replace "YOUR_HUGGINGFACE_TOKEN" with your HuggingFace Inference API token and "YourKahootNickname" with your desired Kahoot nickname.

## Usage

To start the Kahoot bot, run the following command:

```bash
python kahoot_bot.py --nickname YourBotNickname
```
Replace "YourBotNickname" with the nickname you want your bot to use. If you don't specify a nickname, it will use the default nickname provided in configuration.json.

### Customizing Your Bot
You can customize your bot by modifying the configuration.json file and adjusting the bot's behavior in the kahoot_bot.py script. Feel free to explore and modify the code to suit your requirements.

### Contributing
Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue on the GitHub repository. If you'd like to contribute code, please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

This project uses Selenium for web automation.
It also utilizes the HuggingFace Hub for machine learning capabilities.
Thanks to the open-source community for their valuable contributions.


